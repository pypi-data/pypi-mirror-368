"""
Core SBOM Generator module

Copyright 2024 Firefly OSS
Licensed under the Apache License, Version 2.0
"""

import asyncio
import json
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import git
import requests

from .auditors import SecurityAuditor
from .config import Config
from .generators import CycloneDXGenerator, HTMLGenerator, SPDXGenerator
from .scanners import (
    FlutterScanner,
    GoScanner,
    MavenScanner,
    NodeScanner,
    PythonScanner,
    RubyScanner,
    RustScanner,
    Scanner,
)
from .utils.github import GitHubAPI, GitHubAPIError
from .utils.logger import get_logger

logger = get_logger(__name__)


class SBOMGenerator:
    """Main SBOM Generator class orchestrating all scanning operations"""

    def __init__(self, config: Config = None):
        """Initialize SBOM Generator with configuration"""
        self.config = config or Config()
        self.scanners = self._initialize_scanners()
        self.generators = self._initialize_generators()
        self.auditor = SecurityAuditor(self.config)

    def _initialize_scanners(self) -> Dict[str, Scanner]:
        """Initialize technology-specific scanners"""
        return {
            "maven": MavenScanner(self.config),
            "python": PythonScanner(self.config),
            "flutter": FlutterScanner(self.config),
            "node": NodeScanner(self.config),
            "go": GoScanner(self.config),
            "ruby": RubyScanner(self.config),
            "rust": RustScanner(self.config),
        }

    def _initialize_generators(self) -> Dict[str, Any]:
        """Initialize report generators"""
        return {
            "cyclonedx-json": CycloneDXGenerator("json"),
            "cyclonedx-xml": CycloneDXGenerator("xml"),
            "spdx-json": SPDXGenerator("json"),
            "spdx-yaml": SPDXGenerator("yaml"),
            "html": HTMLGenerator(),
        }

    def detect_technology_stack(self, path: Path) -> List[Dict[str, Any]]:
        """Detect technology stack in a repository"""
        tech_stack = []

        # Maven/Java detection
        pom_files = list(path.rglob("pom.xml"))
        if pom_files:
            tech_stack.append(
                {
                    "name": "Java/Maven",
                    "type": "maven",
                    "files": [str(f.relative_to(path)) for f in pom_files],
                }
            )

        # Gradle/Java detection
        gradle_files = list(path.rglob("build.gradle")) + list(
            path.rglob("build.gradle.kts")
        )
        if gradle_files:
            tech_stack.append(
                {
                    "name": "Java/Gradle",
                    "type": "gradle",
                    "files": [str(f.relative_to(path)) for f in gradle_files],
                }
            )

        # Python detection
        python_files = (
            list(path.rglob("requirements*.txt"))
            + list(path.rglob("setup.py"))
            + list(path.rglob("pyproject.toml"))
            + list(path.rglob("Pipfile"))
        )
        if python_files:
            tech_stack.append(
                {
                    "name": "Python",
                    "type": "python",
                    "files": [str(f.relative_to(path)) for f in python_files],
                }
            )

        # Flutter/Dart detection
        pubspec_files = list(path.rglob("pubspec.yaml"))
        if pubspec_files:
            tech_stack.append(
                {
                    "name": "Flutter/Dart",
                    "type": "flutter",
                    "files": [str(f.relative_to(path)) for f in pubspec_files],
                }
            )

        # Node.js detection
        package_files = list(path.rglob("package.json"))
        if package_files:
            tech_stack.append(
                {
                    "name": "Node.js",
                    "type": "node",
                    "files": [str(f.relative_to(path)) for f in package_files],
                }
            )

        # Go detection
        go_mod_files = list(path.rglob("go.mod"))
        if go_mod_files:
            tech_stack.append(
                {
                    "name": "Go",
                    "type": "go",
                    "files": [str(f.relative_to(path)) for f in go_mod_files],
                }
            )

        # Ruby detection
        ruby_files = list(path.rglob("Gemfile")) + list(path.rglob("Gemfile.lock"))
        if ruby_files:
            tech_stack.append(
                {
                    "name": "Ruby",
                    "type": "ruby",
                    "files": [str(f.relative_to(path)) for f in ruby_files],
                }
            )

        # Rust detection
        rust_files = list(path.rglob("Cargo.toml")) + list(path.rglob("Cargo.lock"))
        if rust_files:
            tech_stack.append(
                {
                    "name": "Rust",
                    "type": "rust",
                    "files": [str(f.relative_to(path)) for f in rust_files],
                }
            )

        return tech_stack

    def scan_repository(
        self, path: Path, include_dev: bool = False, audit: bool = False
    ) -> Dict[str, Any]:
        """Scan a repository and generate SBOM data"""
        logger.info(f"Scanning repository: {path}")

        # Detect technology stack
        tech_stack = self.detect_technology_stack(path)
        if not tech_stack:
            logger.warning(f"No supported technology stack detected in {path}")
            return self._empty_sbom(path)

        # Collect components from all detected technologies
        all_components = []
        metadata = {
            "repository": str(path),
            "timestamp": datetime.now().isoformat(),
            "technologies": [t["name"] for t in tech_stack],
            "tool": {"name": "Firefly SBOM Tool", "version": "1.0.0"},
        }

        # Scan with appropriate scanners
        for tech in tech_stack:
            scanner_type = tech["type"]
            if scanner_type in self.scanners:
                scanner = self.scanners[scanner_type]
                try:
                    components = scanner.scan(path, include_dev=include_dev)
                    all_components.extend(components)
                    logger.info(
                        f"Found {len(components)} components for {tech['name']}"
                    )
                except Exception as e:
                    logger.error(f"Error scanning {tech['name']}: {e}")

        # Remove duplicates
        unique_components = self._deduplicate_components(all_components)

        # Build SBOM data structure
        sbom_data = {
            "metadata": metadata,
            "components": unique_components,
            "stats": {
                "total_components": len(unique_components),
                "direct_deps": sum(
                    1 for c in unique_components if c.get("scope") == "direct"
                ),
                "transitive_deps": sum(
                    1 for c in unique_components if c.get("scope") == "transitive"
                ),
            },
        }

        # Perform security audit if requested
        if audit:
            logger.info("Performing security audit...")
            vulnerabilities, enhanced_components = self.auditor.audit(unique_components)
            sbom_data["vulnerabilities"] = vulnerabilities
            sbom_data["components"] = enhanced_components  # Use enhanced components with licenses
            sbom_data["stats"]["vulnerabilities"] = len(vulnerabilities)
            
            # Add vulnerability severity breakdown
            severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'unknown': 0}
            for vuln in vulnerabilities:
                severity = vuln.get('severity', 'unknown')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            sbom_data["stats"]["vulnerability_breakdown"] = severity_counts

        return sbom_data

    def scan_repository_url(self, repo_url: str, audit: bool = False) -> Dict[str, Any]:
        """Scan a repository from URL (clone and scan)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "repo"

            # Clone repository
            logger.info(f"Cloning repository: {repo_url}")
            git.Repo.clone_from(repo_url, repo_path, depth=1)

            # Scan the cloned repository
            return self.scan_repository(repo_path, audit=audit)

    def list_org_repositories(
        self, 
        org: str, 
        repo_filter: Optional[List[str]] = None,
        include_private: bool = True,
        include_forks: bool = False,
        include_archived: bool = False,
        languages: Optional[List[str]] = None,
        topics: Optional[List[str]] = None
    ) -> List[Dict[str, str]]:
        """List repositories in a GitHub organization with filtering options
        
        Args:
            org: Organization name
            repo_filter: Optional list of specific repository names to scan
            include_private: Whether to include private repositories
            include_forks: Whether to include forked repositories
            include_archived: Whether to include archived repositories
            languages: Optional list of programming languages to filter by
            topics: Optional list of topics to filter by
            
        Returns:
            List of repository information dictionaries
        """
        github_api = GitHubAPI(token=self.config.github_token)
        
        try:
            # Validate access to organization
            capabilities = github_api.validate_access(org)
            if not capabilities["org_access"]:
                raise GitHubAPIError(f"Unable to access organization: {org}")
            
            # Log access capabilities
            if capabilities["private_repos"]:
                logger.info("✓ Private repository access available")
            else:
                logger.warning("⚠️  Private repository access not available - only public repos will be scanned")
                include_private = False
                
            # Get all organization repositories
            all_repos = github_api.get_organization_repositories(
                org=org,
                include_private=include_private,
                include_forks=include_forks,
                include_archived=include_archived
            )
            
            # Filter by specific repository names if provided
            if repo_filter:
                repo_names = set(repo_filter)
                all_repos = [repo for repo in all_repos if repo["name"] in repo_names]
                logger.info(f"Filtered to {len(all_repos)} specific repositories")
            
            # Apply additional filters
            filtered_repos = github_api.filter_repositories(
                repos=all_repos,
                languages=languages,
                topics=topics
            )
            
            # Convert to expected format for backwards compatibility
            repos = []
            for repo in filtered_repos:
                # Get appropriate clone URL (handles private repo authentication)
                clone_url = github_api.get_clone_url(repo)
                
                repos.append({
                    "name": repo["name"],
                    "url": clone_url,
                    "description": repo.get("description", ""),
                    "language": repo.get("language", "Unknown"),
                    "private": repo.get("private", False),
                    "fork": repo.get("fork", False),
                    "archived": repo.get("archived", False),
                    "topics": repo.get("topics", []),
                    "full_name": repo.get("full_name", f"{org}/{repo['name']}"),
                    "size": repo.get("size", 0),
                    "updated_at": repo.get("updated_at", "")
                })
            
            return repos
            
        except GitHubAPIError as e:
            logger.error(f"GitHub API error: {e}")
            raise Exception(f"Failed to fetch repositories: {e}")

    def generate_report(
        self, sbom_data: Dict[str, Any], format: str, output_path: Optional[Path] = None
    ) -> Path:
        """Generate SBOM report in specified format"""
        if format not in self.generators:
            raise ValueError(f"Unsupported format: {format}")

        generator = self.generators[format]

        # Determine output path with format-specific extension
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ext = format.split("-")[-1]
            final_output_path = Path(f"sbom_{timestamp}.{ext}")
        else:
            # Map format to appropriate file extension
            ext_map = {
                "cyclonedx-json": "json",
                "cyclonedx-xml": "xml", 
                "spdx-json": "json",
                "spdx-yaml": "yaml",
                "html": "html",
                "markdown": "md",
                "text": "txt",
                "json": "json",
            }
            
            # Get base name and add appropriate extension
            base_path = Path(output_path)
            ext = ext_map.get(format, format.split("-")[-1])
            
            if base_path.suffix:
                # If user provided extension, use it
                final_output_path = base_path
            else:
                # Add format-appropriate extension
                final_output_path = base_path.with_suffix(f".{ext}")

        # Generate report
        generator.generate(sbom_data, final_output_path)
        logger.info(f"Generated {format} report: {final_output_path}")

        return final_output_path

    def _deduplicate_components(
        self, components: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Remove duplicate components based on purl or name+version"""
        seen = set()
        unique = []

        for comp in components:
            # Use purl if available, otherwise name+version
            if "purl" in comp:
                key = comp["purl"]
            else:
                key = f"{comp.get('name', '')}@{comp.get('version', '')}"

            if key not in seen:
                seen.add(key)
                unique.append(comp)

        return unique

    def _empty_sbom(self, path: Path) -> Dict[str, Any]:
        """Return empty SBOM structure"""
        return {
            "metadata": {
                "repository": str(path),
                "timestamp": datetime.now().isoformat(),
                "technologies": [],
                "tool": {"name": "Firefly SBOM Tool", "version": "1.0.0"},
            },
            "components": [],
            "stats": {
                "total_components": 0,
                "direct_deps": 0,
                "transitive_deps": 0,
            },
        }

    def scan_organization(
        self,
        org: str,
        output_dir: Path,
        audit: bool = False,
        include_dev: bool = False,
        parallel: int = 4,
        formats: List[str] = None,
        combined_report: bool = True,
        progress_callback: callable = None,
    ) -> Dict[str, Any]:
        """Scan entire GitHub organization with parallel cloning and processing"""
        from .generators import MarkdownGenerator, TextGenerator
        from .utils.parallel import ParallelScanner

        # Set default formats if none specified
        if formats is None:
            formats = ["cyclonedx-json", "html", "markdown"]

        # Create output directory
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Get organization repositories
        logger.info(f"Fetching repositories for organization: {org}")
        repos = self.list_org_repositories(org)

        if not repos:
            logger.warning(f"No repositories found for organization: {org}")
            return {"organization": org, "repositories": [], "stats": {}}

        logger.info(f"Found {len(repos)} repositories in {org}")

        # Use parallel scanner for efficient processing
        parallel_scanner = ParallelScanner(config=self.config, max_workers=parallel)

        # Scan all repositories in parallel with progress callback
        scan_results = parallel_scanner.scan_repositories(
            repos=repos, audit=audit, include_dev=include_dev, progress_callback=progress_callback
        )

        # Generate individual reports for each repository
        for repo_name, sbom_data in scan_results.items():
            if sbom_data and "components" in sbom_data:
                repo_dir = output_dir / repo_name
                repo_dir.mkdir(exist_ok=True)

                # Generate reports in requested formats
                for format_type in formats:
                    self._generate_repo_report(
                        sbom_data=sbom_data,
                        repo_name=repo_name,
                        output_dir=repo_dir,
                        format_type=format_type,
                    )

        # Generate combined report if requested
        org_summary = self._create_org_summary(org, scan_results)

        if combined_report:
            self._generate_combined_reports(
                org_summary=org_summary, output_dir=output_dir, formats=formats
            )

        return org_summary

    def _generate_repo_report(
        self,
        sbom_data: Dict[str, Any],
        repo_name: str,
        output_dir: Path,
        format_type: str,
    ):
        """Generate individual repository report"""
        try:
            ext_map = {
                "cyclonedx-json": "cyclonedx.json",
                "cyclonedx-xml": "cyclonedx.xml",
                "spdx-json": "spdx.json",
                "spdx-yaml": "spdx.yaml",
                "html": "html",
                "markdown": "md",
                "text": "txt",
                "json": "json",
            }

            filename = f"sbom.{ext_map.get(format_type, format_type)}"
            output_path = output_dir / filename

            if format_type in self.generators:
                generator = self.generators[format_type]
                generator.generate(sbom_data, output_path)
            elif format_type == "json":
                # Raw JSON output
                with open(output_path, "w") as f:
                    json.dump(sbom_data, f, indent=2, default=str)

            logger.debug(
                f"Generated {format_type} report for {repo_name}: {output_path}"
            )

        except Exception as e:
            logger.error(
                f"Failed to generate {format_type} report for {repo_name}: {e}"
            )

    def _create_org_summary(
        self, org: str, scan_results: Dict[str, Dict]
    ) -> Dict[str, Any]:
        """Create organization-wide summary with comprehensive vulnerability analysis"""
        total_components = 0
        total_vulnerabilities = 0
        tech_stats = {}
        license_stats = {}
        
        # Initialize vulnerability severity aggregation
        org_vuln_breakdown = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'unknown': 0}
        all_vulnerabilities = []  # Store all vulnerabilities for detailed analysis

        repo_summaries = []

        for repo_name, sbom_data in scan_results.items():
            if sbom_data and "components" in sbom_data:
                components = sbom_data.get("components", [])
                vulnerabilities = sbom_data.get("vulnerabilities", [])

                # Aggregate statistics
                total_components += len(components)
                total_vulnerabilities += len(vulnerabilities)
                
                # Aggregate vulnerabilities for organization-level analysis
                all_vulnerabilities.extend(vulnerabilities)
                
                # Aggregate vulnerability severity breakdown
                repo_breakdown = sbom_data.get("stats", {}).get("vulnerability_breakdown", {})
                for severity, count in repo_breakdown.items():
                    if severity in org_vuln_breakdown:
                        org_vuln_breakdown[severity] += count
                    else:
                        org_vuln_breakdown['unknown'] += count
                
                # Alternative: if breakdown not available, analyze vulnerabilities directly
                if not repo_breakdown and vulnerabilities:
                    for vuln in vulnerabilities:
                        severity = vuln.get('severity', 'unknown').lower()
                        if severity in org_vuln_breakdown:
                            org_vuln_breakdown[severity] += 1
                        else:
                            org_vuln_breakdown['unknown'] += 1

                # Technology statistics
                for tech in sbom_data.get("metadata", {}).get("technologies", []):
                    tech_stats[tech] = tech_stats.get(tech, 0) + 1

                # License statistics
                for comp in components:
                    license_name = comp.get("license", "Unknown")
                    license_stats[license_name] = license_stats.get(license_name, 0) + 1

                # Repository summary with vulnerability breakdown
                repo_vuln_breakdown = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'unknown': 0}
                for vuln in vulnerabilities:
                    severity = vuln.get('severity', 'unknown').lower()
                    if severity in repo_vuln_breakdown:
                        repo_vuln_breakdown[severity] += 1
                    else:
                        repo_vuln_breakdown['unknown'] += 1
                
                repo_summaries.append(
                    {
                        "name": repo_name,
                        "components": len(components),
                        "vulnerabilities": len(vulnerabilities),
                        "vulnerability_breakdown": repo_vuln_breakdown,
                        "technologies": sbom_data.get("metadata", {}).get(
                            "technologies", []
                        ),
                        "status": "success",
                        "description": sbom_data.get("metadata", {}).get("description", "No description available")
                    }
                )
            else:
                repo_summaries.append(
                    {
                        "name": repo_name,
                        "components": 0,
                        "vulnerabilities": 0,
                        "vulnerability_breakdown": {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'unknown': 0},
                        "technologies": [],
                        "status": "failed",
                        "description": "Scan failed - no description available"
                    }
                )

        # Calculate additional statistics
        total_critical = org_vuln_breakdown['critical']
        total_high = org_vuln_breakdown['high']
        total_medium = org_vuln_breakdown['medium']
        total_low = org_vuln_breakdown['low']
        total_unknown = org_vuln_breakdown['unknown']
        
        # Risk assessment
        risk_level = "low"
        if total_critical > 0:
            risk_level = "critical"
        elif total_high > 0:
            risk_level = "high"
        elif total_medium > 0:
            risk_level = "medium"
        
        return {
            "organization": org,
            "scan_date": datetime.now().isoformat(),
            "total_repositories": len(scan_results),
            "successful_scans": sum(
                1 for r in repo_summaries if r["status"] == "success"
            ),
            "failed_scans": sum(1 for r in repo_summaries if r["status"] == "failed"),
            "total_components": total_components,
            "total_vulnerabilities": total_vulnerabilities,
            "vulnerability_breakdown": org_vuln_breakdown,
            "risk_level": risk_level,
            "vulnerabilities": all_vulnerabilities,  # Include all vulnerabilities for detailed reporting
            "technology_distribution": tech_stats,
            "license_distribution": license_stats,
            "repositories": repo_summaries,
        }

    def _generate_combined_reports(
        self, org_summary: Dict[str, Any], output_dir: Path, formats: List[str]
    ):
        """Generate combined organization reports"""
        for format_type in formats:
            try:
                if format_type == "json":
                    output_path = output_dir / "organization-summary.json"
                    with open(output_path, "w") as f:
                        json.dump(org_summary, f, indent=2, default=str)
                elif format_type == "markdown":
                    from .generators import MarkdownGenerator

                    output_path = output_dir / "organization-summary.md"
                    generator = MarkdownGenerator()
                    generator.generate_org_summary(org_summary, output_path)
                elif format_type == "html":
                    output_path = output_dir / "organization-summary.html"
                    if "html" in self.generators:
                        self.generators["html"].generate_org_summary(
                            org_summary, output_path
                        )
                elif format_type == "text":
                    from .generators import TextGenerator

                    output_path = output_dir / "organization-summary.txt"
                    generator = TextGenerator()
                    generator.generate_org_summary(org_summary, output_path)

                logger.info(f"Generated combined {format_type} report: {output_path}")

            except Exception as e:
                logger.error(f"Failed to generate combined {format_type} report: {e}")

    async def scan_multiple_repositories(
        self, repos: List[str], audit: bool = False, parallel: int = 4
    ) -> List[Dict[str, Any]]:
        """Scan multiple repositories in parallel"""
        results = []

        with ThreadPoolExecutor(max_workers=parallel) as executor:
            futures = {
                executor.submit(self.scan_repository_url, repo, audit): repo
                for repo in repos
            }

            for future in as_completed(futures):
                repo = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    logger.info(f"Completed scanning: {repo}")
                except Exception as e:
                    logger.error(f"Failed to scan {repo}: {e}")
                    results.append(self._empty_sbom(Path(repo)))

        return results
