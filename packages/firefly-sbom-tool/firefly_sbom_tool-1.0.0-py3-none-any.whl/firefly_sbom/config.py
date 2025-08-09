"""
Configuration management for Firefly SBOM Tool

Copyright 2024 Firefly OSS
Licensed under the Apache License, Version 2.0
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class ScanConfig:
    """Scan configuration settings"""

    include_dev_dependencies: bool = False
    max_depth: int = 5
    parallel_workers: int = 4
    ignore_patterns: List[str] = field(
        default_factory=lambda: [
            "*.test.*",
            "*.spec.*",
            "node_modules/",
            "venv/",
            ".git/",
            "__pycache__/",
            ".pytest_cache/",
            "target/",
            "build/",
            "dist/",
        ]
    )
    follow_symlinks: bool = False
    scan_archives: bool = False


@dataclass
class AuditConfig:
    """Security audit configuration"""

    vulnerability_databases: List[str] = field(
        default_factory=lambda: ["nvd", "osv", "ghsa"]
    )
    fail_on_critical: bool = True
    severity_threshold: str = "medium"
    ignore_vulnerabilities: List[str] = field(default_factory=list)
    check_licenses: bool = True
    allowed_licenses: List[str] = field(
        default_factory=lambda: [
            "Apache-2.0",
            "MIT",
            "BSD-3-Clause",
            "BSD-2-Clause",
            "ISC",
            "LGPL-3.0",
            "MPL-2.0",
        ]
    )
    denied_licenses: List[str] = field(
        default_factory=lambda: ["GPL-3.0", "AGPL-3.0", "Commercial"]
    )


@dataclass
class OutputConfig:
    """Output configuration"""

    formats: List[str] = field(default_factory=lambda: ["cyclonedx-json", "html"])
    include_metadata: bool = True
    timestamp: bool = True
    pretty_print: bool = True
    compress: bool = False
    sign_reports: bool = False


@dataclass
class CacheConfig:
    """Cache configuration"""

    enabled: bool = True
    directory: str = "~/.cache/firefly-sbom"
    ttl_hours: int = 24
    max_size_mb: int = 500


class Config:
    """Main configuration class"""

    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """Initialize configuration from dictionary"""
        config_dict = config_dict or {}

        # Initialize sub-configurations
        self.scan = self._parse_scan_config(config_dict.get("scan", {}))
        self.audit = self._parse_audit_config(config_dict.get("audit", {}))
        self.output = self._parse_output_config(config_dict.get("output", {}))
        self.cache = self._parse_cache_config(config_dict.get("cache", {}))

        # Additional settings
        self.github_token = config_dict.get("github", {}).get(
            "token", os.getenv("GITHUB_TOKEN")
        )
        self.proxy = config_dict.get("proxy")
        self.timeout = config_dict.get("timeout", 300)
        self.verbose = config_dict.get("verbose", False)

    @classmethod
    def from_file(cls, config_path: str) -> "Config":
        """Load configuration from YAML file"""
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(path, "r") as f:
            config_dict = yaml.safe_load(f) or {}

        return cls(config_dict)

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables"""
        config_dict = {}

        # Scan configuration from env
        if os.getenv("SBOM_INCLUDE_DEV"):
            config_dict.setdefault("scan", {})["include_dev_dependencies"] = (
                os.getenv("SBOM_INCLUDE_DEV").lower() == "true"
            )

        if os.getenv("SBOM_MAX_DEPTH"):
            config_dict.setdefault("scan", {})["max_depth"] = int(
                os.getenv("SBOM_MAX_DEPTH")
            )

        # Audit configuration from env
        if os.getenv("SBOM_FAIL_ON_CRITICAL"):
            config_dict.setdefault("audit", {})["fail_on_critical"] = (
                os.getenv("SBOM_FAIL_ON_CRITICAL").lower() == "true"
            )

        if os.getenv("SBOM_SEVERITY_THRESHOLD"):
            config_dict.setdefault("audit", {})["severity_threshold"] = os.getenv(
                "SBOM_SEVERITY_THRESHOLD"
            )

        # Output configuration from env
        if os.getenv("SBOM_OUTPUT_FORMATS"):
            config_dict.setdefault("output", {})["formats"] = os.getenv(
                "SBOM_OUTPUT_FORMATS"
            ).split(",")

        # GitHub token
        if os.getenv("GITHUB_TOKEN"):
            config_dict.setdefault("github", {})["token"] = os.getenv("GITHUB_TOKEN")

        return cls(config_dict)

    def _parse_scan_config(self, scan_dict: Dict[str, Any]) -> ScanConfig:
        """Parse scan configuration"""
        default_ignore_patterns = [
            "*.test.*",
            "*.spec.*",
            "node_modules/",
            "venv/",
            ".git/",
            "__pycache__/",
            ".pytest_cache/",
            "target/",
            "build/",
            "dist/",
        ]
        return ScanConfig(
            include_dev_dependencies=scan_dict.get("include_dev_dependencies", False),
            max_depth=scan_dict.get("max_depth", 5),
            parallel_workers=scan_dict.get("parallel_workers", 4),
            ignore_patterns=scan_dict.get("ignore_patterns", default_ignore_patterns),
            follow_symlinks=scan_dict.get("follow_symlinks", False),
            scan_archives=scan_dict.get("scan_archives", False),
        )

    def _parse_audit_config(self, audit_dict: Dict[str, Any]) -> AuditConfig:
        """Parse audit configuration"""
        default_vuln_dbs = ["nvd", "osv", "ghsa"]
        default_allowed_licenses = [
            "Apache-2.0",
            "MIT",
            "BSD-3-Clause",
            "BSD-2-Clause",
            "ISC",
            "LGPL-3.0",
            "MPL-2.0",
        ]
        default_denied_licenses = ["GPL-3.0", "AGPL-3.0", "Commercial"]

        return AuditConfig(
            vulnerability_databases=audit_dict.get(
                "vulnerability_databases", default_vuln_dbs
            ),
            fail_on_critical=audit_dict.get("fail_on_critical", True),
            severity_threshold=audit_dict.get("severity_threshold", "medium"),
            ignore_vulnerabilities=audit_dict.get("ignore_vulnerabilities", []),
            check_licenses=audit_dict.get("check_licenses", True),
            allowed_licenses=audit_dict.get(
                "allowed_licenses", default_allowed_licenses
            ),
            denied_licenses=audit_dict.get("denied_licenses", default_denied_licenses),
        )

    def _parse_output_config(self, output_dict: Dict[str, Any]) -> OutputConfig:
        """Parse output configuration"""
        default_formats = ["cyclonedx-json", "html"]

        return OutputConfig(
            formats=output_dict.get("formats", default_formats),
            include_metadata=output_dict.get("include_metadata", True),
            timestamp=output_dict.get("timestamp", True),
            pretty_print=output_dict.get("pretty_print", True),
            compress=output_dict.get("compress", False),
            sign_reports=output_dict.get("sign_reports", False),
        )

    def _parse_cache_config(self, cache_dict: Dict[str, Any]) -> CacheConfig:
        """Parse cache configuration"""
        return CacheConfig(
            enabled=cache_dict.get("enabled", True),
            directory=cache_dict.get("directory", "~/.cache/firefly-sbom"),
            ttl_hours=cache_dict.get("ttl_hours", 24),
            max_size_mb=cache_dict.get("max_size_mb", 500),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "scan": {
                "include_dev_dependencies": self.scan.include_dev_dependencies,
                "max_depth": self.scan.max_depth,
                "parallel_workers": self.scan.parallel_workers,
                "ignore_patterns": self.scan.ignore_patterns,
                "follow_symlinks": self.scan.follow_symlinks,
                "scan_archives": self.scan.scan_archives,
            },
            "audit": {
                "vulnerability_databases": self.audit.vulnerability_databases,
                "fail_on_critical": self.audit.fail_on_critical,
                "severity_threshold": self.audit.severity_threshold,
                "ignore_vulnerabilities": self.audit.ignore_vulnerabilities,
                "check_licenses": self.audit.check_licenses,
                "allowed_licenses": self.audit.allowed_licenses,
                "denied_licenses": self.audit.denied_licenses,
            },
            "output": {
                "formats": self.output.formats,
                "include_metadata": self.output.include_metadata,
                "timestamp": self.output.timestamp,
                "pretty_print": self.output.pretty_print,
                "compress": self.output.compress,
                "sign_reports": self.output.sign_reports,
            },
            "cache": {
                "enabled": self.cache.enabled,
                "directory": self.cache.directory,
                "ttl_hours": self.cache.ttl_hours,
                "max_size_mb": self.cache.max_size_mb,
            },
            "github": {"token": self.github_token if self.github_token else None},
            "proxy": self.proxy,
            "timeout": self.timeout,
            "verbose": self.verbose,
        }

    def save(self, path: str):
        """Save configuration to YAML file"""
        config_dict = self.to_dict()

        # Remove None values
        config_dict = {k: v for k, v in config_dict.items() if v is not None}

        with open(path, "w") as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)

    def validate(self) -> List[str]:
        """Validate configuration and return list of warnings"""
        warnings = []

        # Check severity threshold
        valid_severities = ["low", "medium", "high", "critical"]
        if self.audit.severity_threshold not in valid_severities:
            warnings.append(
                f"Invalid severity threshold: {self.audit.severity_threshold}"
            )

        # Check output formats
        valid_formats = [
            "cyclonedx-json",
            "cyclonedx-xml",
            "spdx-json",
            "spdx-yaml",
            "html",
        ]
        for fmt in self.output.formats:
            if fmt not in valid_formats:
                warnings.append(f"Invalid output format: {fmt}")

        # Check cache directory
        cache_dir = Path(self.cache.directory).expanduser()
        if self.cache.enabled and not cache_dir.parent.exists():
            warnings.append(
                f"Cache directory parent does not exist: {cache_dir.parent}"
            )

        return warnings
