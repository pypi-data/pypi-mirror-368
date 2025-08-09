"""
Rust scanner for Cargo.toml and Cargo.lock

Copyright 2024 Firefly OSS
Licensed under the Apache License, Version 2.0
"""

import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

import toml

from ..utils.logger import get_logger
from .base import Scanner

logger = get_logger(__name__)


class RustScanner(Scanner):
    """Scanner for Rust projects using Cargo"""

    def detect(self, path: Path) -> bool:
        """Detect if this is a Rust project"""
        return (path / "Cargo.toml").exists()

    def scan(self, path: Path, include_dev: bool = False) -> List[Dict[str, Any]]:
        """Scan Rust project for dependencies"""
        components = []

        # Try to use Cargo.lock for exact versions
        if (path / "Cargo.lock").exists():
            components = self._parse_cargo_lock(path, include_dev)
        elif (path / "Cargo.toml").exists():
            components = self._parse_cargo_toml(path, include_dev)

        # Try to enhance with cargo if available
        if self._is_cargo_available():
            components = self._enhance_with_cargo(path, components, include_dev)

        return components

    def _parse_cargo_lock(self, path: Path, include_dev: bool) -> List[Dict[str, Any]]:
        """Parse Cargo.lock for exact versions"""
        components = []
        lock_file = path / "Cargo.lock"

        try:
            with open(lock_file, "r") as f:
                lock_data = toml.load(f)

            # Parse packages
            for package in lock_data.get("package", []):
                name = package.get("name", "")
                version = package.get("version", "")
                source = package.get("source", "local")

                # Determine scope based on source
                scope = "direct"
                if (
                    source
                    and source
                    != "registry+https://github.com/rust-lang/crates.io-index"
                ):
                    if "git" in source:
                        scope = "git"
                    elif source == "local":
                        scope = "local"

                component = self.create_component(
                    name=name,
                    version=version,
                    type="library",
                    scope=scope,
                    purl=f"pkg:cargo/{name}@{version}",
                )

                # Add checksum if available
                if "checksum" in package:
                    component["hashes"] = [
                        {"alg": "sha256", "content": package["checksum"]}
                    ]

                # Add dependencies list
                if "dependencies" in package:
                    component["dependencies"] = package["dependencies"]

                components.append(component)

            # Add Rust version if specified in metadata
            if "metadata" in lock_data:
                metadata = lock_data["metadata"]
                if isinstance(metadata, dict) and "rust_version" in metadata:
                    rust_version = metadata["rust_version"]
                    components.append(
                        self.create_component(
                            name="rust",
                            version=rust_version,
                            type="runtime",
                            scope="required",
                            purl=f"pkg:generic/rust@{rust_version}",
                        )
                    )

        except Exception as e:
            logger.error(f"Error parsing Cargo.lock: {e}")

        return components

    def _parse_cargo_toml(self, path: Path, include_dev: bool) -> List[Dict[str, Any]]:
        """Parse Cargo.toml for dependencies"""
        components = []
        cargo_toml = path / "Cargo.toml"

        try:
            with open(cargo_toml, "r") as f:
                cargo_data = toml.load(f)

            # Parse workspace members if it's a workspace
            if "workspace" in cargo_data:
                workspace = cargo_data["workspace"]
                if "members" in workspace:
                    for member in workspace["members"]:
                        member_path = path / member
                        if member_path.exists():
                            member_components = self._parse_cargo_toml(
                                member_path, include_dev
                            )
                            components.extend(member_components)

            # Parse package metadata
            if "package" in cargo_data:
                package = cargo_data["package"]

                # Add Rust edition if specified
                if "edition" in package:
                    edition = package["edition"]
                    components.append(
                        self.create_component(
                            name="rust-edition",
                            version=edition,
                            type="language",
                            scope="required",
                            purl=f"pkg:generic/rust-edition@{edition}",
                        )
                    )

                # Add rust-version if specified
                if "rust-version" in package:
                    rust_version = package["rust-version"]
                    components.append(
                        self.create_component(
                            name="rust",
                            version=rust_version,
                            type="runtime",
                            scope="required",
                            purl=f"pkg:generic/rust@{rust_version}",
                        )
                    )

            # Parse dependencies
            dependencies = cargo_data.get("dependencies", {})
            for name, spec in dependencies.items():
                version = self._parse_dependency_spec(spec)

                component = self.create_component(
                    name=name,
                    version=version,
                    type="library",
                    scope="direct",
                    purl=f"pkg:cargo/{name}@{version}",
                )

                # Add features if specified
                if isinstance(spec, dict) and "features" in spec:
                    component["features"] = spec["features"]

                components.append(component)

            # Parse dev-dependencies if included
            if include_dev:
                dev_dependencies = cargo_data.get("dev-dependencies", {})
                for name, spec in dev_dependencies.items():
                    version = self._parse_dependency_spec(spec)

                    component = self.create_component(
                        name=name,
                        version=version,
                        type="library",
                        scope="dev",
                        purl=f"pkg:cargo/{name}@{version}",
                    )

                    components.append(component)

            # Parse build-dependencies
            build_dependencies = cargo_data.get("build-dependencies", {})
            for name, spec in build_dependencies.items():
                version = self._parse_dependency_spec(spec)

                component = self.create_component(
                    name=name,
                    version=version,
                    type="library",
                    scope="build",
                    purl=f"pkg:cargo/{name}@{version}",
                )

                components.append(component)

            # Parse target-specific dependencies
            for target_key, target_value in cargo_data.items():
                if target_key.startswith("target."):
                    if "dependencies" in target_value:
                        for name, spec in target_value["dependencies"].items():
                            version = self._parse_dependency_spec(spec)

                            component = self.create_component(
                                name=name,
                                version=version,
                                type="library",
                                scope="target",
                                purl=f"pkg:cargo/{name}@{version}",
                            )

                            # Add target information
                            component["target"] = target_key.replace("target.", "")

                            components.append(component)

        except Exception as e:
            logger.error(f"Error parsing Cargo.toml: {e}")

        return components

    def _parse_dependency_spec(self, spec) -> str:
        """Parse dependency specification from Cargo.toml"""
        if isinstance(spec, str):
            # Simple version string
            return spec.lstrip("^~>=<")

        elif isinstance(spec, dict):
            # Complex specification
            if "version" in spec:
                return spec["version"].lstrip("^~>=<")
            elif "git" in spec:
                # Git dependency
                ref = spec.get("branch") or spec.get("tag") or spec.get("rev") or "main"
                return f"git+{ref}"
            elif "path" in spec:
                # Local path dependency
                return "local"
            else:
                return "unknown"

        return "unknown"

    def _is_cargo_available(self) -> bool:
        """Check if cargo is available"""
        try:
            result = subprocess.run(
                ["cargo", "--version"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def _enhance_with_cargo(
        self, path: Path, components: List[Dict[str, Any]], include_dev: bool
    ) -> List[Dict[str, Any]]:
        """Enhance components with cargo metadata"""
        try:
            # Run cargo metadata to get detailed information
            cmd = ["cargo", "metadata", "--format-version", "1"]
            if not include_dev:
                cmd.append("--no-deps")

            result = subprocess.run(
                cmd, cwd=str(path), capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                import json

                metadata = json.loads(result.stdout)

                # Create a map of existing components
                comp_map = {c["name"]: c for c in components}

                # Process packages from metadata
                for package in metadata.get("packages", []):
                    name = package["name"]
                    version = package["version"]

                    if name in comp_map:
                        # Update existing component
                        comp = comp_map[name]
                        comp["version"] = version

                        # Add license information
                        if "license" in package:
                            comp["license"] = self._normalize_license(
                                package["license"]
                            )

                        # Add repository
                        if "repository" in package:
                            comp["repository"] = package["repository"]

                        # Add authors
                        if "authors" in package and package["authors"]:
                            comp["authors"] = package["authors"]
                    else:
                        # Add new component
                        component = self.create_component(
                            name=name,
                            version=version,
                            type="library",
                            scope="direct",
                            purl=f"pkg:cargo/{name}@{version}",
                            license=package.get("license"),
                            description=package.get("description"),
                        )

                        if "repository" in package:
                            component["repository"] = package["repository"]

                        if "authors" in package and package["authors"]:
                            component["authors"] = package["authors"]

                        components.append(component)

                # Process resolve information for exact versions
                if "resolve" in metadata and metadata["resolve"]:
                    resolve = metadata["resolve"]

                    for node in resolve.get("nodes", []):
                        pkg_id = node["id"]
                        # Extract name and version from package ID
                        match = re.match(r"(.+) (.+) \((.+)\)", pkg_id)
                        if match:
                            name = match.group(1)
                            version = match.group(2)

                            # Update component version if it exists
                            for comp in components:
                                if comp["name"] == name:
                                    comp["version"] = version
                                    break

        except Exception as e:
            logger.debug(f"Could not enhance with cargo metadata: {e}")

        return components

    def _generate_purl(
        self, name: str, version: str, group: Optional[str] = None
    ) -> str:
        """Generate Rust-specific Package URL"""
        return f"pkg:cargo/{name}@{version}"
