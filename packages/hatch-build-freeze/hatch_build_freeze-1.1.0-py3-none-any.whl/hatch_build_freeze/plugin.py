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
"""Plugin to generate a requirements.txt file using 'uv export' and include it in the build."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Any

import tomlkit
from hatchling.builders.hooks.plugin.interface import BuildHookInterface

from hatch_build_freeze.logger import setup_logger

if TYPE_CHECKING:
    from hatchling.bridge.app import Application
    from hatchling.builders.config import BuilderConfigBound
    from hatchling.metadata.core import ProjectMetadata


class HatchBuildFreezePlugin(BuildHookInterface):
    """A build hook to freeze the dependency tree for a Python package."""

    PLUGIN_NAME = "hatch-build-freeze"

    def __init__(
        self,
        root: Path,
        config: dict[str, Any],
        build_config: BuilderConfigBound,
        metadata: ProjectMetadata,
        directory: Path,
        target_name: str,
        app: Application | None = None,
    ):
        # pylint: disable=too-many-arguments
        super().__init__(
            str(root), config, build_config, metadata, str(directory), target_name, app
        )
        file_name = self.config.get("file", "requirements.txt")
        self.requirements_file_path = Path(self.root) / file_name
        self._uv_command: list[str] = []
        self.logger = setup_logger(self.config.get("log-level", "info"))

    @property
    def uv_args(self) -> list[str]:
        """Returns the user provided arguments for the 'uv' command."""
        return self.config.get("uv-args", [])

    @property
    def groups(self) -> list[str]:
        """Returns the user provided dependency groups to include for package dependencies."""
        return self.config.get("groups", [])

    @property
    def extras(self) -> list[str]:
        """Returns the user provided optional dependencies to include for package dependencies."""
        return self.config.get("extras", [])

    def _generate_requirements_file(self) -> bool:
        """Generates the requirements file using 'uv export'."""
        self.logger.info(
            "Attempting to generate '%s' using uv...", self.requirements_file_path.name
        )
        pyproject_path = Path(self.root) / "pyproject.toml"
        if not pyproject_path.exists():
            self.logger.error("'%s' not found. Cannot generate requirements.", pyproject_path)
            return False
        package_name = tomlkit.loads(pyproject_path.read_text(encoding="utf-8"))["project"]["name"]
        command = [
            "uv",
            "export",
            "--locked",
            "--format=requirements.txt",
            "--output-file",
            str(self.requirements_file_path),
            "--no-editable",
            "--no-emit-package",
            package_name,
            "--no-emit-project",
            "--no-hashes",
            "--no-annotate",
        ]
        if self.groups:
            command.extend([f"--group={group_name}" for group_name in self.groups])
        if self.extras:
            command.extend([f"--extra={extra_name}" for extra_name in self.extras])
        command.extend(self.uv_args)

        try:
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                cwd=self.root,
            )
            if process.returncode == 0:
                self.logger.info("Successfully generated '%s'.", self.requirements_file_path.name)
                if process.stdout:
                    self.logger.debug("uv stdout:\n%s", process.stdout)
                if process.stderr:  # uv often outputs to stderr even on success
                    self.logger.debug("uv stderr:\n%s", process.stderr)
                return True
            self.logger.error(
                "Failed to generate '%s' with uv.\nExit code: %s\nStdout:\n%s\nStderr:\n%s",
                self.requirements_file_path.name,
                process.returncode,
                process.stdout,
                process.stderr,
            )
            return False
        except FileNotFoundError:
            self.logger.error(
                "'uv' command not found. Please ensure uv is installed and in your PATH. "
                "Cannot generate requirements."
            )
            return False
        except Exception:  # pylint: disable=broad-exception-caught
            self.logger.error("An unexpected error occurred while running uv", exc_info=True)
            return False

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        """Called before the build process starts.

        Generates requirements.txt, then includes its dependencies.
        """
        if os.getenv("HATCH_BUILD_FREEZE_DISABLED", "0").lower() not in ("0", "false"):
            self.logger.info(
                "Hatch Build Freeze is disabled. Set HATCH_BUILD_FREEZE_DISABLED=0 to enable."
            )
            return
        generation_successful = self._generate_requirements_file()

        if not generation_successful and not self.requirements_file_path.exists():
            self.logger.warning(
                "'%s' could not be generated and was not found. "
                "No frozen dependencies will be injected.",
                self.requirements_file_path.name,
            )
            return

        self.logger.info("Reading dependencies from '%s'.", self.requirements_file_path.name)
        try:
            dependencies = self._parse_requirements_file(self.requirements_file_path)
            if "dependencies" not in build_data:
                build_data["dependencies"] = []

            current_deps = set(build_data.get("dependencies", []))
            new_deps = [dep for dep in dependencies if dep not in current_deps]
            if new_deps:
                self.logger.info(
                    "Adding %s new dependencies from %s.",
                    len(new_deps),
                    self.requirements_file_path.name,
                )
                build_data["dependencies"].extend(new_deps)
            elif dependencies:
                self.logger.info(
                    "All dependencies from %s are already listed.",
                    self.requirements_file_path.name,
                )
            else:
                self.logger.info(
                    "%s is empty or contains only comments.",
                    self.requirements_file_path.name,
                )
        except Exception:  # pylint: disable=broad-exception-caught
            self.logger.error("Failed to parse %s", self.requirements_file_path.name, exc_info=True)

    def finalize(self, version: str, build_data: dict[str, Any], artifact_path: str) -> None:
        """Called after the build process ends."""
        if self.requirements_file_path.exists():
            self.logger.info(
                "Deleting generated '%s' after build.", self.requirements_file_path.name
            )
            self.requirements_file_path.unlink()

    def _parse_requirements_file(self, requirements_file_path: Path) -> list[str]:
        """Parses a requirements file, ignoring comments and empty lines."""
        if not requirements_file_path.is_file():
            return []
        try:
            content = requirements_file_path.read_text(encoding="utf-8")
            dependencies = [
                line.strip()
                for line in content.splitlines()
                if line.strip() and not line.strip().startswith("#")
            ]
            return dependencies
        except Exception:  # pylint: disable=broad-exception-caught
            self.logger.error(
                "Error reading or parsing requirements file %s", requirements_file_path
            )
        return []
