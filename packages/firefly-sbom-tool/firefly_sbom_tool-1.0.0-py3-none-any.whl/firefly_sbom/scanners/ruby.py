"""
Ruby scanner for Gemfile and Gemfile.lock

Copyright 2024 Firefly OSS
Licensed under the Apache License, Version 2.0
"""

import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..utils.logger import get_logger
from .base import Scanner

logger = get_logger(__name__)


class RubyScanner(Scanner):
    """Scanner for Ruby projects using Bundler"""

    def detect(self, path: Path) -> bool:
        """Detect if this is a Ruby project"""
        return (path / "Gemfile").exists() or (path / "Gemfile.lock").exists()

    def scan(self, path: Path, include_dev: bool = False) -> List[Dict[str, Any]]:
        """Scan Ruby project for dependencies"""
        components = []

        # Try to use Gemfile.lock for exact versions
        if (path / "Gemfile.lock").exists():
            components = self._parse_gemfile_lock(path, include_dev)
        elif (path / "Gemfile").exists():
            components = self._parse_gemfile(path, include_dev)

        # Try to enhance with bundler if available
        if self._is_bundler_available():
            components = self._enhance_with_bundler(path, components)

        return components

    def _parse_gemfile_lock(
        self, path: Path, include_dev: bool
    ) -> List[Dict[str, Any]]:
        """Parse Gemfile.lock for exact versions"""
        components = []
        lock_file = path / "Gemfile.lock"

        try:
            with open(lock_file, "r") as f:
                content = f.read()

            # Parse GEM section
            gem_section = re.search(
                r"GEM\n.*?specs:\n(.*?)(?:\n\n|\Z)", content, re.DOTALL
            )
            if gem_section:
                specs = gem_section.group(1)

                # Parse each gem specification
                gem_pattern = re.compile(r"^    (\S+) \(([^)]+)\)", re.MULTILINE)

                for match in gem_pattern.finditer(specs):
                    name = match.group(1)
                    version = match.group(2)

                    component = self.create_component(
                        name=name,
                        version=version,
                        type="library",
                        scope="direct",
                        purl=f"pkg:gem/{name}@{version}",
                    )

                    components.append(component)

            # Parse BUNDLED WITH section for Bundler version
            bundler_match = re.search(r"BUNDLED WITH\n\s+(\S+)", content)
            if bundler_match:
                bundler_version = bundler_match.group(1)
                components.append(
                    self.create_component(
                        name="bundler",
                        version=bundler_version,
                        type="tool",
                        scope="required",
                        purl=f"pkg:gem/bundler@{bundler_version}",
                    )
                )

            # Parse RUBY VERSION section
            ruby_match = re.search(r"RUBY VERSION\n\s+ruby (\S+)", content)
            if ruby_match:
                ruby_version = ruby_match.group(1)
                components.append(
                    self.create_component(
                        name="ruby",
                        version=ruby_version,
                        type="runtime",
                        scope="required",
                        purl=f"pkg:generic/ruby@{ruby_version}",
                    )
                )

        except Exception as e:
            logger.error(f"Error parsing Gemfile.lock: {e}")

        return components

    def _parse_gemfile(self, path: Path, include_dev: bool) -> List[Dict[str, Any]]:
        """Parse Gemfile for dependencies"""
        components = []
        gemfile = path / "Gemfile"

        try:
            with open(gemfile, "r") as f:
                content = f.read()

            # Parse ruby version
            ruby_match = re.search(r"ruby ['\"]([^'\"]+)['\"]", content)
            if ruby_match:
                ruby_version = ruby_match.group(1)
                components.append(
                    self.create_component(
                        name="ruby",
                        version=ruby_version,
                        type="runtime",
                        scope="required",
                        purl=f"pkg:generic/ruby@{ruby_version}",
                    )
                )

            # Parse gem dependencies
            gem_pattern = re.compile(
                r"gem\s+['\"]([^'\"]+)['\"](?:\s*,\s*['\"]([^'\"]+)['\"])?",
                re.MULTILINE,
            )

            for match in gem_pattern.finditer(content):
                name = match.group(1)
                version = match.group(2) or "latest"

                # Clean version specifiers
                if version and version != "latest":
                    version = re.sub(r"^[~>=<]+\s*", "", version)

                component = self.create_component(
                    name=name,
                    version=version,
                    type="library",
                    scope="direct",
                    purl=f"pkg:gem/{name}@{version}",
                )

                components.append(component)

            # Parse group dependencies if include_dev
            if include_dev:
                group_pattern = re.compile(r"group\s+:(\w+).*?do(.*?)end", re.DOTALL)

                for group_match in group_pattern.finditer(content):
                    group_name = group_match.group(1)
                    group_content = group_match.group(2)

                    if group_name in ["development", "test"]:
                        for gem_match in gem_pattern.finditer(group_content):
                            name = gem_match.group(1)
                            version = gem_match.group(2) or "latest"

                            if version and version != "latest":
                                version = re.sub(r"^[~>=<]+\s*", "", version)

                            component = self.create_component(
                                name=name,
                                version=version,
                                type="library",
                                scope="dev",
                                purl=f"pkg:gem/{name}@{version}",
                            )

                            components.append(component)

        except Exception as e:
            logger.error(f"Error parsing Gemfile: {e}")

        return components

    def _is_bundler_available(self) -> bool:
        """Check if bundler is available"""
        try:
            result = subprocess.run(
                ["bundle", "--version"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def _enhance_with_bundler(
        self, path: Path, components: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Enhance components with bundler info"""
        try:
            # Run bundle list to get installed gems
            result = subprocess.run(
                ["bundle", "list"],
                cwd=str(path),
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                # Parse bundle list output
                for line in result.stdout.split("\n"):
                    match = re.match(r"\s*\*\s+(\S+)\s+\(([^)]+)\)", line)
                    if match:
                        name = match.group(1)
                        version = match.group(2)

                        # Update or add component
                        found = False
                        for component in components:
                            if component["name"] == name:
                                component["version"] = version
                                found = True
                                break

                        if not found:
                            components.append(
                                self.create_component(
                                    name=name,
                                    version=version,
                                    type="library",
                                    scope="direct",
                                    purl=f"pkg:gem/{name}@{version}",
                                )
                            )

        except Exception as e:
            logger.debug(f"Could not enhance with bundler info: {e}")

        return components

    def _generate_purl(
        self, name: str, version: str, group: Optional[str] = None
    ) -> str:
        """Generate Ruby-specific Package URL"""
        return f"pkg:gem/{name}@{version}"
