"""
Node.js, TypeScript, and Angular scanner

Copyright 2024 Firefly OSS
Licensed under the Apache License, Version 2.0
"""

import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from ..utils.logger import get_logger
from .base import Scanner

logger = get_logger(__name__)


class NodeScanner(Scanner):
    """Scanner for Node.js, TypeScript, and Angular projects"""

    def detect(self, path: Path) -> bool:
        """Detect if this is a Node.js/TypeScript/Angular project"""
        return (path / "package.json").exists()

    def scan(self, path: Path, include_dev: bool = False) -> List[Dict[str, Any]]:
        """Scan Node.js project for dependencies"""
        components = []

        # Detect project type
        project_type = self._detect_project_type(path)

        # Try to use package-lock.json or yarn.lock for exact versions
        if (path / "package-lock.json").exists():
            components = self._parse_package_lock(path, include_dev)
        elif (path / "yarn.lock").exists():
            components = self._parse_yarn_lock(path, include_dev)
        elif (path / "pnpm-lock.yaml").exists():
            components = self._parse_pnpm_lock(path, include_dev)
        else:
            # Fall back to package.json
            components = self._parse_package_json(path, include_dev)

        # Add framework-specific components
        if project_type:
            components.extend(self._get_framework_components(path, project_type))

        # Try to enhance with npm/yarn commands if available
        if self._is_npm_available():
            components = self._enhance_with_npm_info(path, components)

        return components

    def _detect_project_type(self, path: Path) -> Optional[str]:
        """Detect if this is a special type of Node.js project"""
        package_json = path / "package.json"

        if not package_json.exists():
            return None

        try:
            with open(package_json, "r") as f:
                data = json.load(f)

            dependencies = {
                **data.get("dependencies", {}),
                **data.get("devDependencies", {}),
            }

            # Check for Angular
            if "@angular/core" in dependencies:
                return "angular"

            # Check for React
            if "react" in dependencies:
                return "react"

            # Check for Vue
            if "vue" in dependencies:
                return "vue"

            # Check for Next.js
            if "next" in dependencies:
                return "nextjs"

            # Check for TypeScript
            if "typescript" in dependencies or (path / "tsconfig.json").exists():
                return "typescript"

            # Check for Electron
            if "electron" in dependencies:
                return "electron"

        except Exception as e:
            logger.debug(f"Error detecting project type: {e}")

        return None

    def _parse_package_json(
        self, path: Path, include_dev: bool
    ) -> List[Dict[str, Any]]:
        """Parse package.json for dependencies"""
        components = []
        package_json = path / "package.json"

        if not package_json.exists():
            return components

        try:
            with open(package_json, "r") as f:
                data = json.load(f)

            # Add Node.js version if specified
            if "engines" in data and "node" in data["engines"]:
                node_version = self._parse_version_range(data["engines"]["node"])
                components.append(
                    self.create_component(
                        name="node",
                        version=node_version,
                        type="runtime",
                        scope="required",
                        purl=f"pkg:generic/node@{node_version}",
                    )
                )

            # Process regular dependencies
            for name, version_spec in data.get("dependencies", {}).items():
                version = self._parse_version_range(version_spec)

                component = self.create_component(
                    name=name,
                    version=version,
                    type="library",
                    scope="direct",
                    purl=f"pkg:npm/{name}@{version}",
                )

                components.append(component)

            # Process dev dependencies if included
            if include_dev:
                for name, version_spec in data.get("devDependencies", {}).items():
                    version = self._parse_version_range(version_spec)

                    component = self.create_component(
                        name=name,
                        version=version,
                        type="library",
                        scope="dev",
                        purl=f"pkg:npm/{name}@{version}",
                    )

                    components.append(component)

            # Process optional dependencies
            for name, version_spec in data.get("optionalDependencies", {}).items():
                version = self._parse_version_range(version_spec)

                component = self.create_component(
                    name=name,
                    version=version,
                    type="library",
                    scope="optional",
                    purl=f"pkg:npm/{name}@{version}",
                )

                components.append(component)

            # Process peer dependencies
            for name, version_spec in data.get("peerDependencies", {}).items():
                version = self._parse_version_range(version_spec)

                component = self.create_component(
                    name=name,
                    version=version,
                    type="library",
                    scope="peer",
                    purl=f"pkg:npm/{name}@{version}",
                )

                components.append(component)

        except Exception as e:
            logger.error(f"Error parsing package.json: {e}")

        return components

    def _parse_package_lock(
        self, path: Path, include_dev: bool
    ) -> List[Dict[str, Any]]:
        """Parse package-lock.json for exact versions"""
        components = []
        lock_file = path / "package-lock.json"

        try:
            with open(lock_file, "r") as f:
                lock_data = json.load(f)

            # Handle v1 and v2 lock file formats
            if "lockfileVersion" in lock_data:
                version = lock_data["lockfileVersion"]

                if version == 1:
                    # v1 format
                    dependencies = lock_data.get("dependencies", {})
                    components = self._parse_npm_v1_deps(dependencies, include_dev)

                elif version >= 2:
                    # v2/v3 format
                    packages = lock_data.get("packages", {})
                    components = self._parse_npm_v2_packages(packages, include_dev)

        except Exception as e:
            logger.error(f"Error parsing package-lock.json: {e}")

        return components

    def _parse_npm_v1_deps(
        self, dependencies: Dict, include_dev: bool
    ) -> List[Dict[str, Any]]:
        """Parse npm v1 lock file dependencies"""
        components = []

        for name, info in dependencies.items():
            version = info.get("version", "")
            is_dev = info.get("dev", False)

            # Skip dev dependencies if not included
            if is_dev and not include_dev:
                continue

            # Determine scope
            scope = "dev" if is_dev else "direct"
            if info.get("optional"):
                scope = "optional"
            elif info.get("peer"):
                scope = "peer"

            component = self.create_component(
                name=name,
                version=version,
                type="library",
                scope=scope,
                purl=f"pkg:npm/{name}@{version}",
            )

            # Add integrity hash if available
            if "integrity" in info:
                integrity = info["integrity"]
                if integrity.startswith("sha"):
                    alg, hash_value = integrity.split("-", 1)
                    component["hashes"] = [{"alg": alg, "content": hash_value}]

            components.append(component)

            # Process nested dependencies
            if "dependencies" in info:
                nested_components = self._parse_npm_v1_deps(
                    info["dependencies"], include_dev
                )
                for nested in nested_components:
                    nested["scope"] = "transitive"
                components.extend(nested_components)

        return components

    def _parse_npm_v2_packages(
        self, packages: Dict, include_dev: bool
    ) -> List[Dict[str, Any]]:
        """Parse npm v2+ lock file packages"""
        components = []
        processed = set()

        for path, info in packages.items():
            # Skip root package
            if path == "":
                continue

            # Extract package name from path
            name = path.split("node_modules/")[-1]

            # Skip if already processed
            if name in processed:
                continue
            processed.add(name)

            version = info.get("version", "")
            is_dev = info.get("dev", False)

            # Skip dev dependencies if not included
            if is_dev and not include_dev:
                continue

            # Determine scope
            scope = "dev" if is_dev else "direct"
            if info.get("optional"):
                scope = "optional"
            elif info.get("peer"):
                scope = "peer"
            elif "node_modules" in path.split("/")[:-1]:
                scope = "transitive"

            component = self.create_component(
                name=name,
                version=version,
                type="library",
                scope=scope,
                purl=f"pkg:npm/{name}@{version}",
                license=info.get("license"),
            )

            # Add integrity hash if available
            if "integrity" in info:
                integrity = info["integrity"]
                if integrity.startswith("sha"):
                    alg, hash_value = integrity.split("-", 1)
                    component["hashes"] = [{"alg": alg, "content": hash_value}]

            components.append(component)

        return components

    def _parse_yarn_lock(self, path: Path, include_dev: bool) -> List[Dict[str, Any]]:
        """Parse yarn.lock for exact versions"""
        components = []
        lock_file = path / "yarn.lock"

        try:
            with open(lock_file, "r") as f:
                content = f.read()

            # Parse yarn.lock format
            entries = re.findall(
                r'^"?([^@\s]+@[^"]+)"?:\n\s+version\s+"([^"]+)"', content, re.MULTILINE
            )

            processed = set()

            for spec, version in entries:
                # Extract package name
                match = re.match(r"(@?[^@]+)@", spec)
                if match:
                    name = match.group(1)

                    # Skip if already processed
                    if f"{name}@{version}" in processed:
                        continue
                    processed.add(f"{name}@{version}")

                    component = self.create_component(
                        name=name,
                        version=version,
                        type="library",
                        scope="direct",
                        purl=f"pkg:npm/{name}@{version}",
                    )

                    components.append(component)

        except Exception as e:
            logger.error(f"Error parsing yarn.lock: {e}")

        return components

    def _parse_pnpm_lock(self, path: Path, include_dev: bool) -> List[Dict[str, Any]]:
        """Parse pnpm-lock.yaml for exact versions"""
        components = []
        lock_file = path / "pnpm-lock.yaml"

        try:
            import yaml

            with open(lock_file, "r") as f:
                lock_data = yaml.safe_load(f)

            # Process dependencies
            for name, version in lock_data.get("dependencies", {}).items():
                component = self.create_component(
                    name=name,
                    version=version,
                    type="library",
                    scope="direct",
                    purl=f"pkg:npm/{name}@{version}",
                )
                components.append(component)

            # Process dev dependencies if included
            if include_dev:
                for name, version in lock_data.get("devDependencies", {}).items():
                    component = self.create_component(
                        name=name,
                        version=version,
                        type="library",
                        scope="dev",
                        purl=f"pkg:npm/{name}@{version}",
                    )
                    components.append(component)

        except Exception as e:
            logger.error(f"Error parsing pnpm-lock.yaml: {e}")

        return components

    def _get_framework_components(
        self, path: Path, project_type: str
    ) -> List[Dict[str, Any]]:
        """Get framework-specific components"""
        components = []

        if project_type == "angular":
            # Check for Angular configuration
            angular_json = path / "angular.json"
            if angular_json.exists():
                try:
                    with open(angular_json, "r") as f:
                        angular_config = json.load(f)

                    # Extract Angular CLI version
                    cli_version = angular_config.get("cli", {}).get("version")
                    if cli_version:
                        components.append(
                            self.create_component(
                                name="@angular/cli",
                                version=cli_version,
                                type="framework",
                                scope="required",
                                purl=f"pkg:npm/@angular/cli@{cli_version}",
                            )
                        )

                except Exception as e:
                    logger.debug(f"Error parsing angular.json: {e}")

        elif project_type == "typescript":
            # Check for TypeScript configuration
            tsconfig = path / "tsconfig.json"
            if tsconfig.exists():
                components.append(
                    self.create_component(
                        name="typescript-project",
                        version="detected",
                        type="language",
                        scope="required",
                        purl="pkg:generic/typescript@detected",
                    )
                )

        return components

    def _parse_version_range(self, version_spec: str) -> str:
        """Parse version range specification"""
        if not version_spec or version_spec == "*":
            return "any"

        # Handle GitHub dependencies
        if version_spec.startswith("git") or version_spec.startswith("http"):
            return "git"

        # Handle file dependencies
        if version_spec.startswith("file:"):
            return "local"

        # Handle npm tags
        if version_spec in ["latest", "next", "beta", "alpha"]:
            return version_spec

        # Remove version range operators
        version = re.sub(r"^[\^~>=<\s]+", "", version_spec)
        version = version.split(" ")[0]  # Take first part if space-separated

        return version if version else "any"

    def _is_npm_available(self) -> bool:
        """Check if npm is available"""
        try:
            result = subprocess.run(
                ["npm", "--version"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def _enhance_with_npm_info(
        self, path: Path, components: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Enhance components with npm info"""
        try:
            # Run npm list to get full dependency tree
            result = subprocess.run(
                ["npm", "list", "--json", "--depth=0"],
                cwd=str(path),
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0 and result.stdout:
                list_data = json.loads(result.stdout)

                # Enhance components with additional metadata
                dependencies = list_data.get("dependencies", {})
                for component in components:
                    name = component["name"]
                    if name in dependencies:
                        dep_info = dependencies[name]
                        if "resolved" in dep_info:
                            component["resolved"] = dep_info["resolved"]

        except Exception as e:
            logger.debug(f"Could not enhance with npm info: {e}")

        return components

    def _generate_purl(
        self, name: str, version: str, group: Optional[str] = None
    ) -> str:
        """Generate npm-specific Package URL"""
        # Handle scoped packages
        if name.startswith("@"):
            return f"pkg:npm/{name}@{version}"
        return f"pkg:npm/{name}@{version}"
