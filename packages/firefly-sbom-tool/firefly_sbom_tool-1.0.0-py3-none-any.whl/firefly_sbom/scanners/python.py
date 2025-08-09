"""
Python scanner for pip/poetry/pipenv projects

Copyright 2024 Firefly OSS
Licensed under the Apache License, Version 2.0
"""

import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

import toml

from ..utils.logger import get_logger
from .base import Scanner

logger = get_logger(__name__)


class PythonScanner(Scanner):
    """Scanner for Python projects"""

    def detect(self, path: Path) -> bool:
        """Detect if this is a Python project"""
        indicators = [
            "requirements.txt",
            "requirements-dev.txt",
            "setup.py",
            "setup.cfg",
            "pyproject.toml",
            "Pipfile",
            "Pipfile.lock",
            "poetry.lock",
        ]

        for indicator in indicators:
            if (path / indicator).exists():
                return True

        # Check for requirements*.txt files
        if list(path.glob("requirements*.txt")):
            return True

        return False

    def scan(self, path: Path, include_dev: bool = False) -> List[Dict[str, Any]]:
        """Scan Python project for dependencies"""
        components = []

        # Try different Python package managers
        if (path / "poetry.lock").exists():
            components = self._scan_poetry(path, include_dev)
        elif (path / "Pipfile.lock").exists():
            components = self._scan_pipenv(path, include_dev)
        elif (path / "pyproject.toml").exists():
            # Check if it's a poetry project without lock file
            pyproject = toml.load(path / "pyproject.toml")
            if "tool" in pyproject and "poetry" in pyproject["tool"]:
                components = self._scan_poetry_pyproject(path, include_dev)
            else:
                components = self._scan_pip(path, include_dev)
        else:
            components = self._scan_pip(path, include_dev)

        return components

    def _scan_pip(self, path: Path, include_dev: bool) -> List[Dict[str, Any]]:
        """Scan using pip and requirements files"""
        components = []

        # Find requirements files
        req_files = list(path.glob("requirements*.txt"))
        if not req_files and (path / "setup.py").exists():
            # Try to extract from setup.py
            components = self._parse_setup_py(path)

        for req_file in req_files:
            # Skip dev requirements if not included
            if not include_dev and "dev" in req_file.name:
                continue

            components.extend(self._parse_requirements_file(req_file))

        # Try pip freeze if available
        if not components:
            components = self._scan_pip_freeze(path)

        return components

    def _parse_requirements_file(self, req_file: Path) -> List[Dict[str, Any]]:
        """Parse a requirements.txt file"""
        components = []

        try:
            with open(req_file, "r") as f:
                for line in f:
                    line = line.strip()

                    # Skip comments and empty lines
                    if not line or line.startswith("#"):
                        continue

                    # Skip special pip options
                    if line.startswith("-"):
                        continue

                    # Parse package specification
                    match = re.match(r"^([a-zA-Z0-9\-_\.]+)([=<>!]+)(.+)$", line)
                    if match:
                        name = match.group(1)
                        version = match.group(3).strip()

                        component = self.create_component(
                            name=name,
                            version=version,
                            type="library",
                            scope="direct",
                            purl=f"pkg:pypi/{name}@{version}",
                        )

                        components.append(component)

        except Exception as e:
            logger.error(f"Error parsing requirements file {req_file}: {e}")

        return components

    def _scan_poetry(self, path: Path, include_dev: bool) -> List[Dict[str, Any]]:
        """Scan Poetry project"""
        components = []

        lock_file = path / "poetry.lock"
        if not lock_file.exists():
            return components

        try:
            with open(lock_file, "r") as f:
                lock_data = toml.load(f)

            for package in lock_data.get("package", []):
                # Skip dev dependencies if not included
                if not include_dev and package.get("category") == "dev":
                    continue

                name = package.get("name", "")
                version = package.get("version", "")

                component = self.create_component(
                    name=name,
                    version=version,
                    type="library",
                    scope=(
                        "direct" if package.get("category") == "main" else "transitive"
                    ),
                    description=package.get("description"),
                    purl=f"pkg:pypi/{name}@{version}",
                )

                components.append(component)

        except Exception as e:
            logger.error(f"Error parsing Poetry lock file: {e}")

        return components

    def _scan_pipenv(self, path: Path, include_dev: bool) -> List[Dict[str, Any]]:
        """Scan Pipenv project"""
        components = []

        lock_file = path / "Pipfile.lock"
        if not lock_file.exists():
            return components

        try:
            with open(lock_file, "r") as f:
                lock_data = json.load(f)

            # Process default dependencies
            for name, info in lock_data.get("default", {}).items():
                version = info.get("version", "").lstrip("==")

                component = self.create_component(
                    name=name,
                    version=version,
                    type="library",
                    scope="direct",
                    purl=f"pkg:pypi/{name}@{version}",
                )

                components.append(component)

            # Process dev dependencies if included
            if include_dev:
                for name, info in lock_data.get("develop", {}).items():
                    version = info.get("version", "").lstrip("==")

                    component = self.create_component(
                        name=name,
                        version=version,
                        type="library",
                        scope="dev",
                        purl=f"pkg:pypi/{name}@{version}",
                    )

                    components.append(component)

        except Exception as e:
            logger.error(f"Error parsing Pipfile.lock: {e}")

        return components

    def _scan_poetry_pyproject(
        self, path: Path, include_dev: bool
    ) -> List[Dict[str, Any]]:
        """Scan pyproject.toml for Poetry dependencies"""
        components = []

        try:
            with open(path / "pyproject.toml", "r") as f:
                pyproject = toml.load(f)

            poetry_config = pyproject.get("tool", {}).get("poetry", {})

            # Process main dependencies
            for name, version in poetry_config.get("dependencies", {}).items():
                if name == "python":
                    continue

                # Handle different version specifications
                if isinstance(version, str):
                    version_str = version.lstrip("^~>=<")
                elif isinstance(version, dict):
                    version_str = version.get("version", "*").lstrip("^~>=<")
                else:
                    version_str = "*"

                component = self.create_component(
                    name=name,
                    version=version_str,
                    type="library",
                    scope="direct",
                    purl=f"pkg:pypi/{name}@{version_str}",
                )

                components.append(component)

            # Process dev dependencies if included
            if include_dev:
                for name, version in poetry_config.get("dev-dependencies", {}).items():
                    if isinstance(version, str):
                        version_str = version.lstrip("^~>=<")
                    elif isinstance(version, dict):
                        version_str = version.get("version", "*").lstrip("^~>=<")
                    else:
                        version_str = "*"

                    component = self.create_component(
                        name=name,
                        version=version_str,
                        type="library",
                        scope="dev",
                        purl=f"pkg:pypi/{name}@{version_str}",
                    )

                    components.append(component)

        except Exception as e:
            logger.error(f"Error parsing pyproject.toml: {e}")

        return components

    def _scan_pip_freeze(self, path: Path) -> List[Dict[str, Any]]:
        """Use pip freeze to get installed packages"""
        components = []

        try:
            result = subprocess.run(
                ["pip", "freeze"],
                cwd=str(path),
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if "==" in line:
                        name, version = line.split("==")

                        component = self.create_component(
                            name=name,
                            version=version,
                            type="library",
                            scope="direct",
                            purl=f"pkg:pypi/{name}@{version}",
                        )

                        components.append(component)

        except Exception as e:
            logger.error(f"Error running pip freeze: {e}")

        return components

    def _parse_setup_py(self, path: Path) -> List[Dict[str, Any]]:
        """Parse setup.py for dependencies"""
        components = []
        setup_file = path / "setup.py"

        if not setup_file.exists():
            return components

        try:
            with open(setup_file, "r") as f:
                content = f.read()

            # Simple regex to find install_requires
            match = re.search(r"install_requires\s*=\s*\[(.*?)\]", content, re.DOTALL)
            if match:
                requires_str = match.group(1)

                for line in requires_str.split(","):
                    line = line.strip().strip("\"'")

                    if not line:
                        continue

                    # Parse package specification
                    pkg_match = re.match(r"^([a-zA-Z0-9\-_\.]+)([=<>!]+)?(.*)$", line)
                    if pkg_match:
                        name = pkg_match.group(1)
                        version = (
                            pkg_match.group(3).strip() if pkg_match.group(3) else "*"
                        )

                        component = self.create_component(
                            name=name,
                            version=version,
                            type="library",
                            scope="direct",
                            purl=f"pkg:pypi/{name}@{version}",
                        )

                        components.append(component)

        except Exception as e:
            logger.error(f"Error parsing setup.py: {e}")

        return components

    def _generate_purl(
        self, name: str, version: str, group: Optional[str] = None
    ) -> str:
        """Generate Python-specific Package URL"""
        return f"pkg:pypi/{name}@{version}"
