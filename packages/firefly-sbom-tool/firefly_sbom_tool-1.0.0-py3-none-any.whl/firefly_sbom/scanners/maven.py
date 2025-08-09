"""
Maven scanner for Java/Spring Boot projects

Copyright 2024 Firefly OSS
Licensed under the Apache License, Version 2.0
"""

import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from ..utils.logger import get_logger
from .base import Scanner

logger = get_logger(__name__)


class MavenScanner(Scanner):
    """Scanner for Maven-based Java projects including multi-module projects
    
    Uses Maven commands when available for complete dependency resolution,
    including transitive dependencies, licenses, and vulnerability information.
    """

    def detect(self, path: Path) -> bool:
        """Detect if this is a Maven project"""
        return (path / "pom.xml").exists()

    def scan(self, path: Path, include_dev: bool = False) -> List[Dict[str, Any]]:
        """Scan Maven project for dependencies"""
        components = []

        # Check if Maven is available
        if not self._is_maven_available():
            logger.warning("Maven not found, falling back to POM parsing")
            return self._parse_pom_files(path, include_dev)

        # Try to use Maven dependency tree
        try:
            components = self._scan_with_maven(path, include_dev)
        except Exception as e:
            logger.warning(f"Maven scan failed: {e}, falling back to POM parsing")
            components = self._parse_pom_files(path, include_dev)

        return components

    def _is_maven_available(self) -> bool:
        """Check if Maven is available in the system"""
        try:
            result = subprocess.run(
                ["mvn", "--version"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def _scan_with_maven(self, path: Path, include_dev: bool) -> List[Dict[str, Any]]:
        """Scan using comprehensive Maven commands for complete dependency resolution"""
        components = []
        
        # First, get all dependencies with Maven dependency:list
        components.extend(self._get_maven_dependencies(path, include_dev))
        
        # If we have components, try to enrich with license information
        if components:
            self._enrich_with_license_info(path, components)
        
        return components
        
    def _get_maven_dependencies(self, path: Path, include_dev: bool) -> List[Dict[str, Any]]:
        """Get all dependencies using Maven dependency:list command"""
        components = []
        
        # Use dependency:list for comprehensive dependency resolution
        cmd = [
            "mvn",
            "dependency:list",
            "-DoutputFile=dependencies.txt",
            "-DappendOutput=false",
            "-DincludeScope=compile"
        ]
        
        if include_dev:
            cmd[-1] = "-DincludeScope=compile,provided,runtime,test"
        else:
            cmd[-1] = "-DincludeScope=compile,runtime"
            
        logger.info(f"Running Maven dependency analysis in {path}")
        result = subprocess.run(
            cmd,
            cwd=str(path),
            capture_output=True,
            text=True,
            timeout=self.config.timeout,
        )
        
        if result.returncode == 0:
            # Parse the output file if it exists
            dep_file = path / "dependencies.txt"
            if dep_file.exists():
                components = self._parse_dependency_list_file(dep_file, include_dev)
                dep_file.unlink()  # Clean up
            
            # Also parse from stdout if available
            if result.stdout:
                components.extend(self._parse_dependency_list_output(result.stdout, include_dev))
        
        # If dependency:list failed or returned nothing, try dependency:tree
        if not components:
            components = self._get_maven_dependency_tree(path, include_dev)
        
        return self._remove_duplicates(components)
    
    def _get_maven_dependency_tree(self, path: Path, include_dev: bool) -> List[Dict[str, Any]]:
        """Get dependencies using Maven dependency:tree command"""
        components = []
        
        # Use dependency:tree for hierarchical view
        cmd = ["mvn", "dependency:tree", "-Dverbose"]
        
        if not include_dev:
            cmd.extend(["-Dscopes=compile,runtime"])
        
        result = subprocess.run(
            cmd,
            cwd=str(path),
            capture_output=True,
            text=True,
            timeout=self.config.timeout,
        )
        
        if result.returncode == 0 and result.stdout:
            components = self._parse_dependency_tree_output(result.stdout, include_dev)
        
        return components
        
    def _parse_dependency_list_file(self, dep_file: Path, include_dev: bool) -> List[Dict[str, Any]]:
        """Parse Maven dependency list file"""
        components = []
        
        try:
            with open(dep_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and ':' in line and not line.startswith('['):
                        component = self._parse_maven_coordinate(line, include_dev)
                        if component:
                            components.append(component)
        except Exception as e:
            logger.error(f"Error parsing dependency list file {dep_file}: {e}")
        
        return components
        
    def _parse_dependency_list_output(self, output: str, include_dev: bool) -> List[Dict[str, Any]]:
        """Parse Maven dependency list from stdout"""
        components = []
        
        for line in output.split('\n'):
            line = line.strip()
            if line and ':' in line and not line.startswith('[INFO]') and not line.startswith('[WARNING]'):
                component = self._parse_maven_coordinate(line, include_dev)
                if component:
                    components.append(component)
        
        return components
        
    def _parse_dependency_tree_output(self, output: str, include_dev: bool) -> List[Dict[str, Any]]:
        """Parse Maven dependency tree from stdout"""
        components = []
        
        lines = output.split('\n')
        for line in lines:
            # Look for dependency lines in tree format
            if any(marker in line for marker in ['+- ', '\\- ', '   ']):
                # Extract the Maven coordinates from the line
                coord_match = re.search(r'([a-zA-Z0-9\._-]+):([a-zA-Z0-9\._-]+):([a-zA-Z0-9\._-]+):([a-zA-Z0-9\._-]+)(?::([a-zA-Z0-9\._-]+))?', line)
                if coord_match:
                    groups = coord_match.groups()
                    group_id = groups[0]
                    artifact_id = groups[1] 
                    packaging = groups[2] if len(groups) > 2 else 'jar'
                    version = groups[3] if len(groups) > 3 else ''
                    scope = groups[4] if len(groups) > 4 and groups[4] else 'compile'
                    
                    # Skip if development dependency and not included
                    if not include_dev and self._is_dev_dependency(scope):
                        continue
                    
                    # Determine if direct or transitive based on tree structure
                    is_direct = line.strip().startswith(('+- ', '\\- '))
                    dep_scope = "direct" if is_direct else "transitive"
                    
                    component = self.create_component(
                        name=artifact_id,
                        version=version,
                        type="library",
                        scope=dep_scope,
                        group=group_id,
                        purl=f"pkg:maven/{group_id}/{artifact_id}@{version}",
                    )
                    
                    components.append(component)
        
        return components
        
    def _parse_maven_coordinate(self, coord_line: str, include_dev: bool) -> Optional[Dict[str, Any]]:
        """Parse a single Maven coordinate line"""
        # Maven coordinates format: groupId:artifactId:packaging:version:scope
        # or groupId:artifactId:version:scope
        coord_line = coord_line.strip()
        
        # Remove common prefixes
        coord_line = re.sub(r'^\s*[-+\\|\s]*', '', coord_line)
        
        # Parse coordinates
        parts = coord_line.split(':')
        if len(parts) < 3:
            return None
            
        group_id = parts[0]
        artifact_id = parts[1]
        
        if len(parts) == 3:
            # Format: groupId:artifactId:version
            version = parts[2]
            scope = "compile"
            packaging = "jar"
        elif len(parts) == 4:
            # Format: groupId:artifactId:version:scope
            # or groupId:artifactId:packaging:version
            if parts[2] in ['jar', 'war', 'pom', 'ear', 'rar']:
                packaging = parts[2]
                version = parts[3]
                scope = "compile"
            else:
                packaging = "jar"
                version = parts[2]
                scope = parts[3]
        elif len(parts) == 5:
            # Format: groupId:artifactId:packaging:version:scope
            packaging = parts[2]
            version = parts[3]
            scope = parts[4]
        else:
            # Handle other formats
            packaging = "jar"
            version = parts[-2] if len(parts) > 3 else parts[2]
            scope = parts[-1] if len(parts) > 3 else "compile"
        
        # Clean up scope
        scope = scope or "compile"
        if scope in ['provided', 'test'] and not include_dev:
            return None
            
        component = self.create_component(
            name=artifact_id,
            version=version,
            type="library", 
            scope="direct",  # We'll determine this better later
            group=group_id,
            purl=f"pkg:maven/{group_id}/{artifact_id}@{version}",
        )
        
        return component
        
    def _enrich_with_license_info(self, path: Path, components: List[Dict[str, Any]]) -> None:
        """Enrich components with license information using multiple strategies
        
        Strategy order:
        1) Parse local dependency POMs from ~/.m2/repository to read <licenses>
        2) If POM missing, fetch it via `mvn dependency:get -Dpackaging=pom` (no transitive) and parse
        3) Fallback: attempt project-info-reports:dependencies and parse HTML report
        """
        try:
            # 1) Try resolving licenses from local/fetched POMs
            for comp in components:
                if comp.get('license'):
                    continue
                group = comp.get('group')
                artifact = comp.get('name')
                version = comp.get('version')
                if not (group and artifact and version):
                    continue
                license_value = self._get_license_from_local_pom(group, artifact, version, repo_path=None)
                if not license_value:
                    # Attempt to fetch POM quietly and retry
                    self._fetch_artifact_pom(group, artifact, version, cwd=path)
                    license_value = self._get_license_from_local_pom(group, artifact, version, repo_path=None)
                if license_value:
                    comp['license'] = license_value
            
            # 2) Fallback to project-info-reports HTML parsing if still missing licenses
            if any('license' not in c or not c.get('license') for c in components):
                cmd = [
                    "mvn",
                    "project-info-reports:dependencies",
                    "-DoutputDirectory=target/site",
                    "-q"
                ]
                result = subprocess.run(
                    cmd,
                    cwd=str(path),
                    capture_output=True,
                    text=True,
                    timeout=self.config.timeout,
                )
                if result.returncode == 0:
                    license_file = path / "target" / "site" / "dependencies.html"
                    if license_file.exists():
                        self._parse_license_report(license_file, components)
        except Exception as e:
            logger.debug(f"Failed to enrich license information: {e}")
            
    def _parse_license_report(self, license_file: Path, components: List[Dict[str, Any]]) -> None:
        """Parse license report HTML to extract license information (best-effort)"""
        try:
            with open(license_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            for component in components:
                if component.get('license'):
                    continue
                group_id = component.get('group', '')
                name = component.get('name', '')
                pattern = rf'{re.escape(group_id)}.*?{re.escape(name)}.*?<td>(.*?)</td>'
                matches = re.findall(pattern, content, re.DOTALL)
                if matches:
                    license_text = re.sub(r'<.*?>', '', matches[0]).strip()
                    if license_text and license_text != '-':
                        component['license'] = self._normalize_license(license_text)
        except Exception as e:
            logger.debug(f"Failed to parse license report: {e}")
            
    def _get_license_from_local_pom(self, group: str, artifact: str, version: str, repo_path: Optional[Path]) -> Optional[str]:
        """Attempt to read licenses from a dependency's POM stored in local Maven repository"""
        try:
            if repo_path is None:
                repo_path = Path.home() / ".m2" / "repository"
            pom_path = repo_path / Path(group.replace('.', '/')) / artifact / version / f"{artifact}-{version}.pom"
            if not pom_path.exists():
                return None
            licenses = self._parse_pom_for_licenses(pom_path)
            if licenses:
                # Join multiple licenses with OR (more permissive assumption)
                joined = ' OR '.join([self._normalize_license(l) for l in licenses if l])
                return joined if joined else None
            return None
        except Exception as e:
            logger.debug(f"Failed reading local POM for {group}:{artifact}:{version}: {e}")
            return None
        
    def _fetch_artifact_pom(self, group: str, artifact: str, version: str, cwd: Optional[Path]) -> None:
        """Fetch an artifact POM (only) into local repo using Maven, without transitive deps"""
        try:
            gav = f"{group}:{artifact}:{version}"
            cmd = [
                "mvn",
                "dependency:get",
                f"-Dartifact={gav}",
                "-Dpackaging=pom",
                "-Dtransitive=false",
                "-q",
            ]
            subprocess.run(cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True, timeout=self.config.timeout)
        except Exception as e:
            logger.debug(f"Failed to fetch POM for {gav}: {e}")
        
    def _parse_pom_for_licenses(self, pom_path: Path) -> List[str]:
        """Parse a POM file for <licenses> entries and return list of license names/ids"""
        try:
            tree = ET.parse(pom_path)
            root = tree.getroot()
            ns = {"m": "http://maven.apache.org/POM/4.0.0"}
            licenses = []
            # Try namespaced first
            for lic in root.findall('.//m:licenses/m:license', ns) or root.findall('.//licenses/license'):
                name = lic.findtext('m:name', default=None, namespaces=ns) if hasattr(lic, 'findtext') else None
                if not name:
                    # Try without namespace
                    name_elem = lic.find('name')
                    name = name_elem.text.strip() if name_elem is not None and name_elem.text else None
                if not name:
                    # Some POMs use <license><url> or <comments> indicating the license
                    url_elem = lic.find('m:url', ns) if hasattr(lic, 'find') else None
                    if not url_elem:
                        url_elem = lic.find('url')
                    if url_elem is not None and url_elem.text:
                        name = url_elem.text.strip()
                if name:
                    licenses.append(name)
            return licenses
        except Exception as e:
            logger.debug(f"Failed to parse POM {pom_path} for licenses: {e}")
            return []
            
    def _remove_duplicates(self, components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate components while preserving order"""
        seen = set()
        unique_components = []
        
        for comp in components:
            key = (comp.get('group'), comp.get('name'), comp.get('version'))
            if key not in seen:
                seen.add(key)
                unique_components.append(comp)
                
        return unique_components

    def _parse_maven_tree(
        self, tree_data: Dict, include_dev: bool
    ) -> List[Dict[str, Any]]:
        """Parse Maven dependency tree JSON"""
        components = []

        if isinstance(tree_data, dict):
            # Process main artifact
            self._process_maven_artifact(tree_data, components, include_dev)
        elif isinstance(tree_data, list):
            for artifact in tree_data:
                self._process_maven_artifact(artifact, components, include_dev)

        return components

    def _process_maven_artifact(
        self, artifact: Dict, components: List, include_dev: bool, scope: str = "direct"
    ):
        """Process a single Maven artifact"""
        group_id = artifact.get("groupId", "")
        artifact_id = artifact.get("artifactId", "")
        version = artifact.get("version", "")
        artifact_scope = artifact.get("scope", "compile")

        # Skip if development dependency and not included
        if not include_dev and self._is_dev_dependency(artifact_scope):
            return

        # Create component
        component = self.create_component(
            name=artifact_id,
            version=version,
            type="library",
            scope=scope,
            group=group_id,
            purl=f"pkg:maven/{group_id}/{artifact_id}@{version}",
        )

        components.append(component)

        # Process children (transitive dependencies)
        if "children" in artifact:
            for child in artifact["children"]:
                self._process_maven_artifact(
                    child, components, include_dev, "transitive"
                )

    def _parse_maven_text_tree(
        self, path: Path, include_dev: bool
    ) -> List[Dict[str, Any]]:
        """Parse Maven dependency tree text output"""
        components = []

        # Run Maven dependency:tree in text mode
        cmd = ["mvn", "dependency:tree"]
        if not include_dev:
            cmd.extend(["-Dscope=compile,runtime"])

        result = subprocess.run(
            cmd,
            cwd=str(path),
            capture_output=True,
            text=True,
            timeout=self.config.timeout,
        )

        if result.returncode == 0:
            components = self._parse_dependency_tree_text(result.stdout, include_dev)

        return components

    def _parse_dependency_tree_text(
        self, tree_text: str, include_dev: bool
    ) -> List[Dict[str, Any]]:
        """Parse Maven dependency tree text format"""
        components = []

        # Pattern to match Maven coordinates
        pattern = r"([a-zA-Z0-9\.\-_]+):([a-zA-Z0-9\.\-_]+):([a-zA-Z0-9\.\-_]+):([a-zA-Z0-9\.\-_]+):([a-zA-Z0-9\.\-_]+)"

        for line in tree_text.split("\n"):
            match = re.search(pattern, line)
            if match:
                group_id = match.group(1)
                artifact_id = match.group(2)
                packaging = match.group(3)
                version = match.group(4)
                scope = match.group(5)

                # Skip if development dependency and not included
                if not include_dev and self._is_dev_dependency(scope):
                    continue

                # Determine if direct or transitive
                dep_scope = "direct" if line.startswith("[INFO] +-") else "transitive"

                component = self.create_component(
                    name=artifact_id,
                    version=version,
                    type="library",
                    scope=dep_scope,
                    group=group_id,
                    purl=f"pkg:maven/{group_id}/{artifact_id}@{version}",
                )

                components.append(component)

        return components

    def _parse_pom_files(self, path: Path, include_dev: bool) -> List[Dict[str, Any]]:
        """Parse POM files directly when Maven is not available"""
        components = []
        
        # First, build a property map from all POM files
        properties = self._build_property_map(path)
        
        # Find all POM files (for multi-module projects)
        pom_files = list(path.rglob("pom.xml"))
        
        # Process parent POM first to get dependencyManagement
        root_pom = path / "pom.xml"
        dependency_management = {}
        if root_pom.exists():
            dependency_management = self._parse_dependency_management(root_pom, properties)

        for pom_file in pom_files:
            try:
                components.extend(self._parse_single_pom(pom_file, include_dev, properties, dependency_management))
            except Exception as e:
                logger.error(f"Error parsing POM file {pom_file}: {e}")

        # Remove duplicates while preserving order
        seen = set()
        unique_components = []
        for comp in components:
            key = (comp.get('name'), comp.get('version'), comp.get('group'))
            if key not in seen:
                seen.add(key)
                unique_components.append(comp)

        return unique_components

    def _parse_single_pom(
        self, pom_file: Path, include_dev: bool, properties: Dict[str, str] = None, dependency_management: Dict[str, str] = None
    ) -> List[Dict[str, Any]]:
        """Parse a single POM file with property resolution and dependency management support"""
        components = []
        if properties is None:
            properties = {}
        if dependency_management is None:
            dependency_management = {}

        try:
            tree = ET.parse(pom_file)
            root = tree.getroot()

            # Handle namespace
            ns = {"m": "http://maven.apache.org/POM/4.0.0"}
            
            # Get project info for property resolution
            project_version = self._get_element_text(root, "version", ns)
            if project_version:
                properties["project.version"] = project_version
                properties["version"] = project_version

            # Parse dependencies (not dependencyManagement)
            dependencies = root.findall(".//m:dependencies/m:dependency", ns)
            if not dependencies:
                # Try without namespace
                dependencies = root.findall(".//dependencies/dependency")

            for dep in dependencies:
                group_id = self._get_element_text(dep, "groupId", ns)
                artifact_id = self._get_element_text(dep, "artifactId", ns)
                version = self._get_element_text(dep, "version", ns)
                scope = self._get_element_text(dep, "scope", ns) or "compile"

                # Skip if development dependency and not included
                if not include_dev and self._is_dev_dependency(scope):
                    continue

                # Resolve version from properties or dependency management
                resolved_version = self._resolve_version(version, group_id, artifact_id, properties, dependency_management)
                
                if resolved_version and group_id and artifact_id:
                    component = self.create_component(
                        name=artifact_id,
                        version=resolved_version,
                        type="library",
                        scope="direct",
                        group=group_id,
                        purl=f"pkg:maven/{group_id}/{artifact_id}@{resolved_version}",
                    )

                    components.append(component)

        except ET.ParseError as e:
            logger.error(f"Error parsing XML in {pom_file}: {e}")

        return components

    def _get_element_text(self, parent, tag: str, ns: Dict) -> Optional[str]:
        """Get text from XML element with namespace handling"""
        elem = parent.find(f"m:{tag}", ns)
        if elem is None:
            elem = parent.find(tag)

        return elem.text if elem is not None else None

    def _build_property_map(self, path: Path) -> Dict[str, str]:
        """Build a map of properties from all POM files"""
        properties = {}
        
        # Standard Maven properties
        properties.update({
            "maven.version": "3.8.0",
            "java.version": "17",
        })
        
        # Find all POM files and extract properties
        pom_files = list(path.rglob("pom.xml"))
        
        for pom_file in pom_files:
            try:
                tree = ET.parse(pom_file)
                root = tree.getroot()
                ns = {"m": "http://maven.apache.org/POM/4.0.0"}
                
                # Extract project properties
                project_version = self._get_element_text(root, "version", ns)
                if project_version:
                    properties["project.version"] = project_version
                    properties["version"] = project_version
                    
                # Extract custom properties
                props_elem = root.find(".//m:properties", ns)
                if props_elem is None:
                    props_elem = root.find(".//properties")
                    
                if props_elem is not None:
                    for prop in props_elem:
                        if prop.text:
                            # Remove namespace prefix if present
                            tag_name = prop.tag.split('}')[-1] if '}' in prop.tag else prop.tag
                            properties[tag_name] = prop.text.strip()
                            
            except Exception as e:
                logger.debug(f"Error extracting properties from {pom_file}: {e}")
                
        return properties
    
    def _parse_dependency_management(self, pom_file: Path, properties: Dict[str, str]) -> Dict[str, str]:
        """Parse dependencyManagement section to get version information"""
        dependency_management = {}
        
        try:
            tree = ET.parse(pom_file)
            root = tree.getroot()
            ns = {"m": "http://maven.apache.org/POM/4.0.0"}
            
            # Find dependencyManagement dependencies
            dep_mgmt = root.findall(".//m:dependencyManagement/m:dependencies/m:dependency", ns)
            if not dep_mgmt:
                dep_mgmt = root.findall(".//dependencyManagement/dependencies/dependency")
            
            for dep in dep_mgmt:
                group_id = self._get_element_text(dep, "groupId", ns)
                artifact_id = self._get_element_text(dep, "artifactId", ns)
                version = self._get_element_text(dep, "version", ns)
                
                if group_id and artifact_id and version:
                    key = f"{group_id}:{artifact_id}"
                    resolved_version = self._resolve_property(version, properties)
                    if resolved_version:
                        dependency_management[key] = resolved_version
                        
        except Exception as e:
            logger.debug(f"Error parsing dependency management from {pom_file}: {e}")
            
        return dependency_management
    
    def _resolve_version(self, version: Optional[str], group_id: str, artifact_id: str, 
                        properties: Dict[str, str], dependency_management: Dict[str, str]) -> Optional[str]:
        """Resolve version from properties or dependency management"""
        if not version:
            # Try dependency management
            key = f"{group_id}:{artifact_id}"
            return dependency_management.get(key)
            
        # Resolve property placeholders
        return self._resolve_property(version, properties)
    
    def _resolve_property(self, value: str, properties: Dict[str, str]) -> Optional[str]:
        """Resolve Maven property placeholders like ${property.name}"""
        if not value:
            return None
            
        # Handle property placeholders
        if value.startswith("${") and value.endswith("}"):
            prop_name = value[2:-1]
            return properties.get(prop_name)
            
        # Handle nested properties (simple case)
        import re
        pattern = r'\$\{([^}]+)\}'
        matches = re.findall(pattern, value)
        
        resolved_value = value
        for prop_name in matches:
            prop_value = properties.get(prop_name)
            if prop_value:
                resolved_value = resolved_value.replace(f"${{{prop_name}}}", prop_value)
        
        # Return None if we couldn't resolve all properties
        if "${" in resolved_value:
            return None
            
        return resolved_value

    def _generate_purl(
        self, name: str, version: str, group: Optional[str] = None
    ) -> str:
        """Generate Maven-specific Package URL"""
        if group:
            return f"pkg:maven/{group}/{name}@{version}"
        return f"pkg:maven/{name}@{version}"
    
    def _is_dev_dependency(self, scope: str) -> bool:
        """Check if a dependency is a development dependency based on scope"""
        dev_scopes = {'test', 'provided'}
        return scope.lower() in dev_scopes
