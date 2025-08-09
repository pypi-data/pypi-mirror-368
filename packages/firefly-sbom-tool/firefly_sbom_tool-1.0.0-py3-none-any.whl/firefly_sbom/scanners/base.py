"""
Base scanner class for all language-specific scanners

Copyright 2024 Firefly OSS
Licensed under the Apache License, Version 2.0
"""

import hashlib
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..config import Config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class Scanner(ABC):
    """Abstract base class for technology-specific scanners"""

    def __init__(self, config: Config):
        """Initialize scanner with configuration"""
        self.config = config
        self.cache = {}

    @abstractmethod
    def scan(self, path: Path, include_dev: bool = False) -> List[Dict[str, Any]]:
        """
        Scan repository for dependencies

        Args:
            path: Repository path to scan
            include_dev: Whether to include development dependencies

        Returns:
            List of component dictionaries
        """
        pass

    @abstractmethod
    def detect(self, path: Path) -> bool:
        """
        Detect if this scanner applies to the given path

        Args:
            path: Repository path to check

        Returns:
            True if this scanner can handle the repository
        """
        pass

    def create_component(
        self,
        name: str,
        version: str,
        type: str = "library",
        scope: str = "required",
        license: Optional[str] = None,
        description: Optional[str] = None,
        purl: Optional[str] = None,
        hashes: Optional[Dict[str, str]] = None,
        author: Optional[str] = None,
        publisher: Optional[str] = None,
        group: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a standardized component dictionary

        Args:
            name: Component name
            version: Component version
            type: Component type (library, application, framework, etc.)
            scope: Dependency scope (required, optional, excluded)
            license: License identifier
            description: Component description
            purl: Package URL
            hashes: Dictionary of hash algorithms and values
            author: Component author
            publisher: Component publisher
            group: Component group/namespace

        Returns:
            Standardized component dictionary
        """
        component = {
            "name": name,
            "version": version,
            "type": type,
            "scope": scope,
            "bom-ref": self._generate_bom_ref(name, version, group),
        }

        if license:
            component["license"] = license

        if description:
            component["description"] = description

        if purl:
            component["purl"] = purl
        else:
            # Generate PURL if not provided
            component["purl"] = self._generate_purl(name, version, group)

        if hashes:
            component["hashes"] = [
                {"alg": alg, "content": value} for alg, value in hashes.items()
            ]

        if author:
            component["author"] = author

        if publisher:
            component["publisher"] = publisher

        if group:
            component["group"] = group

        return component

    def _generate_bom_ref(
        self, name: str, version: str, group: Optional[str] = None
    ) -> str:
        """Generate a unique BOM reference for a component"""
        if group:
            ref_string = f"{group}/{name}@{version}"
        else:
            ref_string = f"{name}@{version}"

        # Create a hash for uniqueness
        hash_obj = hashlib.sha256(ref_string.encode())
        return f"pkg:{hash_obj.hexdigest()[:16]}"

    def _generate_purl(
        self, name: str, version: str, group: Optional[str] = None
    ) -> str:
        """Generate Package URL (purl) for a component"""
        # This should be overridden by specific scanners
        return f"pkg:generic/{name}@{version}"

    def _read_json_file(self, path: Path) -> Dict[str, Any]:
        """Read and parse JSON file"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading JSON file {path}: {e}")
            return {}

    def _calculate_file_hash(
        self, path: Path, algorithm: str = "sha256"
    ) -> Optional[str]:
        """Calculate hash of a file"""
        try:
            hash_obj = hashlib.new(algorithm)
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash for {path}: {e}")
            return None

    def _normalize_license(self, license_str: str) -> str:
        """Normalize license string to SPDX identifier"""
        # Common license mappings
        license_map = {
            "apache2": "Apache-2.0",
            "apache 2.0": "Apache-2.0",
            "apache-2": "Apache-2.0",
            "mit": "MIT",
            "bsd": "BSD-3-Clause",
            "bsd-3": "BSD-3-Clause",
            "bsd-2": "BSD-2-Clause",
            "gpl3": "GPL-3.0",
            "gpl-3": "GPL-3.0",
            "lgpl3": "LGPL-3.0",
            "lgpl-3": "LGPL-3.0",
            "mpl2": "MPL-2.0",
            "mpl-2": "MPL-2.0",
            "isc": "ISC",
            "unlicense": "Unlicense",
            "cc0": "CC0-1.0",
            "wtfpl": "WTFPL",
            "agpl3": "AGPL-3.0",
            "agpl-3": "AGPL-3.0",
        }

        # Try to match known licenses
        license_lower = license_str.lower().strip()
        if license_lower in license_map:
            return license_map[license_lower]

        # Check if it's already a valid SPDX identifier
        spdx_identifiers = [
            "Apache-2.0",
            "MIT",
            "BSD-3-Clause",
            "BSD-2-Clause",
            "GPL-3.0",
            "LGPL-3.0",
            "MPL-2.0",
            "ISC",
            "Unlicense",
        ]

        if license_str in spdx_identifiers:
            return license_str

        # Return original if no match
        return license_str

    def _is_dev_dependency(self, scope: str) -> bool:
        """Check if a dependency scope indicates development dependency"""
        dev_scopes = ["test", "dev", "development", "provided", "system"]
        return scope.lower() in dev_scopes
