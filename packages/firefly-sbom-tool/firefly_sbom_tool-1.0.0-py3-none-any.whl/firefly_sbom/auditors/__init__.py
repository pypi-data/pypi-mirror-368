"""Enhanced Security auditors with comprehensive vulnerability analysis - Copyright 2024 Firefly OSS"""

import re
import time
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import requests
from packaging import version


class SecurityAuditor:
    """Enhanced security auditor with proper severity categorization and license detection"""
    
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Firefly-SBOM-Tool/1.0.0 (https://github.com/firefly-oss/sbom-tool)'
        })
        
        # Rate limiting for APIs
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests
        
        # License patterns for common licenses
        self.license_patterns = {
            'MIT': [r'MIT License', r'MIT', r'\bMIT\b'],
            'Apache-2.0': [r'Apache License.*2\.0', r'Apache-2\.0', r'\bApache\s*2\b'],
            'GPL-3.0': [r'GNU General Public License.*version 3', r'GPL-3\.0', r'GPLv3'],
            'GPL-2.0': [r'GNU General Public License.*version 2', r'GPL-2\.0', r'GPLv2'],
            'BSD-3-Clause': [r'BSD.*3[- ]Clause', r'BSD-3-Clause'],
            'BSD-2-Clause': [r'BSD.*2[- ]Clause', r'BSD-2-Clause'],
            'LGPL-2.1': [r'GNU Lesser General Public License.*version 2\.1', r'LGPL-2\.1'],
            'LGPL-3.0': [r'GNU Lesser General Public License.*version 3', r'LGPL-3\.0'],
            'ISC': [r'\bISC\b'],
            'Mozilla-2.0': [r'Mozilla Public License.*2\.0', r'MPL-2\.0'],
            'CDDL-1.0': [r'Common Development and Distribution License', r'CDDL'],
            'EPL-1.0': [r'Eclipse Public License.*1\.0', r'EPL-1\.0'],
            'EPL-2.0': [r'Eclipse Public License.*2\.0', r'EPL-2\.0']
        }
    
    def _rate_limit(self):
        """Ensure we don't exceed API rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
    
    def _parse_cvss_vector(self, cvss_vector: str) -> Optional[float]:
        """Parse CVSS vector string to extract numerical score"""
        if not cvss_vector or not isinstance(cvss_vector, str):
            return None
        
        # CVSS v3/v4 base score calculation based on vector components
        cvss_vector = cvss_vector.strip()
        
        # If it's already a number, return it
        try:
            return float(cvss_vector)
        except ValueError:
            pass
        
        # Parse CVSS vector string (e.g., "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H")
        if cvss_vector.startswith('CVSS:'):
            try:
                # Extract version and components
                parts = cvss_vector.split('/')
                if len(parts) < 2:
                    return None
                
                # Simple approximation based on impact metrics
                components = {}
                for part in parts[1:]:
                    if ':' in part:
                        key, value = part.split(':', 1)
                        components[key] = value
                
                # Approximate score based on key components
                base_score = 0.0
                
                # Attack Vector (AV)
                av = components.get('AV', 'L')
                if av == 'N':  # Network
                    base_score += 3.0
                elif av == 'A':  # Adjacent
                    base_score += 2.0
                elif av == 'L':  # Local
                    base_score += 1.0
                
                # Attack Complexity (AC)
                ac = components.get('AC', 'H')
                if ac == 'L':  # Low
                    base_score += 1.5
                elif ac == 'H':  # High
                    base_score += 0.5
                
                # Impact scores
                for impact in ['C', 'I', 'A']:  # Confidentiality, Integrity, Availability
                    impact_val = components.get(impact, 'N')
                    if impact_val == 'H':  # High
                        base_score += 2.5
                    elif impact_val == 'L':  # Low
                        base_score += 1.0
                
                # CVSS v4 specific components
                for impact in ['VC', 'VI', 'VA', 'SC', 'SI', 'SA']:  # Various impact metrics
                    impact_val = components.get(impact, 'N')
                    if impact_val == 'H':  # High
                        base_score += 1.0
                    elif impact_val == 'L':  # Low
                        base_score += 0.3
                
                # Cap the score at 10.0
                return min(base_score, 10.0)
                
            except Exception:
                pass
        
        return None
    
    def _extract_severity_from_cvss(self, cvss_score: Optional[float]) -> str:
        """Extract severity level from CVSS score"""
        if cvss_score is None:
            return "unknown"
        
        if cvss_score >= 9.0:
            return "critical"
        elif cvss_score >= 7.0:
            return "high"
        elif cvss_score >= 4.0:
            return "medium"
        else:
            return "low"
    
    def _parse_severity_from_text(self, text: str) -> str:
        """Parse severity from vulnerability description or metadata"""
        if not text:
            return "unknown"
        
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['critical', 'severe', 'remote code execution', 'rce']):
            return "critical"
        elif any(word in text_lower for word in ['high', 'important', 'privilege escalation', 'sql injection']):
            return "high"
        elif any(word in text_lower for word in ['medium', 'moderate', 'xss', 'cross-site']):
            return "medium"
        elif any(word in text_lower for word in ['low', 'minor', 'information disclosure']):
            return "low"
        
        return "medium"  # Default to medium if unclear
    
    def _detect_license_from_text(self, text: str) -> str:
        """Detect license from text content using patterns"""
        if not text:
            return "Unknown"
        
        # Clean and normalize the text
        text = re.sub(r'\s+', ' ', text.strip())
        
        for license_name, patterns in self.license_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return license_name
        
        # Check for common variations
        if 'unlicense' in text.lower():
            return 'Unlicense'
        elif 'public domain' in text.lower():
            return 'Public Domain'
        elif 'wtfpl' in text.lower():
            return 'WTFPL'
        
        return "Unknown"
    
    def _query_npm_license(self, package_name: str) -> str:
        """Query NPM registry for license information"""
        try:
            self._rate_limit()
            response = self.session.get(
                f"https://registry.npmjs.org/{package_name}/latest",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                license_info = data.get('license', {})
                if isinstance(license_info, str):
                    return license_info
                elif isinstance(license_info, dict):
                    return license_info.get('type', 'Unknown')
        except Exception:
            pass
        return "Unknown"
    
    def _query_maven_license(self, group_id: str, artifact_id: str, version_str: str) -> str:
        """Query Maven Central for license information"""
        try:
            self._rate_limit()
            # Query Maven Central API
            response = self.session.get(
                f"https://search.maven.org/solrsearch/select",
                params={
                    'q': f'g:{group_id} AND a:{artifact_id} AND v:{version_str}',
                    'rows': 1,
                    'wt': 'json'
                },
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                docs = data.get('response', {}).get('docs', [])
                if docs:
                    # Get the POM file for license info
                    doc = docs[0]
                    pom_url = f"https://repo1.maven.org/maven2/{group_id.replace('.', '/')}/{artifact_id}/{version_str}/{artifact_id}-{version_str}.pom"
                    
                    self._rate_limit()
                    pom_response = self.session.get(pom_url, timeout=5)
                    if pom_response.status_code == 200:
                        pom_content = pom_response.text
                        # Extract license from POM
                        license_match = re.search(r'<name>([^<]+)</name>', pom_content)
                        if license_match:
                            license_name = license_match.group(1)
                            return self._detect_license_from_text(license_name)
        except Exception:
            pass
        return "Unknown"
    
    def _query_pypi_license(self, package_name: str) -> str:
        """Query PyPI for license information"""
        try:
            self._rate_limit()
            response = self.session.get(
                f"https://pypi.org/pypi/{package_name}/json",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                info = data.get('info', {})
                
                # Try license field first
                license_info = info.get('license', '')
                if license_info and license_info.strip():
                    return self._detect_license_from_text(license_info)
                
                # Try classifiers
                classifiers = info.get('classifiers', [])
                for classifier in classifiers:
                    if classifier.startswith('License ::'):
                        license_part = classifier.split('::')[-1].strip()
                        return self._detect_license_from_text(license_part)
        except Exception:
            pass
        return "Unknown"
    
    def _enhance_component_license(self, component: Dict[str, Any]) -> str:
        """Enhance component with proper license information"""
        # If license is already detected and not unknown, return it
        existing_license = component.get('license', 'Unknown')
        if existing_license and existing_license != 'Unknown':
            return existing_license
        
        purl = component.get('purl', '')
        if not purl:
            return "Unknown"
        
        # Parse PURL to extract package info
        try:
            # Simple PURL parsing
            if purl.startswith('pkg:'):
                parts = purl.split('/')
                if len(parts) >= 2:
                    ecosystem = purl.split(':')[1].split('/')[0]
                    name_version = parts[-1]
                    
                    if '@' in name_version:
                        name, version_str = name_version.split('@')
                    else:
                        name = name_version
                        version_str = ''
                    
                    # Query appropriate registry based on ecosystem
                    if ecosystem == 'npm':
                        return self._query_npm_license(name)
                    elif ecosystem == 'maven':
                        if len(parts) >= 3:
                            group_artifact = parts[-2]
                            if '/' in group_artifact:
                                group_id = group_artifact.split('/')[0]
                                return self._query_maven_license(group_id, name, version_str)
                    elif ecosystem == 'pypi':
                        return self._query_pypi_license(name)
        except Exception:
            pass
        
        return "Unknown"
    
    def audit(self, components: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Enhanced audit with proper vulnerability categorization and license detection"""
        vulnerabilities = []
        enhanced_components = []
        
        print(f"🔍 Starting enhanced security audit of {len(components)} components...")
        
        for i, component in enumerate(components):
            if i % 10 == 0:
                print(f"   Processed {i}/{len(components)} components...")
            
            # Enhance component with license information
            enhanced_component = component.copy()
            enhanced_component['license'] = self._enhance_component_license(component)
            enhanced_components.append(enhanced_component)
            
            # Query vulnerabilities
            purl = component.get("purl")
            if purl:
                try:
                    self._rate_limit()
                    response = self.session.post(
                        "https://api.osv.dev/v1/query",
                        json={"package": {"purl": purl}},
                        timeout=10,
                    )
                    if response.status_code == 200:
                        data = response.json()
                        for vuln in data.get("vulns", []):
                            # Extract comprehensive vulnerability information
                            vuln_id = vuln.get("id", "")
                            summary = vuln.get("summary", "")
                            details = vuln.get("details", "")
                            
                            # Extract CVSS score if available
                            cvss_score = None
                            severity_from_text = "medium"
                            
                            # Check for severity in database_specific
                            database_specific = vuln.get("database_specific", {})
                            if isinstance(database_specific, dict):
                                cvss_score = database_specific.get("cvss_score")
                                severity_info = database_specific.get("severity")
                                if severity_info:
                                    severity_from_text = severity_info.lower()
                            
                            # Check severity in other fields
                            severity_obj = vuln.get("severity", [])
                            if isinstance(severity_obj, list) and severity_obj:
                                for sev in severity_obj:
                                    if isinstance(sev, dict):
                                        if 'score' in sev:
                                            # Handle both numerical scores and CVSS vectors
                                            score_val = sev['score']
                                            if isinstance(score_val, (int, float)):
                                                cvss_score = float(score_val)
                                            elif isinstance(score_val, str):
                                                # Try to parse CVSS vector
                                                parsed_score = self._parse_cvss_vector(score_val)
                                                if parsed_score is not None:
                                                    cvss_score = parsed_score
                                        if 'type' in sev and sev['type'] == 'CVSS_V3':
                                            score_val = sev.get('score', 0)
                                            if isinstance(score_val, (int, float)):
                                                cvss_score = float(score_val)
                                            elif isinstance(score_val, str):
                                                parsed_score = self._parse_cvss_vector(score_val)
                                                if parsed_score is not None:
                                                    cvss_score = parsed_score
                            
                            # Determine final severity
                            if cvss_score is not None:
                                final_severity = self._extract_severity_from_cvss(cvss_score)
                            else:
                                final_severity = self._parse_severity_from_text(f"{summary} {details} {severity_from_text}")
                            
                            # Extract affected versions
                            affected_versions = []
                            for affected in vuln.get("affected", []):
                                if "ranges" in affected:
                                    for range_info in affected["ranges"]:
                                        affected_versions.extend(range_info.get("events", []))
                            
                            # Create comprehensive vulnerability record
                            vulnerability = {
                                "id": vuln_id,
                                "component": component["name"],
                                "component_version": component.get("version", ""),
                                "severity": final_severity,
                                "cvss_score": cvss_score,
                                "title": summary,
                                "description": details or summary,
                                "affected_versions": affected_versions,
                                "published": vuln.get("published", ""),
                                "modified": vuln.get("modified", ""),
                                "references": [ref.get("url", "") for ref in vuln.get("references", [])],
                                "aliases": vuln.get("aliases", []),
                                "ecosystem": vuln.get("affected", [{}])[0].get("package", {}).get("ecosystem", ""),
                            }
                            
                            vulnerabilities.append(vulnerability)
                            
                except Exception as e:
                    print(f"   Warning: Failed to query vulnerability data for {component['name']}: {e}")
                    continue
        
        print(f"✅ Security audit completed: found {len(vulnerabilities)} vulnerabilities")
        
        # Sort vulnerabilities by severity (critical first)
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'unknown': 4}
        vulnerabilities.sort(key=lambda x: severity_order.get(x['severity'], 4))
        
        return vulnerabilities, enhanced_components


__all__ = ["SecurityAuditor"]
