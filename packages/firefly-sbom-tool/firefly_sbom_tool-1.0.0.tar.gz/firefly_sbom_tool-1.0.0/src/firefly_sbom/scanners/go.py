"""
Go scanner for go.mod and go.sum files

Copyright 2024 Firefly OSS
Licensed under the Apache License, Version 2.0
"""

import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..utils.logger import get_logger
from .base import Scanner

logger = get_logger(__name__)


class GoScanner(Scanner):
    """Scanner for Go projects using go.mod"""

    def detect(self, path: Path) -> bool:
        """Detect if this is a Go project"""
        return (path / "go.mod").exists()

    def scan(self, path: Path, include_dev: bool = False) -> List[Dict[str, Any]]:
        """Scan Go project for dependencies"""
        components = []

        # Try to use go command if available
        if self._is_go_available():
            components = self._scan_with_go_command(path, include_dev)

        # Fall back to parsing go.mod and go.sum
        if not components:
            components = self._parse_go_mod(path)

            # Enhance with go.sum information
            if (path / "go.sum").exists():
                components = self._enhance_with_go_sum(path, components)

        return components

    def _is_go_available(self) -> bool:
        """Check if Go is available in the system"""
        try:
            result = subprocess.run(
                ["go", "version"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def _scan_with_go_command(
        self, path: Path, include_dev: bool
    ) -> List[Dict[str, Any]]:
        """Scan using go list command"""
        components = []

        try:
            # Get all module dependencies
            result = subprocess.run(
                ["go", "list", "-m", "-json", "all"],
                cwd=str(path),
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                # Parse JSON output
                modules = []
                for line in result.stdout.strip().split("\n"):
                    if line:
                        try:
                            modules.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue

                # Process modules (skip the main module)
                for module in modules[1:]:
                    name = module.get("Path", "")
                    version = module.get("Version", "")

                    if not name or not version:
                        continue

                    # Check if it's an indirect dependency
                    is_indirect = module.get("Indirect", False)

                    # Get replace information if any
                    replace = module.get("Replace")
                    if replace:
                        # Use the replacement module
                        name = replace.get("Path", name)
                        version = replace.get("Version", version)

                    component = self.create_component(
                        name=name,
                        version=version,
                        type="library",
                        scope="indirect" if is_indirect else "direct",
                        purl=self._create_go_purl(name, version),
                    )

                    # Add additional metadata
                    if module.get("Time"):
                        component["timestamp"] = module["Time"]

                    if module.get("GoVersion"):
                        component["go_version"] = module["GoVersion"]

                    components.append(component)

            # Get build dependencies if needed
            if include_dev:
                components.extend(self._get_build_dependencies(path))

        except subprocess.TimeoutExpired:
            logger.error("Go command timed out")
        except Exception as e:
            logger.error(f"Error running go command: {e}")

        return components

    def _parse_go_mod(self, path: Path) -> List[Dict[str, Any]]:
        """Parse go.mod file directly"""
        components = []
        go_mod_file = path / "go.mod"

        if not go_mod_file.exists():
            return components

        try:
            with open(go_mod_file, "r") as f:
                content = f.read()

            # Extract module name
            module_match = re.search(r"^module\s+(\S+)", content, re.MULTILINE)
            module_name = module_match.group(1) if module_match else None

            # Extract Go version
            go_version_match = re.search(r"^go\s+([\d.]+)", content, re.MULTILINE)
            go_version = go_version_match.group(1) if go_version_match else None

            if go_version:
                components.append(
                    self.create_component(
                        name="go",
                        version=go_version,
                        type="runtime",
                        scope="required",
                        purl=f"pkg:generic/go@{go_version}",
                    )
                )

            # Parse require blocks
            require_blocks = re.findall(
                r"require\s*\((.*?)\)", content, re.DOTALL | re.MULTILINE
            )

            # Parse individual require statements
            individual_requires = re.findall(
                r"^require\s+(\S+)\s+v([\d.\-+\w]+)(?:\s+//\s+indirect)?",
                content,
                re.MULTILINE,
            )

            # Process require blocks
            for block in require_blocks:
                lines = block.strip().split("\n")
                for line in lines:
                    match = re.match(
                        r"\s*(\S+)\s+v([\d.\-+\w]+)(?:\s+//\s+indirect)?", line
                    )
                    if match:
                        name = match.group(1)
                        version = match.group(2)
                        is_indirect = "// indirect" in line

                        component = self.create_component(
                            name=name,
                            version=version,
                            type="library",
                            scope="indirect" if is_indirect else "direct",
                            purl=self._create_go_purl(name, version),
                        )
                        components.append(component)

            # Process individual requires
            for name, version in individual_requires:
                is_indirect = "// indirect" in content
                component = self.create_component(
                    name=name,
                    version=version,
                    type="library",
                    scope="indirect" if is_indirect else "direct",
                    purl=self._create_go_purl(name, version),
                )
                components.append(component)

            # Parse replace directives
            replace_matches = re.findall(
                r"replace\s+(\S+)(?:\s+v([\d.\-+\w]+))?\s*=>\s*(\S+)(?:\s+v([\d.\-+\w]+))?",
                content,
                re.MULTILINE,
            )

            # Update components with replacements
            for old_path, old_version, new_path, new_version in replace_matches:
                # Find and update the component
                for component in components:
                    if component["name"] == old_path:
                        component["replaced_by"] = {
                            "name": new_path,
                            "version": new_version or "local",
                        }
                        if new_path.startswith(".") or new_path.startswith("/"):
                            component["scope"] = "local"

        except Exception as e:
            logger.error(f"Error parsing go.mod: {e}")

        return components

    def _enhance_with_go_sum(
        self, path: Path, components: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Enhance components with checksums from go.sum"""
        go_sum_file = path / "go.sum"

        if not go_sum_file.exists():
            return components

        try:
            checksums = {}

            with open(go_sum_file, "r") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 3:
                        module_version = parts[0]
                        checksum_type = parts[1]
                        checksum = parts[2]

                        # Extract module and version
                        match = re.match(r"(.+?)\s+v([\d.\-+\w]+)", module_version)
                        if match:
                            module = match.group(1)
                            version = match.group(2)

                            if module not in checksums:
                                checksums[module] = {}
                            if version not in checksums[module]:
                                checksums[module][version] = {}

                            checksums[module][version][checksum_type] = checksum

            # Add checksums to components
            for component in components:
                name = component["name"]
                version = component["version"]

                if name in checksums and version in checksums[name]:
                    hashes = {}
                    for checksum_type, checksum in checksums[name][version].items():
                        if "/go.mod" in checksum_type:
                            hashes["go.mod"] = checksum
                        else:
                            hashes["sha256"] = checksum

                    if hashes:
                        component["hashes"] = [
                            {"alg": alg, "content": value}
                            for alg, value in hashes.items()
                        ]

        except Exception as e:
            logger.error(f"Error parsing go.sum: {e}")

        return components

    def _get_build_dependencies(self, path: Path) -> List[Dict[str, Any]]:
        """Get build/tool dependencies"""
        components = []

        try:
            # Check for tools.go file (common pattern for tool dependencies)
            tools_file = path / "tools.go"
            if tools_file.exists():
                with open(tools_file, "r") as f:
                    content = f.read()

                # Extract imports from tools.go
                import_matches = re.findall(r'import\s+(?:_\s+)?"([^"]+)"', content)

                for import_path in import_matches:
                    # Try to get version from go.mod
                    component = self.create_component(
                        name=import_path,
                        version="latest",
                        type="tool",
                        scope="dev",
                        purl=self._create_go_purl(import_path, "latest"),
                    )
                    components.append(component)

        except Exception as e:
            logger.debug(f"Could not get build dependencies: {e}")

        return components

    def _create_go_purl(self, name: str, version: str) -> str:
        """Create Go-specific Package URL"""
        # Handle pseudo-versions
        if "+incompatible" in version:
            version = version.replace("+incompatible", "")

        # URL encode the module path
        import urllib.parse

        encoded_name = urllib.parse.quote(name, safe="")

        return f"pkg:golang/{encoded_name}@{version}"

    def _generate_purl(
        self, name: str, version: str, group: Optional[str] = None
    ) -> str:
        """Generate Go-specific Package URL"""
        return self._create_go_purl(name, version)
