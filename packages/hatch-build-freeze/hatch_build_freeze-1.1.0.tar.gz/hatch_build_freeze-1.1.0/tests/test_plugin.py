# Copyright 2025 Minds.ai, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Tests for Hatch build freeze plugin."""

import os
import subprocess
import tarfile
import zipfile
from email import message_from_bytes
from pathlib import Path
from sys import path as syspath
from types import SimpleNamespace

import pytest
import tomlkit

from hatch_build_freeze import plugin


def _format_toml_value(value: list[str] | str | bool) -> str:
    """Formats a value for TOML representation."""
    if isinstance(value, list):
        return (
            "["
            + ", ".join(f'"{item}"' if isinstance(item, str) else str(item) for item in value)
            + "]"
        )
    if isinstance(value, str):
        return f'"{value}"'
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


@pytest.fixture(name="mock_uv_project")
def base_project_structure(tmp_path: Path, request) -> Path:
    """Creates a basic project structure within a temporary directory.

    Includes a pyproject.toml and a simple src layout.
    """
    project_dir = tmp_path / "my_test_package"
    project_dir.mkdir()
    hook_dir = Path(__file__).resolve().parent.parent
    hatch_build_freeze_dep = f"hatch-build-freeze @ {hook_dir.as_uri()}"
    hatch_freeze_config = getattr(request, "param", {})

    hatch_freeze_options_str = ""
    if hatch_freeze_config:  # Only add options if config is provided
        options = []
        for key, value in hatch_freeze_config.items():
            options.append(f"{key} = {_format_toml_value(value)}")
        hatch_freeze_options_str = "\n".join(options)
    pyproject_content = f"""
[build-system]
requires = ["hatchling~=1.27.0", "{hatch_build_freeze_dep}"]
build-backend = "hatchling.build"

[tool.hatch.build.hooks.hatch-build-freeze]
{hatch_freeze_options_str}

[project]
name = "my_test_package"
version = "0.1.0"
requires-python = ">=3.10"

dependencies = [
    "tqdm<=4.67.1",
]

[project.optional-dependencies]
e1 = ["psutil==6.1.1",]

[dependency-groups]
g1 = ["click==8.2.1",]
"""
    (project_dir / "pyproject.toml").write_text(pyproject_content.strip() + "\n")
    src_dir = project_dir / "my_test_package"
    src_dir.mkdir(parents=True)
    (src_dir / "__init__.py").write_text("__version__ = '0.1.0'")
    (src_dir / "main.py").write_text("def hello(): print('hello')")
    return project_dir


def returns_pyproject_data_and_lock(mock_uv_project: Path) -> tuple[dict, str | None]:
    """Returns the TOML data and the prerelease argument if it exists."""
    toml_data = tomlkit.loads((mock_uv_project / "pyproject.toml").read_text())
    freeze_config = toml_data["tool"]["hatch"]["build"]["hooks"]["hatch-build-freeze"]
    prerelease_arg = next(
        (arg for arg in freeze_config.get("uv-args", []) if arg.startswith("--prerelease")),
        None,
    )
    if prerelease_arg:
        subprocess.check_output(["uv", "lock", prerelease_arg], cwd=mock_uv_project)
    else:
        subprocess.check_output(["uv", "lock"], cwd=mock_uv_project)
    return toml_data, prerelease_arg


@pytest.mark.parametrize(
    "mock_uv_project",
    [
        pytest.param({"groups": ["g1"], "extras": ["e1"]}, id="with_groups_and_extras"),
        pytest.param({"groups": ["g1"]}, id="with_groups"),
        pytest.param({"extras": ["e1"]}, id="with_extras"),
        pytest.param({"groups": []}, id="empty_groups"),
        pytest.param(
            {"groups": ["g1"], "extras": ["e1"], "uv-args": ["--prerelease=allow"]},
            id="with_groups_and_extras_prerelease",
        ),
        pytest.param(
            {"groups": ["g1"], "uv-args": ["--prerelease=allow"]}, id="with_groups_prerelease"
        ),
        pytest.param(
            {"extras": ["e1"], "uv-args": ["--prerelease=allow"]}, id="with_extras_prerelease"
        ),
        pytest.param(
            {"groups": [], "uv-args": ["--prerelease=allow"]}, id="empty_groups_prerelease"
        ),
    ],
    indirect=True,
)
def test_build_hook(mock_uv_project: Path, request) -> None:
    """Tests the standalone implementation of the build hook."""
    syspath.insert(0, str(mock_uv_project))
    toml_data, prerelease_arg = returns_pyproject_data_and_lock(mock_uv_project)
    hook = plugin.HatchBuildFreezePlugin(
        mock_uv_project,
        toml_data["tool"]["hatch"]["build"]["hooks"]["hatch-build-freeze"],
        {},
        SimpleNamespace(name="hatch_build_freeze"),
        mock_uv_project,
        "wheel",
    )
    pyproject_file = mock_uv_project / "pyproject.toml"
    assert pyproject_file.exists()

    # pylint: disable=protected-access
    assert hook._generate_requirements_file()
    dependencies = hook._parse_requirements_file(hook.requirements_file_path)
    expected_dependencies = [
        "colorama==0.4.6 ; sys_platform == 'win32'",
        "tqdm==4.67.1",
    ]
    if request.node.callspec.id in ("with_groups_and_extras", "with_groups_and_extras_prerelease"):
        expected_dependencies.extend(["click==8.2.1", "psutil==6.1.1"])
    elif request.node.callspec.id in ("with_groups", "with_groups_prerelease"):
        expected_dependencies.append("click==8.2.1")
    elif request.node.callspec.id in ("with_extras", "with_extras_prerelease"):
        expected_dependencies.append("psutil==6.1.1")

    assert set(dependencies) == set(expected_dependencies)
    assert not hook.uv_args if not prerelease_arg else hook.uv_args == ["--prerelease=allow"]
    assert hook.requirements_file_path.exists()
    version = "0.1.0"
    hook.initialize(version, {})
    hook.finalize(version, {}, "")
    assert not hook.requirements_file_path.exists()


def verify_dependencies(pkg_data_bytes: bytes, test_type: str) -> None:
    """Verifies the dependencies in the package data."""
    data = message_from_bytes(pkg_data_bytes)
    dependencies = set(data.get_all("Requires-Dist"))
    expected_dependencies = {
        "tqdm<=4.67.1",
        "colorama==0.4.6 ; sys_platform == 'win32'",
        "tqdm==4.67.1",
        "psutil==6.1.1; extra == 'e1'",
    }
    if test_type in ("with_groups_and_extras", "with_groups_and_extras_prerelease"):
        expected_dependencies.update({"click==8.2.1", "psutil==6.1.1"})
    elif test_type in ("with_groups", "with_groups_prerelease"):
        expected_dependencies.add("click==8.2.1")
    elif test_type in ("with_extras", "with_extras_prerelease"):
        expected_dependencies.add("psutil==6.1.1")
    elif "dont-freeze" in test_type:
        expected_dependencies = {
            "tqdm<=4.67.1",
            "psutil==6.1.1; extra == 'e1'",
        }
    assert dependencies == expected_dependencies


@pytest.mark.parametrize(
    "mock_uv_project",
    [
        pytest.param({"groups": ["g1"], "extras": ["e1"]}, id="with_groups_and_extras"),
        pytest.param({"groups": ["g1"]}, id="with_groups"),
        pytest.param({"extras": ["e1"]}, id="with_extras"),
        pytest.param({"groups": []}, id="empty_groups"),
        pytest.param(
            {"groups": ["g1"], "extras": ["e1"], "uv-args": ["--prerelease=allow"]},
            id="with_groups_and_extras_prerelease",
        ),
        pytest.param(
            {"groups": ["g1"], "uv-args": ["--prerelease=allow"]}, id="with_groups_prerelease"
        ),
        pytest.param(
            {"extras": ["e1"], "uv-args": ["--prerelease=allow"]}, id="with_extras_prerelease"
        ),
        pytest.param(
            {"groups": [], "uv-args": ["--prerelease=allow"]}, id="empty_groups_prerelease"
        ),
        pytest.param({"groups": ["g1"], "extras": ["e1"]}, id="dont-freeze-with-groups-and-extras"),
        pytest.param({"groups": ["g1"]}, id="dont-freeze-with-groups"),
        pytest.param({"extras": ["e1"]}, id="dont-freeze-with-extras"),
        pytest.param({"groups": []}, id="dont-freeze"),
    ],
    indirect=True,
)
def test_build(mock_uv_project: Path, request) -> None:
    """Tests the build process on a sample project with the plugin."""
    syspath.insert(0, str(mock_uv_project))
    env = os.environ.copy()
    if "dont-freeze" in request.node.callspec.id:
        env["HATCH_BUILD_FREEZE_DISABLED"] = "1"
    else:
        env["HATCH_BUILD_FREEZE_DISABLED"] = "0"
    returns_pyproject_data_and_lock(mock_uv_project)
    subprocess.check_output(["hatch", "-v", "build"], cwd=mock_uv_project, env=env)
    wheel_path = mock_uv_project / "dist" / "my_test_package-0.1.0-py3-none-any.whl"
    sdist_path = mock_uv_project / "dist" / "my_test_package-0.1.0.tar.gz"
    assert wheel_path.exists()
    assert sdist_path.exists()

    assert not (mock_uv_project / "requirements.txt").exists()

    # Verify PKG-INFO in the sdist file
    with tarfile.open(sdist_path, "r") as tar_in:
        for member in tar_in.getmembers():
            if member.name.endswith("PKG-INFO"):
                pkg_info_content = tar_in.extractfile(member).read()
                break
    verify_dependencies(pkg_info_content, request.node.callspec.id)

    # Verify METADATA in the wheel file
    metadata_bytes = None
    with zipfile.ZipFile(wheel_path, "r") as zip_in:
        metadata_bytes = zip_in.read("my_test_package-0.1.0.dist-info/METADATA")
    verify_dependencies(metadata_bytes, request.node.callspec.id)
