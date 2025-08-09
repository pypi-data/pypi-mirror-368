"""
Flutter/Dart scanner for pubspec.yaml and pubspec.lock

Copyright 2024 Firefly OSS
Licensed under the Apache License, Version 2.0
"""

import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from ..utils.logger import get_logger
from .base import Scanner

logger = get_logger(__name__)


class FlutterScanner(Scanner):
    """Scanner for Flutter/Dart projects"""

    def detect(self, path: Path) -> bool:
        """Detect if this is a Flutter/Dart project"""
        return (path / "pubspec.yaml").exists()

    def scan(self, path: Path, include_dev: bool = False) -> List[Dict[str, Any]]:
        """Scan Flutter/Dart project for dependencies"""
        components = []

        # Try to use pubspec.lock first (more accurate)
        if (path / "pubspec.lock").exists():
            components = self._parse_pubspec_lock(path, include_dev)

        # Fall back to pubspec.yaml if no lock file
        if not components and (path / "pubspec.yaml").exists():
            components = self._parse_pubspec_yaml(path, include_dev)

        # Try to get more info using flutter/dart commands if available
        if self._is_flutter_available():
            components = self._enhance_with_flutter_info(path, components)

        return components

    def _parse_pubspec_lock(
        self, path: Path, include_dev: bool
    ) -> List[Dict[str, Any]]:
        """Parse pubspec.lock for exact dependency versions"""
        components = []
        lock_file = path / "pubspec.lock"

        try:
            with open(lock_file, "r") as f:
                lock_data = yaml.safe_load(f)

            packages = lock_data.get("packages", {})

            for name, info in packages.items():
                # Skip SDK packages
                if info.get("source") == "sdk":
                    continue

                # Determine if it's a dev dependency
                dependency_type = info.get("dependency", "direct main")
                is_dev = "dev" in dependency_type.lower()

                # Skip dev dependencies if not included
                if is_dev and not include_dev:
                    continue

                version = info.get("version", "unknown")
                description = info.get("description", {})

                # Extract repository URL if available
                repository = None
                if isinstance(description, dict):
                    repository = description.get("url")

                # Determine scope
                scope = "direct" if "direct" in dependency_type else "transitive"
                if is_dev:
                    scope = "dev"

                component = self.create_component(
                    name=name,
                    version=version,
                    type="library",
                    scope=scope,
                    purl=f"pkg:pub/{name}@{version}",
                    description=(
                        description.get("name")
                        if isinstance(description, dict)
                        else None
                    ),
                )

                # Add repository URL if available
                if repository:
                    component["repository"] = repository

                components.append(component)

        except Exception as e:
            logger.error(f"Error parsing pubspec.lock: {e}")

        return components

    def _parse_pubspec_yaml(
        self, path: Path, include_dev: bool
    ) -> List[Dict[str, Any]]:
        """Parse pubspec.yaml for dependencies"""
        components = []
        pubspec_file = path / "pubspec.yaml"

        try:
            with open(pubspec_file, "r") as f:
                pubspec_data = yaml.safe_load(f)

            # Process regular dependencies
            dependencies = pubspec_data.get("dependencies", {})
            for name, version_spec in dependencies.items():
                # Skip Flutter SDK
                if name == "flutter":
                    continue

                version = self._parse_version_spec(version_spec)

                component = self.create_component(
                    name=name,
                    version=version,
                    type="library",
                    scope="direct",
                    purl=f"pkg:pub/{name}@{version}",
                )

                components.append(component)

            # Process dev dependencies if included
            if include_dev:
                dev_dependencies = pubspec_data.get("dev_dependencies", {})
                for name, version_spec in dev_dependencies.items():
                    # Skip Flutter test SDK
                    if name in ["flutter_test", "flutter_lints"]:
                        continue

                    version = self._parse_version_spec(version_spec)

                    component = self.create_component(
                        name=name,
                        version=version,
                        type="library",
                        scope="dev",
                        purl=f"pkg:pub/{name}@{version}",
                    )

                    components.append(component)

            # Add Flutter SDK version if specified
            environment = pubspec_data.get("environment", {})
            if "flutter" in environment:
                flutter_version = self._parse_version_spec(environment["flutter"])
                components.append(
                    self.create_component(
                        name="flutter-sdk",
                        version=flutter_version,
                        type="framework",
                        scope="required",
                        purl=f"pkg:generic/flutter@{flutter_version}",
                    )
                )

            # Add Dart SDK version if specified
            if "sdk" in environment:
                dart_version = self._parse_version_spec(environment["sdk"])
                components.append(
                    self.create_component(
                        name="dart-sdk",
                        version=dart_version,
                        type="runtime",
                        scope="required",
                        purl=f"pkg:generic/dart@{dart_version}",
                    )
                )

        except Exception as e:
            logger.error(f"Error parsing pubspec.yaml: {e}")

        return components

    def _parse_version_spec(self, version_spec) -> str:
        """Parse version specification from pubspec"""
        if version_spec is None:
            return "any"

        if isinstance(version_spec, str):
            # Remove version constraints
            version = version_spec.strip()
            version = re.sub(r"^[\^~>=<]+", "", version)
            return version if version else "any"

        if isinstance(version_spec, dict):
            # Handle git dependencies
            if "git" in version_spec:
                git_info = version_spec["git"]
                if isinstance(git_info, dict):
                    return git_info.get("ref", "main")
                return "git"

            # Handle path dependencies
            if "path" in version_spec:
                return "local"

            # Handle hosted dependencies
            if "hosted" in version_spec:
                return version_spec.get("version", "any")

            # Handle version key
            if "version" in version_spec:
                return self._parse_version_spec(version_spec["version"])

        return "any"

    def _is_flutter_available(self) -> bool:
        """Check if Flutter CLI is available"""
        try:
            result = subprocess.run(
                ["flutter", "--version"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def _enhance_with_flutter_info(
        self, path: Path, components: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Enhance component info using Flutter CLI"""
        try:
            # Run flutter pub deps to get dependency tree
            result = subprocess.run(
                ["flutter", "pub", "deps", "--json"],
                cwd=str(path),
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0 and result.stdout:
                # Parse JSON output if available
                import json

                deps_data = json.loads(result.stdout)

                # Enhance existing components with additional info
                for component in components:
                    name = component["name"]
                    if name in deps_data:
                        dep_info = deps_data[name]
                        if "license" in dep_info:
                            component["license"] = self._normalize_license(
                                dep_info["license"]
                            )
                        if "homepage" in dep_info:
                            component["homepage"] = dep_info["homepage"]

        except Exception as e:
            logger.debug(f"Could not enhance with Flutter info: {e}")

        return components

    def _generate_purl(
        self, name: str, version: str, group: Optional[str] = None
    ) -> str:
        """Generate Dart/Flutter-specific Package URL"""
        return f"pkg:pub/{name}@{version}"
