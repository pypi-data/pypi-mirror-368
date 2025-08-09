"""Report generators - Copyright 2024 Firefly OSS"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import yaml
from cyclonedx.model.bom import Bom
from cyclonedx.model.component import Component
from cyclonedx.output import OutputFormat, make_outputter
from cyclonedx.schema import SchemaVersion


class CycloneDXGenerator:
    def __init__(self, format_type):
        self.format_type = format_type

    def generate(self, sbom_data: Dict[str, Any], output_path: Path):
        bom = Bom()
        for comp in sbom_data.get("components", []):
            component = Component(name=comp["name"], version=comp.get("version"))
            bom.components.add(component)

        output_format = (
            OutputFormat.JSON if self.format_type == "json" else OutputFormat.XML
        )
        outputter = make_outputter(
            bom, output_format=output_format, schema_version=SchemaVersion.V1_6
        )
        with open(output_path, "w") as f:
            f.write(outputter.output_as_string())


class SPDXGenerator:
    def __init__(self, format_type):
        self.format_type = format_type

    def generate(self, sbom_data: Dict[str, Any], output_path: Path):
        spdx_doc = {
            "spdxVersion": "SPDX-2.3",
            "name": "SBOM Document",
            "packages": [
                {"name": c["name"], "version": c.get("version", "")}
                for c in sbom_data.get("components", [])
            ],
        }

        with open(output_path, "w") as f:
            if self.format_type == "json":
                json.dump(spdx_doc, f, indent=2)
            else:
                yaml.dump(spdx_doc, f)


class HTMLGenerator:
    def generate(self, sbom_data: Dict[str, Any], output_path: Path):
        """Generate pretty HTML report"""
        html = self._generate_html_report(sbom_data)
        with open(output_path, "w") as f:
            f.write(html)

    def generate_org_summary(self, org_summary: Dict[str, Any], output_path: Path):
        """Generate organization summary HTML report"""
        html = self._generate_org_html_report(org_summary)
        with open(output_path, "w") as f:
            f.write(html)

    def _generate_html_report(self, sbom_data: Dict[str, Any]) -> str:
        """Generate enhanced HTML content for SBOM report with comprehensive vulnerability and license analysis"""
        metadata = sbom_data.get("metadata", {})
        components = sbom_data.get("components", [])
        stats = sbom_data.get("stats", {})
        vulnerabilities = sbom_data.get("vulnerabilities", [])
        
        # Process vulnerability data by severity
        vuln_by_severity = self._categorize_vulnerabilities(vulnerabilities)
        
        # Process license data
        license_stats = self._analyze_licenses(components)
        
        # Group components by type
        components_by_type = {}
        for comp in components:
            comp_type = comp.get("type", "library")
            if comp_type not in components_by_type:
                components_by_type[comp_type] = []
            components_by_type[comp_type].append(comp)

        # Generate comprehensive vulnerability section
        vuln_html = self._generate_vulnerability_section(vulnerabilities, vuln_by_severity)
        
        # Generate license analysis section
        license_html = self._generate_license_section(license_stats)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{metadata.get('repository_name', 'Repository')} | SBOM Security Report</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        {self._get_enhanced_single_css_styles()}
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">
            <i class="fas fa-shield-alt"></i>
            <span>Firefly SBOM</span>
        </div>
        <div class="nav-links">
            <a href="#overview"><i class="fas fa-chart-line"></i> Overview</a>
            <a href="#components"><i class="fas fa-cubes"></i> Components</a>
            {'<a href="#vulnerabilities"><i class="fas fa-exclamation-triangle"></i> Security</a>' if vulnerabilities else ''}
            {'<a href="#licenses"><i class="fas fa-balance-scale"></i> Licenses</a>' if license_stats['total_components'] > 0 else ''}
        </div>
    </nav>

    <main class="main-content">
        <section id="overview" class="hero-section">
            <div class="hero-content">
                <div class="hero-text">
                    <h1><i class="fas fa-cube"></i> {metadata.get('repository_name', metadata.get('repository', 'Repository'))}</h1>
                    <p class="hero-subtitle">Software Bill of Materials & Security Analysis</p>
                    <div class="hero-meta">
                        <span><i class="fas fa-calendar"></i> {datetime.fromisoformat(metadata.get('timestamp', datetime.now().isoformat())).strftime('%B %d, %Y at %I:%M %p')}</span>
                        <span><i class="fas fa-code"></i> {', '.join(metadata.get('technologies', ['Unknown']))}</span>
                    </div>
                </div>
                <div class="hero-visual">
                    <div class="security-badge {'secure' if stats.get('vulnerabilities', 0) == 0 else 'warning' if stats.get('vulnerabilities', 0) < 10 else 'critical'}">
                        <i class="fas {'fa-shield-alt' if stats.get('vulnerabilities', 0) == 0 else 'fa-exclamation-triangle'}"></i>
                        <span>{'SECURE' if stats.get('vulnerabilities', 0) == 0 else f"{stats.get('vulnerabilities', 0)} ISSUES"}</span>
                    </div>
                </div>
            </div>
        </section>

        <section class="metrics-section">
            <div class="metrics-grid">
                <div class="metric-card primary">
                    <div class="metric-icon"><i class="fas fa-cubes"></i></div>
                    <div class="metric-content">
                        <h3>{stats.get('total_components', 0):,}</h3>
                        <p>Total Components</p>
                        <div class="metric-trend positive"><i class="fas fa-arrow-up"></i> Analyzed</div>
                    </div>
                </div>
                <div class="metric-card success">
                    <div class="metric-icon"><i class="fas fa-link"></i></div>
                    <div class="metric-content">
                        <h3>{stats.get('direct_deps', 0)}</h3>
                        <p>Direct Dependencies</p>
                        <div class="metric-trend neutral">Immediate</div>
                    </div>
                </div>
                <div class="metric-card info">
                    <div class="metric-icon"><i class="fas fa-project-diagram"></i></div>
                    <div class="metric-content">
                        <h3>{stats.get('transitive_deps', 0)}</h3>
                        <p>Transitive Dependencies</p>
                        <div class="metric-trend neutral">Indirect</div>
                    </div>
                </div>
                {f'''
                <div class="metric-card warning">
                    <div class="metric-icon"><i class="fas fa-shield-alt"></i></div>
                    <div class="metric-content">
                        <h3>{stats.get('vulnerabilities', 0)}</h3>
                        <p>Vulnerabilities</p>
                        <div class="metric-trend {'positive' if stats.get('vulnerabilities', 0) == 0 else 'negative'}">
                            <i class="fas {'fa-check' if stats.get('vulnerabilities', 0) == 0 else 'fa-exclamation-triangle'}"></i> 
                            {'Clean' if stats.get('vulnerabilities', 0) == 0 else 'Issues Found'}
                        </div>
                    </div>
                </div>''' if 'vulnerabilities' in stats else ''}
                <div class="metric-card secondary">
                    <div class="metric-icon"><i class="fas fa-balance-scale"></i></div>
                    <div class="metric-content">
                        <h3>{license_stats.get('unique_licenses', 0)}</h3>
                        <p>Unique Licenses</p>
                        <div class="metric-trend neutral">Compliance</div>
                    </div>
                </div>
            </div>
        </section>

        {vuln_html}
        {license_html if license_stats.get('total_components', 0) > 0 else ''}

        <section id="components" class="section">
            <div class="section-header">
                <h2><i class="fas fa-cubes"></i> Component Analysis</h2>
                <p>Detailed breakdown of all software components and dependencies</p>
            </div>
            {self._generate_enhanced_component_tables(components_by_type)}
        </section>
    </main>

    <footer class="footer">
        <div class="footer-content">
            <div class="footer-brand">
                <i class="fas fa-shield-alt"></i>
                <span>Firefly SBOM Tool v1.0.0</span>
            </div>
            <div class="footer-info">
                <span>Apache License 2.0 | Generated {datetime.now().strftime('%B %Y')}</span>
            </div>
        </div>
    </footer>

    <script>
        {self._generate_single_report_scripts()}
    </script>
</body>
</html>"""

    def _generate_component_tables(self, components_by_type: Dict[str, List]) -> str:
        """Generate HTML tables for components grouped by type"""
        html = ""
        for comp_type, components in sorted(components_by_type.items()):
            html += f"""
            <div class="component-group">
                <h3>{comp_type.title()} ({len(components)})</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Version</th>
                            <th>License</th>
                            <th>Scope</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(f'''
                        <tr>
                            <td>{comp.get('name', 'Unknown')}</td>
                            <td>{comp.get('version', 'Unknown')}</td>
                            <td>{comp.get('license', 'Unknown')}</td>
                            <td><span class="badge scope-{comp.get('scope', 'unknown')}">{comp.get('scope', 'Unknown')}</span></td>
                        </tr>''' for comp in sorted(components, key=lambda x: x.get('name', '')))}
                    </tbody>
                </table>
            </div>
            """
        return html

    def _generate_org_html_report(self, org_summary: Dict[str, Any]) -> str:
        """Generate enhanced HTML content for organization summary dashboard"""
        # Process vulnerability data by severity
        vuln_stats = self._process_vulnerability_stats(org_summary)
        
        # Generate technology distribution chart data
        tech_chart_data = self._generate_tech_chart_data(org_summary.get('technology_distribution', {}))
        
        # Generate vulnerability details section
        vuln_details = self._generate_vulnerability_details_section(org_summary)
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Organization SBOM Dashboard - {org_summary.get('organization', 'Unknown')}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <style>
        {self._get_enhanced_organization_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header Section -->
        <div class="header">
            <div class="header-content">
                <h1><i class="fas fa-building"></i> {org_summary.get('organization', 'Organization')} SBOM Dashboard</h1>
                <p style="font-size: 1.25rem; opacity: 0.9; margin-bottom: 0;">Comprehensive Software Bill of Materials Analysis</p>
                
                <div class="header-meta">
                    <div class="header-meta-item">
                        <i class="fas fa-calendar-alt"></i>
                        <div class="header-meta-content">
                            <h3>Scan Date</h3>
                            <p>{datetime.fromisoformat(org_summary.get('scan_date', datetime.now().isoformat())).strftime('%B %d, %Y at %I:%M %p')}</p>
                        </div>
                    </div>
                    <div class="header-meta-item">
                        <i class="fas fa-code-branch"></i>
                        <div class="header-meta-content">
                            <h3>Repositories</h3>
                            <p>{org_summary.get('total_repositories', 0)} Total</p>
                        </div>
                    </div>
                    <div class="header-meta-item">
                        <i class="fas fa-check-circle"></i>
                        <div class="header-meta-content">
                            <h3>Success Rate</h3>
                            <p>{round((org_summary.get('successful_scans', 0) / max(org_summary.get('total_repositories', 1), 1)) * 100, 1)}%</p>
                        </div>
                    </div>
                    <div class="header-meta-item">
                        <i class="fas fa-shield-alt"></i>
                        <div class="header-meta-content">
                            <h3>Security Status</h3>
                            <p>{'Clean' if org_summary.get('total_vulnerabilities', 0) == 0 else f"{org_summary.get('total_vulnerabilities', 0)} Issues"}</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Navigation Tabs -->
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="showTab('overview')">
                <i class="fas fa-chart-pie"></i>
                Overview
            </button>
            <button class="nav-tab" onclick="showTab('repositories')">
                <i class="fas fa-folder"></i>
                Repositories ({org_summary.get('total_repositories', 0)})
            </button>
            <button class="nav-tab" onclick="showTab('security')">
                <i class="fas fa-shield-alt"></i>
                Security ({org_summary.get('total_vulnerabilities', 0)})
            </button>
            <button class="nav-tab" onclick="showTab('technologies')">
                <i class="fas fa-cogs"></i>
                Technologies ({len(org_summary.get('technology_distribution', {}))})
            </button>
        </div>
        
        <!-- Overview Tab -->
        <div id="overview-tab" class="tab-content active">
            <!-- Statistics Cards -->
            <div class="stats-grid">
                <div class="stat-card success">
                    <div class="stat-header">
                        <div class="stat-title">Successful Scans</div>
                        <div class="stat-icon"><i class="fas fa-check-circle"></i></div>
                    </div>
                    <div class="stat-value">{org_summary.get('successful_scans', 0)}</div>
                    <div class="stat-description">
                        <span class="trend-indicator trend-up">
                            <i class="fas fa-arrow-up"></i>
                            {round((org_summary.get('successful_scans', 0) / max(org_summary.get('total_repositories', 1), 1)) * 100, 1)}%
                        </span>
                        Success rate
                    </div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-title">Total Components</div>
                        <div class="stat-icon"><i class="fas fa-cubes"></i></div>
                    </div>
                    <div class="stat-value">{org_summary.get('total_components', 0):,}</div>
                    <div class="stat-description">
                        Across {org_summary.get('total_repositories', 0)} repositories
                    </div>
                </div>
                
                <div class="stat-card {'danger' if org_summary.get('vulnerability_breakdown', {}).get('critical', 0) > 0 else 'warning' if org_summary.get('total_vulnerabilities', 0) > 0 else 'success'}">
                    <div class="stat-header">
                        <div class="stat-title">Security Issues</div>
                        <div class="stat-icon"><i class="fas fa-shield-alt"></i></div>
                    </div>
                    <div class="stat-value">{org_summary.get('total_vulnerabilities', 0)}</div>
                    <div class="stat-description">
                        {'No vulnerabilities found' if org_summary.get('total_vulnerabilities', 0) == 0 else f"{vuln_stats['severity_summary']}"}
                    </div>
                </div>
                
                <div class="stat-card secondary">
                    <div class="stat-header">
                        <div class="stat-title">Technology Stack</div>
                        <div class="stat-icon"><i class="fas fa-layer-group"></i></div>
                    </div>
                    <div class="stat-value">{len(org_summary.get('technology_distribution', {}))}</div>
                    <div class="stat-description">
                        Different technologies
                    </div>
                </div>
            </div>
            
            <!-- Technology Distribution Chart -->
            <div class="content-section">
                <div class="section-header">
                    <div class="section-title">
                        <i class="fas fa-chart-doughnut"></i>
                        Technology Distribution
                    </div>
                    <div class="section-subtitle">
                        Distribution of programming languages and frameworks across repositories
                    </div>
                </div>
                <div class="section-content">
                    <div class="chart-container">
                        <canvas id="techChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Repositories Tab -->
        <div id="repositories-tab" class="tab-content">
            <div class="content-section">
                <div class="section-header">
                    <div class="section-title">
                        <i class="fas fa-folder-open"></i>
                        Repository Analysis
                    </div>
                    <div class="section-subtitle">
                        Detailed breakdown of all scanned repositories with component and vulnerability counts
                    </div>
                </div>
                <div class="section-content">
                    <!-- Filters Bar -->
                    <div class="filters-bar">
                        <div class="filter-group">
                            <label class="filter-label">Search Repositories</label>
                            <input type="text" id="repoSearch" class="filter-input" placeholder="Type repository name..." onkeyup="filterRepositories()">
                        </div>
                        <div class="filter-group">
                            <label class="filter-label">Status Filter</label>
                            <select id="statusFilter" class="filter-input" onchange="filterRepositories()">
                                <option value="all">All Status</option>
                                <option value="success">Success Only</option>
                                <option value="failed">Failed Only</option>
                            </select>
                        </div>
                        <div class="filter-group">
                            <label class="filter-label">Technology Filter</label>
                            <select id="techFilter" class="filter-input" onchange="filterRepositories()">
                                <option value="all">All Technologies</option>
                                {self._generate_tech_filter_options(org_summary.get('technology_distribution', {}))}
                            </select>
                        </div>
                    </div>
                    
                    <!-- Repository Table -->
                    <div class="table-container">
                        <table class="data-table" id="repoTable">
                            <thead>
                                <tr>
                                    <th onclick="sortTable(0)" style="cursor: pointer;">Repository <i class="fas fa-sort"></i></th>
                                    <th onclick="sortTable(1)" style="cursor: pointer;">Status</th>
                                    <th onclick="sortTable(2)" style="cursor: pointer;">Components</th>
                                    <th onclick="sortTable(3)" style="cursor: pointer;">Vulnerabilities</th>
                                    <th onclick="sortTable(4)" style="cursor: pointer;">Technologies</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join(f'''
                                <tr class="repo-row" data-status="{repo.get('status', 'unknown')}" data-tech="{','.join(repo.get('technologies', []))}">
                                    <td>
                                        <div class="repo-cell">
                                            <div class="repo-name">{repo.get('name', 'Unknown')}</div>
                                            <div class="repo-description">{(repo.get('description') or 'No description available')[:100]}{'...' if len(repo.get('description') or '') > 100 else ''}</div>
                                        </div>
                                    </td>
                                    <td>
                                        <span class="badge {'badge-success' if repo.get('status') == 'success' else 'badge-danger'}">
                                            <i class="fas {'fa-check' if repo.get('status') == 'success' else 'fa-times'}"></i>
                                            {repo.get('status', 'Unknown').title()}
                                        </span>
                                    </td>
                                    <td><strong>{repo.get('components', 0):,}</strong></td>
                                    <td>
                                        <div>
                                            <span style="color: {'var(--danger-red)' if repo.get('vulnerabilities', 0) > 0 else 'var(--success-green)'}; font-weight: 600;">
                                                {repo.get('vulnerabilities', 0):,} Total
                                            </span>
                                        </div>
                                        <div style="margin-top: 0.25rem; display: flex; gap: 0.5rem; flex-wrap: wrap;">
                                            {self._generate_repo_vulnerability_badges(repo.get('vulnerability_breakdown', {}))}
                                        </div>
                                    </td>
                                    <td>
                                        <div class="tech-badges">
                                            {self._generate_tech_badges(repo.get('technologies', []))}
                                        </div>
                                    </td>
                                    <td>
                                        <div style="display: flex; gap: 0.5rem;">
                                            <button onclick="viewDetails('{repo.get('name', '')}')" style="padding: 0.5rem 1rem; background: var(--primary-blue); color: white; border: none; border-radius: var(--border-radius-sm); cursor: pointer; font-size: 0.875rem; display: flex; align-items: center; gap: 0.25rem;">
                                                <i class="fas fa-eye"></i> View
                                            </button>
                                        </div>
                                    </td>
                                </tr>''' for repo in org_summary.get('repositories', []))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Security Tab -->
        <div id="security-tab" class="tab-content">
            {vuln_details}
        </div>
        
        <!-- Technologies Tab -->
        <div id="technologies-tab" class="tab-content">
            <div class="content-section">
                <div class="section-header">
                    <div class="section-title">
                        <i class="fas fa-code"></i>
                        Technology Stack Analysis
                    </div>
                    <div class="section-subtitle">
                        Overview of programming languages, frameworks, and build tools used across all repositories
                    </div>
                </div>
                <div class="section-content">
                    <div class="chart-container">
                        <canvas id="techDetailsChart"></canvas>
                    </div>
                    <div style="margin-top: 2rem;">
                        <h3 style="margin-bottom: 1rem; color: var(--gray-800);">Technology Breakdown</h3>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
                            {self._generate_tech_breakdown_cards(org_summary.get('technology_distribution', {}))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <div class="footer-content">
                <p>Generated by <span class="footer-brand">Firefly SBOM Tool v1.0.0</span></p>
                <p>Apache License 2.0 | Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>
        </div>
    </div>
    
    <script>
        {self._generate_enhanced_interactive_scripts(tech_chart_data, org_summary)}
    </script>
</body>
</html>"""

    def _get_css_styles(self) -> str:
        """Get CSS styles for HTML reports"""
        return """
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        header { background: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; margin-bottom: 20px; }
        h2 { color: #34495e; margin: 30px 0 20px; }
        h3 { color: #546e7a; margin: 20px 0 10px; }
        .metadata p { margin: 5px 0; color: #666; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }
        .stat-card { background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .stat-card h3 { font-size: 14px; color: #666; margin-bottom: 10px; }
        .stat-number { font-size: 32px; font-weight: bold; color: #2c3e50; }
        .stat-card.warning .stat-number { color: #e74c3c; }
        table { width: 100%; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin: 20px 0; }
        th { background: #34495e; color: white; padding: 12px; text-align: left; font-weight: 600; }
        td { padding: 12px; border-top: 1px solid #ecf0f1; }
        tr:hover { background: #f8f9fa; }
        .badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; text-transform: uppercase; }
        .badge.scope-direct { background: #3498db; color: white; }
        .badge.scope-transitive { background: #95a5a6; color: white; }
        .badge.scope-dev { background: #9b59b6; color: white; }
        .badge.status-success { background: #27ae60; color: white; }
        .badge.status-failed { background: #e74c3c; color: white; }
        .badge.severity-critical { background: #c0392b; color: white; }
        .badge.severity-high { background: #e74c3c; color: white; }
        .badge.severity-medium { background: #f39c12; color: white; }
        .badge.severity-low { background: #3498db; color: white; }
        footer { text-align: center; margin-top: 50px; padding: 20px; color: #666; }
        .vulnerabilities { background: white; padding: 30px; border-radius: 10px; margin: 30px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .component-group { margin: 20px 0; }
        """
    
    def _get_enhanced_css_styles(self) -> str:
        """Get enhanced CSS styles with navigation and interactivity"""
        return """
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; background: #f8f9fd; display: flex; }
        
        /* Sidebar Navigation */
        .sidebar { width: 280px; height: 100vh; background: #2c3e50; color: white; position: fixed; left: 0; top: 0; padding: 20px; box-shadow: 2px 0 10px rgba(0,0,0,0.1); z-index: 1000; overflow-y: auto; }
        .sidebar .logo { text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #34495e; }
        .sidebar .logo h3 { color: #ecf0f1; font-size: 18px; }
        .nav-menu { list-style: none; }
        .nav-menu li { margin: 10px 0; }
        .nav-menu a { color: #bdc3c7; text-decoration: none; padding: 12px 15px; display: block; border-radius: 6px; transition: all 0.3s ease; }
        .nav-menu a:hover, .nav-menu a.active { background: #34495e; color: #3498db; transform: translateX(5px); }
        
        /* Main Content */
        .main-content { margin-left: 280px; flex: 1; padding: 20px; min-height: 100vh; }
        
        /* Header */
        header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 15px; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
        h1 { font-size: 36px; margin-bottom: 20px; font-weight: 300; }
        .metadata { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }
        .metadata p { background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; margin: 5px 0; backdrop-filter: blur(10px); }
        
        /* Statistics Cards */
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 25px; margin: 40px 0; }
        .stat-card { background: white; padding: 30px; border-radius: 15px; text-align: center; box-shadow: 0 8px 25px rgba(0,0,0,0.1); border-left: 5px solid #3498db; transition: transform 0.3s ease; }
        .stat-card:hover { transform: translateY(-5px); }
        .stat-card.warning { border-left-color: #e74c3c; }
        .stat-card.info { border-left-color: #9b59b6; }
        .stat-card h3 { font-size: 14px; color: #666; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px; }
        .stat-number { font-size: 42px; font-weight: 700; color: #2c3e50; margin: 10px 0; }
        .stat-change { font-size: 13px; color: #7f8c8d; }
        .stat-card.warning .stat-number { color: #e74c3c; }
        .stat-card.info .stat-number { color: #9b59b6; }
        
        /* Sections */
        .section { background: white; margin: 30px 0; padding: 30px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); }
        h2 { color: #2c3e50; margin-bottom: 25px; font-size: 24px; display: flex; align-items: center; }
        h2::before { content: ''; width: 4px; height: 30px; background: #3498db; margin-right: 15px; border-radius: 2px; }
        
        /* Charts */
        .chart-container { max-width: 600px; margin: 20px auto; padding: 20px; }
        
        /* Search and Filters */
        .search-box { display: flex; gap: 15px; margin-bottom: 25px; flex-wrap: wrap; }
        .search-box input, .search-box select { padding: 12px 16px; border: 2px solid #ecf0f1; border-radius: 8px; font-size: 14px; flex: 1; min-width: 200px; }
        .search-box input:focus, .search-box select:focus { outline: none; border-color: #3498db; }
        
        /* Tables */
        .table-container { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 16px 12px; text-align: left; font-weight: 600; cursor: pointer; position: relative; }
        th:hover { background: linear-gradient(135deg, #5a67d8 0%, #667eea 100%); }
        td { padding: 16px 12px; border-top: 1px solid #ecf0f1; vertical-align: middle; }
        tr:hover { background: #f8f9ff; }
        tr.hidden { display: none; }
        
        /* Repository Names */
        .repo-name strong { color: #2c3e50; font-size: 16px; }
        .repo-meta { color: #7f8c8d; font-size: 12px; margin-top: 4px; }
        
        /* Badges */
        .badge { display: inline-block; padding: 6px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; text-transform: uppercase; margin: 2px; }
        .badge.status-success { background: #27ae60; color: white; }
        .badge.status-failed { background: #e74c3c; color: white; }
        .tech-badges { display: flex; flex-wrap: wrap; gap: 4px; }
        .tech-badge { background: #3498db; color: white; padding: 4px 8px; border-radius: 12px; font-size: 10px; }
        .tech-badge.java { background: #f89820; }
        .tech-badge.python { background: #3776ab; }
        .tech-badge.javascript { background: #f7df1e; color: #000; }
        .tech-badge.typescript { background: #3178c6; }
        .tech-badge.go { background: #00add8; }
        .tech-badge.rust { background: #000000; }
        .tech-badge.ruby { background: #cc342d; }
        
        /* Buttons */
        .action-buttons { display: flex; gap: 8px; }
        .btn-primary, .btn-secondary { padding: 6px 12px; border: none; border-radius: 6px; font-size: 12px; cursor: pointer; transition: all 0.3s ease; }
        .btn-primary { background: #3498db; color: white; }
        .btn-primary:hover { background: #2980b9; }
        .btn-secondary { background: #95a5a6; color: white; }
        .btn-secondary:hover { background: #7f8c8d; }
        .btn-sm { padding: 4px 8px; font-size: 11px; }
        
        /* Numbers */
        .number { font-weight: 600; }
        .text-danger { color: #e74c3c; }
        .text-success { color: #27ae60; }
        
        /* Vulnerabilities */
        .vulnerability-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }
        .vuln-card { padding: 20px; border-radius: 10px; border-left: 4px solid; }
        .vuln-card.critical { border-left-color: #c0392b; background: #fdf2f2; }
        .vuln-card.high { border-left-color: #e74c3c; background: #fef5f5; }
        .vuln-card.medium { border-left-color: #f39c12; background: #fefcf3; }
        .vuln-card.low { border-left-color: #3498db; background: #f0f8ff; }
        .vuln-title { font-weight: 600; margin-bottom: 8px; }
        .vuln-component { color: #666; font-size: 14px; }
        .vuln-description { margin-top: 10px; font-size: 13px; line-height: 1.4; }
        
        /* Footer */
        footer { text-align: center; margin-top: 60px; padding: 30px; color: #7f8c8d; background: #ecf0f1; border-radius: 10px; }
        
        /* Responsive */
        @media (max-width: 768px) {
            .sidebar { width: 100%; height: auto; position: relative; }
            .main-content { margin-left: 0; }
            .stats { grid-template-columns: 1fr; }
            .search-box { flex-direction: column; }
        }
        
        /* Progress indicators */
        .progress-bar { width: 100%; height: 4px; background: #ecf0f1; border-radius: 2px; overflow: hidden; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #3498db, #2ecc71); transition: width 0.3s ease; }
        
        /* Animations */
        @keyframes slideIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        .section { animation: slideIn 0.6s ease-out; }
        """
    
    def _process_vulnerability_stats(self, org_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Process vulnerability statistics for display"""
        total_vulns = org_summary.get('total_vulnerabilities', 0)
        
        # Get actual vulnerability breakdown from organization data
        vuln_breakdown = org_summary.get('vulnerability_breakdown', {
            'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'unknown': 0
        })
        severity_counts = {
            'critical': vuln_breakdown.get('critical', 0),
            'high': vuln_breakdown.get('high', 0),
            'medium': vuln_breakdown.get('medium', 0),
            'low': vuln_breakdown.get('low', 0),
            'unknown': vuln_breakdown.get('unknown', 0)
        }
        
        # Generate summary text
        if total_vulns == 0:
            severity_summary = "No vulnerabilities found"
        else:
            severity_summary = f"{severity_counts.get('critical', 0)} Critical, {severity_counts.get('high', 0)} High"
        
        return {
            'total': total_vulns,
            'by_severity': severity_counts,
            'severity_summary': severity_summary
        }
    
    def _generate_navigation_menu(self, org_summary: Dict[str, Any]) -> str:
        """Generate navigation menu for sidebar"""
        return f"""
        <ul class="nav-menu">
            <li><a href="#overview" class="active">📊 Overview</a></li>
            <li><a href="#technologies">⚙️ Technologies</a></li>
            <li><a href="#vulnerabilities">🔒 Security ({org_summary.get('total_vulnerabilities', 0)})</a></li>
            <li><a href="#repositories">📂 Repositories ({org_summary.get('total_repositories', 0)})</a></li>
            <li><a href="#" onclick="exportData()">💾 Export Data</a></li>
            <li><a href="#" onclick="printReport()">🖨️ Print Report</a></li>
        </ul>
        """
    
    def _generate_tech_chart_data(self, tech_distribution: Dict[str, int]) -> str:
        """Generate Chart.js data for technology distribution"""
        if not tech_distribution:
            return '{}'
        
        labels = list(tech_distribution.keys())
        data = list(tech_distribution.values())
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#34495e', '#e67e22']
        
        return json.dumps({
            'labels': labels,
            'datasets': [{
                'data': data,
                'backgroundColor': colors[:len(labels)],
                'borderWidth': 0
            }]
        })
    
    def _generate_vulnerability_details_section(self, org_summary: Dict[str, Any]) -> str:
        """Generate detailed vulnerability section with accurate breakdown"""
        total_vulns = org_summary.get('total_vulnerabilities', 0)
        vuln_breakdown = org_summary.get('vulnerability_breakdown', {
            'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'unknown': 0
        })
        
        if total_vulns == 0:
            return f"""
            <div class="content-section">
                <div class="section-header">
                    <div class="section-title">
                        <i class="fas fa-shield-alt"></i>
                        Security Vulnerabilities
                    </div>
                    <div class="section-subtitle">
                        Comprehensive security analysis across all scanned repositories
                    </div>
                </div>
                <div class="section-content">
                    <div style="text-align: center; padding: 3rem; color: var(--success-green);">
                        <div style="font-size: 4rem; margin-bottom: 1rem;">
                            <i class="fas fa-shield-check"></i>
                        </div>
                        <h3 style="color: var(--success-green); margin-bottom: 1rem;">🎉 Excellent Security Posture!</h3>
                        <p style="color: var(--gray-600); font-size: 1.125rem;">No vulnerabilities detected across all {org_summary.get('successful_scans', 0)} scanned repositories.</p>
                    </div>
                </div>
            </div>
            """
        
        # Create detailed breakdown section with accurate counts
        return f"""
        <div class="content-section">
            <div class="section-header">
                <div class="section-title">
                    <i class="fas fa-exclamation-triangle"></i>
                    Security Vulnerabilities ({total_vulns} total)
                </div>
                <div class="section-subtitle">
                    Security vulnerability analysis across {org_summary.get('successful_scans', 0)} repositories
                </div>
            </div>
            <div class="section-content">
                <!-- Severity Breakdown Cards -->
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
                    <div class="stat-card danger">
                        <div class="stat-header">
                            <div class="stat-title">Critical</div>
                            <div class="stat-icon" style="background: var(--danger-red);"><i class="fas fa-skull-crossbones"></i></div>
                        </div>
                        <div class="stat-value">{vuln_breakdown.get('critical', 0)}</div>
                        <div class="stat-description">
                            <span style="color: var(--danger-red); font-weight: 600;">⚠️ Immediate action required</span>
                        </div>
                    </div>
                    <div class="stat-card warning">
                        <div class="stat-header">
                            <div class="stat-title">High</div>
                            <div class="stat-icon" style="background: var(--warning-amber);"><i class="fas fa-exclamation-triangle"></i></div>
                        </div>
                        <div class="stat-value">{vuln_breakdown.get('high', 0)}</div>
                        <div class="stat-description">
                            <span style="color: var(--warning-amber); font-weight: 600;">⚡ Address promptly</span>
                        </div>
                    </div>
                    <div class="stat-card" style="--stat-color: #fbbf24;">
                        <div class="stat-header">
                            <div class="stat-title">Medium</div>
                            <div class="stat-icon" style="background: #fbbf24;"><i class="fas fa-exclamation-circle"></i></div>
                        </div>
                        <div class="stat-value">{vuln_breakdown.get('medium', 0)}</div>
                        <div class="stat-description">
                            <span style="color: #fbbf24; font-weight: 600;">📋 Plan to address</span>
                        </div>
                    </div>
                    <div class="stat-card" style="--stat-color: #60a5fa;">
                        <div class="stat-header">
                            <div class="stat-title">Low</div>
                            <div class="stat-icon" style="background: #60a5fa;"><i class="fas fa-info-circle"></i></div>
                        </div>
                        <div class="stat-value">{vuln_breakdown.get('low', 0)}</div>
                        <div class="stat-description">
                            <span style="color: #60a5fa; font-weight: 600;">ℹ️ Review when convenient</span>
                        </div>
                    </div>
                    <div class="stat-card secondary">
                        <div class="stat-header">
                            <div class="stat-title">Unknown</div>
                            <div class="stat-icon"><i class="fas fa-question-circle"></i></div>
                        </div>
                        <div class="stat-value">{vuln_breakdown.get('unknown', 0)}</div>
                        <div class="stat-description">
                            <span style="color: var(--gray-600); font-weight: 600;">❓ Needs analysis</span>
                        </div>
                    </div>
                </div>
                
                <!-- Risk Assessment -->
                <div style="background: {'#fef2f2' if vuln_breakdown.get('critical', 0) > 0 else '#fef3c7' if vuln_breakdown.get('high', 0) > 0 else '#f0f9ff'}; border: 1px solid {'#fecaca' if vuln_breakdown.get('critical', 0) > 0 else '#fed7aa' if vuln_breakdown.get('high', 0) > 0 else '#bae6fd'}; border-radius: var(--border-radius); padding: 1.5rem; margin-bottom: 2rem;">
                    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                        <div style="font-size: 1.5rem; color: {'#dc2626' if vuln_breakdown.get('critical', 0) > 0 else '#d97706' if vuln_breakdown.get('high', 0) > 0 else '#0284c7'};">
                            <i class="fas {'fa-times-circle' if vuln_breakdown.get('critical', 0) > 0 else 'fa-exclamation-triangle' if vuln_breakdown.get('high', 0) > 0 else 'fa-info-circle'}"></i>
                        </div>
                        <h3 style="margin: 0; color: {'#dc2626' if vuln_breakdown.get('critical', 0) > 0 else '#d97706' if vuln_breakdown.get('high', 0) > 0 else '#0284c7'}; font-size: 1.25rem;">
                            {'CRITICAL RISK: Immediate Action Required' if vuln_breakdown.get('critical', 0) > 0 else 'HIGH RISK: Address Promptly' if vuln_breakdown.get('high', 0) > 0 else 'MODERATE RISK: Plan Remediation'}
                        </h3>
                    </div>
                    <div style="color: var(--gray-700); line-height: 1.6;">
                        {self._create_security_summary(vuln_breakdown, total_vulns, org_summary.get('successful_scans', 0))}
                    </div>
                </div>
                
                <!-- Action Items -->
                <div style="background: var(--gray-50); border-radius: var(--border-radius); padding: 1.5rem; margin-bottom: 2rem;">
                    <h4 style="margin: 0 0 1rem 0; color: var(--gray-800); display: flex; align-items: center; gap: 0.5rem;">
                        <i class="fas fa-tasks"></i>
                        Recommended Actions
                    </h4>
                    <ul style="margin: 0; padding-left: 1.5rem; color: var(--gray-700);">
                        <li style="margin-bottom: 0.5rem;"><strong>Immediate:</strong> Review and patch critical and high severity vulnerabilities</li>
                        <li style="margin-bottom: 0.5rem;"><strong>Short-term:</strong> Implement automated vulnerability scanning in CI/CD pipelines</li>
                        <li style="margin-bottom: 0.5rem;"><strong>Long-term:</strong> Establish regular security reviews and dependency updates</li>
                        <li><strong>Monitoring:</strong> Set up alerts for new vulnerabilities in production dependencies</li>
                    </ul>
                    <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--gray-200); font-size: 0.875rem; color: var(--gray-600);">
                        💡 Use filters above to narrow down vulnerabilities by repository, severity, or component name
                    </div>
                </div>
                
        <!-- Comprehensive Vulnerability List -->
        {self._generate_comprehensive_vulnerability_list(org_summary)}
        
        <!-- Vulnerability Filtering Controls -->
        {self._generate_vulnerability_filter_controls()}
    </div>
        </div>
        """
    
    def _generate_tech_filter_options(self, tech_distribution: Dict[str, int]) -> str:
        """Generate technology filter options"""
        options = []
        for tech in sorted(tech_distribution.keys()):
            options.append(f'<option value="{tech}">{tech} ({tech_distribution[tech]})</option>')
        return '\n'.join(options)
    
    def _generate_tech_badges(self, technologies: List[str]) -> str:
        """Generate technology badges with colors"""
        badges = []
        for tech in technologies:
            css_class = tech.lower().replace('/', '').replace(' ', '').replace('.', '')
            badges.append(f'<span class="tech-badge {css_class}">{tech}</span>')
        return '\n'.join(badges)
    
    def _generate_repo_vulnerability_badges(self, vulnerability_breakdown: Dict[str, int]) -> str:
        """Generate vulnerability severity badges for repository table"""
        if not vulnerability_breakdown:
            return '<span style="color: var(--gray-500); font-size: 0.75rem;">No breakdown available</span>'
        
        badges = []
        severity_config = {
            'critical': {'color': '#dc2626', 'label': 'C'},
            'high': {'color': '#ea580c', 'label': 'H'},
            'medium': {'color': '#d97706', 'label': 'M'},
            'low': {'color': '#0284c7', 'label': 'L'},
            'unknown': {'color': '#6b7280', 'label': 'U'}
        }
        
        for severity, count in vulnerability_breakdown.items():
            if count > 0:
                config = severity_config.get(severity, {'color': '#6b7280', 'label': severity[:1].upper()})
                badges.append(f'''
                <span style="
                    display: inline-flex;
                    align-items: center;
                    padding: 0.125rem 0.375rem;
                    background: {config['color']};
                    color: white;
                    border-radius: 4px;
                    font-size: 0.625rem;
                    font-weight: 600;
                    line-height: 1;
                ">{config['label']}: {count}</span>
                ''')
        
        return ''.join(badges) if badges else '<span style="color: var(--success-green); font-size: 0.75rem;">✅ Clean</span>'
    
    def _generate_interactive_scripts(self, tech_chart_data: str, org_summary: Dict[str, Any]) -> str:
        """Generate JavaScript for interactivity"""
        org_summary_json = json.dumps(org_summary, default=str)
        
        return """
        // Technology Chart
        const ctx = document.getElementById('techChart').getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: """ + tech_chart_data + """,
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'right'
                    }
                }
            }
        });
        
        // Repository filtering
        function filterRepositories() {
            const search = document.getElementById('repoSearch').value.toLowerCase();
            const statusFilter = document.getElementById('statusFilter').value;
            const techFilter = document.getElementById('techFilter').value;
            const rows = document.querySelectorAll('#repoTable tbody tr');
            
            rows.forEach(function(row) {
                const name = row.cells[0].textContent.toLowerCase();
                const status = row.dataset.status;
                const tech = row.dataset.tech;
                
                let visible = true;
                
                if (search && !name.includes(search)) visible = false;
                if (statusFilter !== 'all' && status !== statusFilter) visible = false;
                if (techFilter !== 'all' && !tech.includes(techFilter)) visible = false;
                
                row.classList.toggle('hidden', !visible);
            });
        }
        
        // Table sorting
        let sortDirection = {};
        function sortTable(columnIndex) {
            const table = document.getElementById('repoTable');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr:not(.hidden)'));
            
            const direction = sortDirection[columnIndex] = !sortDirection[columnIndex];
            
            rows.sort(function(a, b) {
                const aVal = a.cells[columnIndex].textContent.trim();
                const bVal = b.cells[columnIndex].textContent.trim();
                
                if (columnIndex === 2 || columnIndex === 3) {
                    // Numeric columns
                    return direction ? parseInt(bVal.replace(/,/g, '')) - parseInt(aVal.replace(/,/g, '')) : parseInt(aVal.replace(/,/g, '')) - parseInt(bVal.replace(/,/g, ''));
                } else {
                    // Text columns
                    return direction ? bVal.localeCompare(aVal) : aVal.localeCompare(bVal);
                }
            });
            
            rows.forEach(function(row) { tbody.appendChild(row); });
        }
        
        // Navigation
        document.querySelectorAll('.nav-menu a').forEach(function(link) {
            link.addEventListener('click', function(e) {
                if (this.getAttribute('href').startsWith('#')) {
                    e.preventDefault();
                    document.querySelectorAll('.nav-menu a').forEach(function(l) { l.classList.remove('active'); });
                    this.classList.add('active');
                    const target = document.querySelector(this.getAttribute('href'));
                    if (target) target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
        
        // Action buttons
        function viewDetails(repoName) {
            window.open(repoName + '/sbom.html', '_blank');
        }
        
        function downloadSBOM(repoName) {
            window.open(repoName + '/sbom.cyclonedx.json', '_blank');
        }
        
        function exportData() {
            const data = """ + org_summary_json + """;
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'organization-sbom-summary.json';
            a.click();
        }
        
        function printReport() {
            window.print();
        }
        
        // Initialize tooltips and smooth scrolling
        document.addEventListener('DOMContentLoaded', function() {
            // Add loading animation
            setTimeout(function() {
                document.body.style.opacity = '1';
            }, 100);
        });
        """
    
    def _categorize_vulnerabilities(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, List]:
        """Categorize vulnerabilities by severity"""
        categories = {'critical': [], 'high': [], 'medium': [], 'low': [], 'unknown': []}
        
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'unknown').lower()
            if severity in categories:
                categories[severity].append(vuln)
            else:
                categories['unknown'].append(vuln)
        
        return categories
    
    def _analyze_licenses(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze license distribution in components"""
        license_counts = {}
        total_components = len(components)
        
        for comp in components:
            license_name = comp.get('license', 'Unknown')
            license_counts[license_name] = license_counts.get(license_name, 0) + 1
        
        # Sort by count, descending
        sorted_licenses = sorted(license_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'total_components': total_components,
            'license_counts': license_counts,
            'sorted_licenses': sorted_licenses,
            'unique_licenses': len(license_counts)
        }
    
    def _generate_vulnerability_section(self, vulnerabilities: List[Dict[str, Any]], vuln_by_severity: Dict[str, List]) -> str:
        """Generate comprehensive vulnerability section with categorization"""
        if not vulnerabilities:
            return ""
        
        # Generate severity summary cards
        severity_cards = ""
        severity_colors = {
            'critical': '#c0392b',
            'high': '#e74c3c', 
            'medium': '#f39c12',
            'low': '#3498db',
            'unknown': '#95a5a6'
        }
        
        for severity, color in severity_colors.items():
            count = len(vuln_by_severity.get(severity, []))
            severity_cards += f"""
            <div class="vuln-summary-card" style="border-left: 4px solid {color}; background: {'#fdf2f2' if severity == 'critical' else '#fef5f5' if severity == 'high' else '#fefcf3' if severity == 'medium' else '#f0f8ff' if severity == 'low' else '#f8f9fa'}; padding: 15px; margin: 10px; border-radius: 8px;">
                <h4 style="color: {color}; margin: 0 0 5px 0; text-transform: capitalize;">{severity.replace('_', ' ')} ({count})</h4>
                <div style="font-size: 24px; font-weight: bold; color: {color};">{count}</div>
            </div>"""
        
        # Generate detailed vulnerability table
        vuln_table_rows = ""
        for vuln in sorted(vulnerabilities, key=lambda x: {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'unknown': 4}.get(x.get('severity', 'unknown'), 4)):
            severity = vuln.get('severity', 'unknown')
            cvss_score = vuln.get('cvss_score', '')
            cvss_display = f" (CVSS: {cvss_score})" if cvss_score else ""
            
            # Handle references separately to avoid nested f-string issues
            references_html = ""
            if vuln.get('references'):
                ref_links = []
                for ref in vuln.get('references', [])[:3]:
                    ref_links.append(f'<a href="{ref}" target="_blank" style="font-size: 11px;">🔗</a>')
                references_html = f'<div style="margin-top: 5px;"><strong>References:</strong> {" ".join(ref_links)}</div>'
            
            description_text = vuln.get('description', '')[:200]
            description_suffix = '...' if len(vuln.get('description', '')) > 200 else ''
            
            vuln_table_rows += f"""
            <tr class="severity-{severity}">
                <td><strong>{vuln.get('component', 'Unknown')}</strong><br><small style="color: #666;">{vuln.get('component_version', '')}</small></td>
                <td><code>{vuln.get('id', 'Unknown')}</code></td>
                <td><span class="badge severity-{severity}">{severity.upper()}{cvss_display}</span></td>
                <td style="max-width: 300px;">
                    <div><strong>{vuln.get('title', vuln.get('description', '')[:100])}</strong></div>
                    <div style="font-size: 12px; color: #666; margin-top: 5px;">{description_text}{description_suffix}</div>
                    {references_html}
                </td>
                <td style="font-size: 12px; color: #666;">{vuln.get('published', '')[:10] if vuln.get('published') else 'N/A'}</td>
            </tr>"""
        
        return f"""
        <div class="vulnerabilities section" id="vulnerabilities">
            <h2>🔒 Security Vulnerabilities ({len(vulnerabilities)})</h2>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0;">
                {severity_cards}
            </div>
            
            <div class="vulnerability-details" style="margin-top: 30px;">
                <h3>Vulnerability Details</h3>
                <div style="overflow-x: auto;">
                    <table style="width: 100%; margin: 0;">
                        <thead>
                            <tr>
                                <th style="min-width: 150px;">Component</th>
                                <th style="min-width: 120px;">Vulnerability ID</th>
                                <th style="min-width: 100px;">Severity</th>
                                <th style="min-width: 300px;">Description & References</th>
                                <th style="min-width: 100px;">Published</th>
                            </tr>
                        </thead>
                        <tbody>
                            {vuln_table_rows}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div style="margin-top: 30px; padding: 15px; background: #f8f9fa; border-radius: 8px; font-size: 14px; color: #666;">
                <h4 style="color: #333; margin: 0 0 10px 0;">📋 Vulnerability Assessment Summary</h4>
                <p><strong>Critical:</strong> Immediate action required - these vulnerabilities allow remote code execution or system compromise.</p>
                <p><strong>High:</strong> Should be addressed promptly - these vulnerabilities may allow privilege escalation or data access.</p>
                <p><strong>Medium:</strong> Plan to address - these vulnerabilities may allow limited access or information disclosure.</p>
                <p><strong>Low:</strong> Review when convenient - these are typically minor issues or require specific conditions to exploit.</p>
            </div>
        </div>
        """
    
    def _generate_license_section(self, license_stats: Dict[str, Any]) -> str:
        """Generate license analysis section"""
        if license_stats['total_components'] == 0:
            return ""
        
        # Generate license distribution chart data
        license_chart_rows = ""
        for license_name, count in license_stats['sorted_licenses'][:10]:  # Top 10 licenses
            percentage = (count / license_stats['total_components']) * 100
            license_chart_rows += f"""
            <tr>
                <td><strong>{license_name}</strong></td>
                <td style="text-align: center;">{count}</td>
                <td style="text-align: center;">{percentage:.1f}%</td>
                <td>
                    <div style="width: 100%; background: #ecf0f1; border-radius: 10px; height: 20px;">
                        <div style="width: {min(percentage, 100)}%; background: #3498db; height: 100%; border-radius: 10px; transition: width 0.3s ease;"></div>
                    </div>
                </td>
                <td style="font-size: 12px; color: #666;">
                    {self._get_license_risk_indicator(license_name)}
                </td>
            </tr>"""
        
        return f"""
        <div class="license-analysis section" id="licenses">
            <h2>⚖️ License Analysis ({license_stats['unique_licenses']} unique licenses)</h2>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0;">
                <div style="background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h3 style="color: #666; font-size: 14px; margin-bottom: 10px;">Total Components</h3>
                    <div style="font-size: 32px; font-weight: bold; color: #2c3e50;">{license_stats['total_components']}</div>
                </div>
                <div style="background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h3 style="color: #666; font-size: 14px; margin-bottom: 10px;">Unique Licenses</h3>
                    <div style="font-size: 32px; font-weight: bold; color: #9b59b6;">{license_stats['unique_licenses']}</div>
                </div>
                <div style="background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h3 style="color: #666; font-size: 14px; margin-bottom: 10px;">Most Common</h3>
                    <div style="font-size: 16px; font-weight: bold; color: #34495e;">{license_stats['sorted_licenses'][0][0] if license_stats['sorted_licenses'] else 'N/A'}</div>
                    <div style="font-size: 12px; color: #666;">({license_stats['sorted_licenses'][0][1] if license_stats['sorted_licenses'] else 0} components)</div>
                </div>
            </div>
            
            <div style="margin-top: 30px;">
                <h3>License Distribution</h3>
                <div style="overflow-x: auto;">
                    <table style="width: 100%; margin: 0;">
                        <thead>
                            <tr>
                                <th>License</th>
                                <th style="text-align: center;">Components</th>
                                <th style="text-align: center;">Percentage</th>
                                <th style="text-align: center;">Distribution</th>
                                <th style="text-align: center;">Risk Level</th>
                            </tr>
                        </thead>
                        <tbody>
                            {license_chart_rows}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div style="margin-top: 30px; padding: 15px; background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; font-size: 14px;">
                <h4 style="color: #856404; margin: 0 0 10px 0;">⚠️ License Compliance Notes</h4>
                <p><strong>Always consult with your legal team</strong> before using components with restrictive licenses.</p>
                <p><strong>Unknown licenses</strong> require manual review to determine compliance requirements.</p>
                <p><strong>Copyleft licenses</strong> (GPL, LGPL) may require source code disclosure under certain conditions.</p>
            </div>
        </div>
        """
    
    def _get_license_risk_indicator(self, license_name: str) -> str:
        """Get risk level indicator for a license"""
        license_name = license_name.lower()
        
        # High risk (copyleft)
        if any(term in license_name for term in ['gpl', 'agpl', 'copyleft']):
            return '<span style="color: #e74c3c; font-weight: bold;">⚠️ High</span>'
        
        # Medium risk (some restrictions)
        elif any(term in license_name for term in ['lgpl', 'mpl', 'cddl', 'epl']):
            return '<span style="color: #f39c12; font-weight: bold;">⚡ Medium</span>'
        
        # Low risk (permissive)
        elif any(term in license_name for term in ['mit', 'apache', 'bsd', 'isc']):
            return '<span style="color: #27ae60; font-weight: bold;">✅ Low</span>'
        
        # Unknown
        elif 'unknown' in license_name:
            return '<span style="color: #95a5a6; font-weight: bold;">❓ Unknown</span>'
        
        else:
            return '<span style="color: #95a5a6; font-weight: bold;">📋 Review</span>'
    
    def _create_security_summary(self, vuln_breakdown: Dict[str, int], total_vulnerabilities: int, successful_scans: int) -> str:
        """Create comprehensive security summary with vulnerability breakdown"""
        if total_vulnerabilities == 0:
            return f"No vulnerabilities detected in {successful_scans} scanned repositories"
        
        # Create breakdown text with color-coded badges
        severity_parts = []
        severity_colors = {
            'critical': '#dc3545',
            'high': '#fd7e14',
            'medium': '#ffc107',
            'low': '#28a745',
            'unknown': '#6c757d'
        }
        
        for severity, count in vuln_breakdown.items():
            if count > 0:
                color = severity_colors.get(severity, '#6c757d')
                severity_parts.append(f"<span style='color: {color}; font-weight: bold;'>{count} {severity.title()}</span>")
        
        summary = f"Found {total_vulnerabilities} vulnerabilities across {successful_scans} repositories: " + ", ".join(severity_parts)
        
        # Add risk assessment
        if vuln_breakdown.get('critical', 0) > 0:
            summary += f"<br><span style='color: #dc3545; font-weight: bold;'>⚠️ CRITICAL: Immediate action required</span>"
        elif vuln_breakdown.get('high', 0) > 0:
            summary += f"<br><span style='color: #fd7e14; font-weight: bold;'>⚡ HIGH: Address promptly</span>"
        elif vuln_breakdown.get('medium', 0) > 0:
            summary += f"<br><span style='color: #ffc107; font-weight: bold;'>📋 MEDIUM: Plan to address</span>"
        else:
            summary += f"<br><span style='color: #28a745; font-weight: bold;'>✅ LOW: Review when convenient</span>"
        
        return summary
    
    def _get_enhanced_organization_css_styles(self) -> str:
        """Get enhanced CSS styles for organization dashboard HTML"""
        return """
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        :root {
            --primary-blue: #3b82f6;
            --primary-dark: #1e40af;
            --secondary-indigo: #6366f1;
            --success-green: #10b981;
            --warning-amber: #f59e0b;
            --danger-red: #ef4444;
            --gray-50: #f8fafc;
            --gray-100: #f1f5f9;
            --gray-200: #e2e8f0;
            --gray-300: #cbd5e1;
            --gray-400: #94a3b8;
            --gray-500: #64748b;
            --gray-600: #475569;
            --gray-700: #334155;
            --gray-800: #1e293b;
            --gray-900: #0f172a;
            --white: #ffffff;
            --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
            --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
            --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
            --border-radius: 12px;
            --border-radius-sm: 6px;
            --border-radius-lg: 16px;
            --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: var(--gray-800);
            background: linear-gradient(135deg, var(--gray-50) 0%, var(--gray-100) 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        /* Header Styles */
        .header {
            background: linear-gradient(135deg, var(--primary-blue) 0%, var(--secondary-indigo) 100%);
            color: var(--white);
            padding: 3rem 2rem;
            border-radius: var(--border-radius-lg);
            margin-bottom: 3rem;
            box-shadow: var(--shadow-xl);
            position: relative;
            overflow: hidden;
        }
        
        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="%23ffffff" fill-opacity="0.05"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>') repeat;
            opacity: 0.1;
        }
        
        .header-content {
            position: relative;
            z-index: 1;
        }
        
        .header h1 {
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .header h1 i {
            font-size: 2.5rem;
            opacity: 0.9;
        }
        
        .header-meta {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }
        
        .header-meta-item {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 1.5rem;
            border-radius: var(--border-radius);
            display: flex;
            align-items: center;
            gap: 1rem;
            transition: var(--transition);
        }
        
        .header-meta-item:hover {
            background: rgba(255, 255, 255, 0.15);
            transform: translateY(-2px);
        }
        
        .header-meta-item i {
            font-size: 1.5rem;
            opacity: 0.8;
        }
        
        .header-meta-content h3 {
            font-size: 0.875rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            opacity: 0.8;
            margin-bottom: 0.25rem;
        }
        
        .header-meta-content p {
            font-size: 1.125rem;
            font-weight: 600;
        }
        
        /* Navigation Tabs */
        .nav-tabs {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 2rem;
            background: var(--white);
            padding: 0.5rem;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow-sm);
            border: 1px solid var(--gray-200);
        }
        
        .nav-tab {
            flex: 1;
            padding: 1rem 1.5rem;
            border: none;
            background: transparent;
            border-radius: var(--border-radius-sm);
            font-weight: 500;
            color: var(--gray-600);
            cursor: pointer;
            transition: var(--transition);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }
        
        .nav-tab:hover {
            background: var(--gray-50);
            color: var(--gray-800);
        }
        
        .nav-tab.active {
            background: var(--primary-blue);
            color: var(--white);
            box-shadow: var(--shadow-sm);
        }
        
        /* Statistics Cards */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }
        
        .stat-card {
            background: var(--white);
            padding: 2rem;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow-md);
            border: 1px solid var(--gray-200);
            position: relative;
            overflow: hidden;
            transition: var(--transition);
        }
        
        .stat-card:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-xl);
        }
        
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: var(--primary-blue);
        }
        
        .stat-card.success::before { background: var(--success-green); }
        .stat-card.warning::before { background: var(--warning-amber); }
        .stat-card.danger::before { background: var(--danger-red); }
        .stat-card.secondary::before { background: var(--secondary-indigo); }
        
        .stat-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1rem;
        }
        
        .stat-title {
            font-size: 0.875rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--gray-600);
        }
        
        .stat-icon {
            width: 3rem;
            height: 3rem;
            border-radius: var(--border-radius-sm);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            color: var(--white);
            background: var(--primary-blue);
        }
        
        .stat-card.success .stat-icon { background: var(--success-green); }
        .stat-card.warning .stat-icon { background: var(--warning-amber); }
        .stat-card.danger .stat-icon { background: var(--danger-red); }
        .stat-card.secondary .stat-icon { background: var(--secondary-indigo); }
        
        .stat-value {
            font-size: 3rem;
            font-weight: 800;
            color: var(--gray-900);
            margin-bottom: 0.5rem;
            line-height: 1;
        }
        
        .stat-description {
            color: var(--gray-600);
            font-size: 0.875rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .trend-indicator {
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            font-weight: 600;
            font-size: 0.75rem;
            padding: 0.25rem 0.5rem;
            border-radius: 9999px;
        }
        
        .trend-up {
            background: #dcfce7;
            color: #166534;
        }
        
        .trend-down {
            background: #fef2f2;
            color: #991b1b;
        }
        
        /* Content Sections */
        .content-section {
            background: var(--white);
            border-radius: var(--border-radius);
            box-shadow: var(--shadow-md);
            border: 1px solid var(--gray-200);
            margin-bottom: 2rem;
            overflow: hidden;
        }
        
        .section-header {
            padding: 2rem;
            background: linear-gradient(135deg, var(--gray-50) 0%, var(--gray-100) 100%);
            border-bottom: 1px solid var(--gray-200);
        }
        
        .section-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--gray-900);
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 0.5rem;
        }
        
        .section-subtitle {
            color: var(--gray-600);
            font-size: 0.875rem;
        }
        
        .section-content {
            padding: 2rem;
        }
        
        /* Charts */
        .chart-container {
            max-width: 600px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        /* Repository Table */
        .table-container {
            overflow-x: auto;
        }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .data-table th {
            background: var(--gray-50);
            color: var(--gray-700);
            font-weight: 600;
            padding: 1rem;
            text-align: left;
            border-bottom: 2px solid var(--gray-200);
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .data-table td {
            padding: 1rem;
            border-bottom: 1px solid var(--gray-200);
            vertical-align: middle;
        }
        
        .data-table tbody tr:hover {
            background: var(--gray-50);
        }
        
        .repo-cell {
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }
        
        .repo-name {
            font-weight: 600;
            color: var(--gray-900);
        }
        
        .repo-description {
            font-size: 0.875rem;
            color: var(--gray-600);
        }
        
        /* Status Badges */
        .badge {
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            padding: 0.5rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .badge-success {
            background: #dcfce7;
            color: #166534;
        }
        
        .badge-danger {
            background: #fef2f2;
            color: #991b1b;
        }
        
        .badge-warning {
            background: #fef3c7;
            color: #92400e;
        }
        
        /* Technology Badges */
        .tech-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        
        .tech-badge {
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 500;
            color: var(--white);
            background: var(--gray-500);
        }
        
        .tech-badge.java { background: #f89820; }
        .tech-badge.python { background: #3776ab; }
        .tech-badge.javascript { background: #f7df1e; color: #000; }
        .tech-badge.typescript { background: #3178c6; }
        .tech-badge.go { background: #00add8; }
        .tech-badge.rust { background: #000; }
        .tech-badge.ruby { background: #cc342d; }
        .tech-badge.maven { background: #c71a36; }
        .tech-badge.nodejs { background: #339933; }
        
        /* Filters and Search */
        .filters-bar {
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
            flex-wrap: wrap;
        }
        
        .filter-group {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .filter-label {
            font-size: 0.875rem;
            font-weight: 500;
            color: var(--gray-700);
        }
        
        .filter-input {
            padding: 0.75rem 1rem;
            border: 1px solid var(--gray-300);
            border-radius: var(--border-radius-sm);
            font-size: 0.875rem;
            transition: var(--transition);
        }
        
        .filter-input:focus {
            outline: none;
            border-color: var(--primary-blue);
            box-shadow: 0 0 0 3px rgb(59 130 246 / 0.1);
        }
        
        /* Footer */
        .footer {
            margin-top: 4rem;
            padding: 2rem;
            text-align: center;
            background: var(--white);
            border-radius: var(--border-radius);
            box-shadow: var(--shadow-sm);
            border: 1px solid var(--gray-200);
        }
        
        .footer-content {
            color: var(--gray-600);
            font-size: 0.875rem;
        }
        
        .footer-brand {
            font-weight: 600;
            color: var(--primary-blue);
        }
        
        /* Tab Content */
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .container {
                padding: 1rem;
            }
            
            .header {
                padding: 2rem 1rem;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .header-meta {
                grid-template-columns: 1fr;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .nav-tabs {
                flex-direction: column;
            }
            
            .filters-bar {
                flex-direction: column;
            }
        }
        
        /* Animations */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .animate-fade-in {
            animation: fadeInUp 0.6s ease-out;
        }
        
        /* Loading States */
        .loading {
            opacity: 0.6;
            pointer-events: none;
        }
        
        .skeleton {
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            animation: loading 1.5s infinite;
        }
        
        @keyframes loading {
            0% {
                background-position: 200% 0;
            }
            100% {
                background-position: -200% 0;
            }
        }
        """
    
    def _get_enhanced_single_css_styles(self) -> str:
        """Get enhanced CSS styles for single repository reports with professional design"""
        return """
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
        
        * { 
            margin: 0; 
            padding: 0; 
            box-sizing: border-box; 
        }
        
        :root {
            --primary-blue: #3b82f6;
            --primary-dark: #1e40af;
            --secondary-indigo: #6366f1;
            --success-green: #10b981;
            --warning-amber: #f59e0b;
            --danger-red: #ef4444;
            --gray-50: #f8fafc;
            --gray-100: #f1f5f9;
            --gray-200: #e2e8f0;
            --gray-300: #cbd5e1;
            --gray-400: #94a3b8;
            --gray-500: #64748b;
            --gray-600: #475569;
            --gray-700: #334155;
            --gray-800: #1e293b;
            --gray-900: #0f172a;
            --white: #ffffff;
            --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
            --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
            --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
            --border-radius: 12px;
            --border-radius-sm: 6px;
            --border-radius-lg: 16px;
            --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: var(--gray-800);
            background: linear-gradient(135deg, var(--primary-blue) 0%, var(--secondary-indigo) 100%);
            min-height: 100vh;
        }
        
        /* Navigation */
        .navbar {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding: 1rem 2rem;
            position: sticky;
            top: 0;
            z-index: 1000;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
        
        .nav-brand {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-weight: 700;
            font-size: 1.25rem;
            color: #2d3748;
        }
        
        .nav-brand i {
            color: #667eea;
            font-size: 1.5rem;
        }
        
        .nav-links {
            display: flex;
            gap: 2rem;
        }
        
        .nav-links a {
            text-decoration: none;
            color: #4a5568;
            font-weight: 500;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .nav-links a:hover {
            color: #667eea;
            background: rgba(102, 126, 234, 0.1);
            transform: translateY(-2px);
        }
        
        .nav-links i {
            font-size: 0.9rem;
        }
        
        /* Main Content */
        .main-content {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        /* Hero Section */
        .hero-section {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(15px);
            border-radius: 20px;
            padding: 3rem;
            margin-bottom: 2rem;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .hero-content {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 3rem;
            align-items: center;
        }
        
        .hero-text h1 {
            font-size: 3rem;
            font-weight: 700;
            color: #1a202c;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .hero-text h1 i {
            color: #667eea;
        }
        
        .hero-subtitle {
            font-size: 1.25rem;
            color: #4a5568;
            margin-bottom: 1.5rem;
            font-weight: 400;
        }
        
        .hero-meta {
            display: flex;
            gap: 2rem;
            flex-wrap: wrap;
        }
        
        .hero-meta span {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: #718096;
            font-size: 0.95rem;
            background: rgba(113, 128, 150, 0.1);
            padding: 0.5rem 1rem;
            border-radius: 50px;
        }
        
        .hero-meta i {
            color: #667eea;
        }
        
        .hero-visual {
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .security-badge {
            width: 200px;
            height: 200px;
            border-radius: 50%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 1.1rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            animation: pulse 3s infinite;
        }
        
        .security-badge.secure {
            background: linear-gradient(135deg, #68d391, #38a169);
            color: white;
        }
        
        .security-badge.warning {
            background: linear-gradient(135deg, #f6ad55, #ed8936);
            color: white;
        }
        
        .security-badge.critical {
            background: linear-gradient(135deg, #fc8181, #e53e3e);
            color: white;
        }
        
        .security-badge i {
            font-size: 3rem;
            margin-bottom: 0.5rem;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        /* Metrics Section */
        .metrics-section {
            margin-bottom: 3rem;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
        }
        
        .metric-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 2rem;
            display: flex;
            align-items: center;
            gap: 1.5rem;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2);
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
        }
        
        .metric-icon {
            width: 60px;
            height: 60px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
        }
        
        .metric-card.primary .metric-icon {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }
        
        .metric-card.success .metric-icon {
            background: linear-gradient(135deg, #68d391, #38a169);
            color: white;
        }
        
        .metric-card.info .metric-icon {
            background: linear-gradient(135deg, #63b3ed, #3182ce);
            color: white;
        }
        
        .metric-card.warning .metric-icon {
            background: linear-gradient(135deg, #f6ad55, #ed8936);
            color: white;
        }
        
        .metric-card.secondary .metric-icon {
            background: linear-gradient(135deg, #a78bfa, #8b5cf6);
            color: white;
        }
        
        .metric-content h3 {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1a202c;
            margin-bottom: 0.25rem;
        }
        
        .metric-content p {
            color: #4a5568;
            font-weight: 500;
            margin-bottom: 0.5rem;
        }
        
        .metric-trend {
            font-size: 0.875rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }
        
        .metric-trend.positive {
            color: #38a169;
        }
        
        .metric-trend.negative {
            color: #e53e3e;
        }
        
        .metric-trend.neutral {
            color: #718096;
        }
        
        /* Section */
        .section {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 2.5rem;
            margin-bottom: 2rem;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .section-header {
            margin-bottom: 2rem;
        }
        
        .section-header h2 {
            font-size: 2rem;
            font-weight: 700;
            color: #1a202c;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        
        .section-header h2 i {
            color: #667eea;
        }
        
        .section-header p {
            color: #718096;
            font-size: 1.1rem;
        }
        
        /* Tables */
        .component-table {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            margin-bottom: 2rem;
        }
        
        .component-table-header {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 1.5rem 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .component-table-header h3 {
            font-size: 1.25rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .component-count {
            background: rgba(255, 255, 255, 0.2);
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 600;
        }
        
        .component-table table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .component-table th {
            background: #f8fafc;
            color: #2d3748;
            font-weight: 600;
            padding: 1rem 1.5rem;
            text-align: left;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .component-table td {
            padding: 1rem 1.5rem;
            border-bottom: 1px solid #e2e8f0;
            vertical-align: middle;
        }
        
        .component-table tr:hover {
            background: #f7fafc;
        }
        
        .component-table .component-name {
            font-weight: 600;
            color: #2d3748;
        }
        
        .component-table .component-version {
            color: #667eea;
            font-weight: 500;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.9rem;
            background: rgba(102, 126, 234, 0.1);
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
        }
        
        .badge {
            display: inline-flex;
            align-items: center;
            padding: 0.375rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .badge.scope-direct {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }
        
        .badge.scope-transitive {
            background: linear-gradient(135deg, #a0aec0, #718096);
            color: white;
        }
        
        .badge.scope-dev {
            background: linear-gradient(135deg, #a78bfa, #8b5cf6);
            color: white;
        }
        
        /* Footer */
        .footer {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 2rem;
            margin-top: 3rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .footer-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: white;
        }
        
        .footer-brand {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-weight: 600;
        }
        
        .footer-brand i {
            font-size: 1.25rem;
        }
        
        .footer-info {
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.9rem;
        }
        
        /* Responsive Design */
        @media (max-width: 1024px) {
            .hero-content {
                grid-template-columns: 1fr;
                text-align: center;
            }
            
            .hero-text h1 {
                font-size: 2.5rem;
            }
            
            .metrics-grid {
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            }
        }
        
        @media (max-width: 768px) {
            .main-content {
                padding: 1rem;
            }
            
            .navbar {
                padding: 1rem;
                flex-direction: column;
                gap: 1rem;
            }
            
            .nav-links {
                gap: 1rem;
            }
            
            .hero-section {
                padding: 2rem;
            }
            
            .hero-text h1 {
                font-size: 2rem;
            }
            
            .hero-meta {
                flex-direction: column;
                gap: 0.5rem;
            }
            
            .security-badge {
                width: 150px;
                height: 150px;
            }
            
            .metric-card {
                padding: 1.5rem;
            }
            
            .footer-content {
                flex-direction: column;
                gap: 1rem;
                text-align: center;
            }
        }
        
        /* Animations */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .section {
            animation: fadeInUp 0.6s ease-out;
        }
        """
    
    def _generate_enhanced_component_tables(self, components_by_type: Dict[str, List]) -> str:
        """Generate enhanced HTML tables for components"""
        if not components_by_type:
            return ""
        
        html = ""
        type_icons = {
            'library': 'fas fa-book',
            'framework': 'fas fa-layer-group',
            'application': 'fas fa-desktop',
            'service': 'fas fa-server',
            'tool': 'fas fa-tools',
            'plugin': 'fas fa-plug'
        }
        
        for comp_type, components in sorted(components_by_type.items()):
            icon = type_icons.get(comp_type.lower(), 'fas fa-cube')
            html += f"""
            <div class="component-table">
                <div class="component-table-header">
                    <h3><i class="{icon}"></i> {comp_type.title()}</h3>
                    <div class="component-count">{len(components)} components</div>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Component</th>
                            <th>Version</th>
                            <th>License</th>
                            <th>Scope</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for comp in sorted(components, key=lambda x: x.get('name', '')):
                html += f"""
                        <tr>
                            <td><div class="component-name">{comp.get('name', 'Unknown')}</div></td>
                            <td><div class="component-version">{comp.get('version', 'Unknown')}</div></td>
                            <td>{comp.get('license', 'Unknown')}</td>
                            <td><span class="badge scope-{comp.get('scope', 'unknown')}">{comp.get('scope', 'Unknown')}</span></td>
                        </tr>
                """
            
            html += """
                    </tbody>
                </table>
            </div>
            """
        
        return html
    
    def _generate_single_report_scripts(self) -> str:
        """Generate JavaScript for single report interactivity"""
        return """
        // Smooth scrolling for navigation links
        document.querySelectorAll('.nav-links a[href^="#"]').forEach(function(link) {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const targetId = this.getAttribute('href');
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
        
        // Add intersection observer for navigation highlighting
        const sections = document.querySelectorAll('section[id]');
        const navLinks = document.querySelectorAll('.nav-links a');
        
        const observer = new IntersectionObserver(
            function(entries) {
                entries.forEach(function(entry) {
                    if (entry.isIntersecting) {
                        navLinks.forEach(function(link) {
                            link.style.color = '#4a5568';
                            link.style.background = 'transparent';
                        });
                        
                        const activeLink = document.querySelector(`.nav-links a[href="#${entry.target.id}"]`);
                        if (activeLink) {
                            activeLink.style.color = '#667eea';
                            activeLink.style.background = 'rgba(102, 126, 234, 0.1)';
                        }
                    }
                });
            },
            {
                threshold: 0.3,
                rootMargin: '-20% 0px -20% 0px'
            }
        );
        
        sections.forEach(function(section) { observer.observe(section); });
        
        // Animate metrics on scroll
        const animateMetrics = function() {
            const metricNumbers = document.querySelectorAll('.metric-content h3');
            metricNumbers.forEach(function(metric) {
                const finalValue = parseInt(metric.textContent.replace(/,/g, ''));
                let currentValue = 0;
                const increment = finalValue / 50;
                
                const timer = setInterval(function() {
                    currentValue += increment;
                    if (currentValue >= finalValue) {
                        currentValue = finalValue;
                        clearInterval(timer);
                    }
                    metric.textContent = Math.floor(currentValue).toLocaleString();
                }, 20);
            });
        };
        
        // Trigger animation when metrics section is visible
        const metricsSection = document.querySelector('.metrics-section');
        if (metricsSection) {
        const metricsObserver = new IntersectionObserver(
            function(entries) {
                entries.forEach(function(entry) {
                    if (entry.isIntersecting) {
                        animateMetrics();
                        metricsObserver.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.5 }
        );
            
            metricsObserver.observe(metricsSection);
        }
        
        // Add loading state removal
        document.addEventListener('DOMContentLoaded', function() {
            document.body.style.opacity = '0';
            setTimeout(function() {
                document.body.style.transition = 'opacity 0.5s ease-in';
                document.body.style.opacity = '1';
            }, 100);
        });
        """
    
    def _generate_tech_breakdown_cards(self, tech_distribution: Dict[str, int]) -> str:
        """Generate technology breakdown cards for the technologies tab"""
        if not tech_distribution:
            return "<p>No technology data available.</p>"
        
        cards = []
        for tech, count in sorted(tech_distribution.items(), key=lambda x: x[1], reverse=True):
            # Calculate percentage
            total = sum(tech_distribution.values())
            percentage = (count / total) * 100 if total > 0 else 0
            
            # Get appropriate color for technology
            tech_colors = {
                'java': '#f89820',
                'python': '#3776ab', 
                'javascript': '#f7df1e',
                'typescript': '#3178c6',
                'go': '#00add8',
                'rust': '#000000',
                'ruby': '#cc342d',
                'maven': '#c71a36',
                'nodejs': '#339933'
            }
            color = tech_colors.get(tech.lower(), '#6366f1')
            
            cards.append(f"""
            <div style="background: var(--white); padding: 1.5rem; border-radius: var(--border-radius); box-shadow: var(--shadow-sm); border: 1px solid var(--gray-200);">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
                    <div style="display: flex; align-items: center; gap: 0.75rem;">
                        <div style="width: 12px; height: 12px; border-radius: 50%; background: {color};"></div>
                        <h4 style="margin: 0; color: var(--gray-800); font-size: 1.125rem; font-weight: 600;">{tech}</h4>
                    </div>
                    <span style="font-size: 1.5rem; font-weight: 700; color: var(--gray-900);">{count}</span>
                </div>
                <div style="margin-bottom: 0.5rem;">
                    <div style="width: 100%; height: 8px; background: var(--gray-200); border-radius: 4px; overflow: hidden;">
                        <div style="width: {percentage}%; height: 100%; background: {color}; transition: width 0.3s ease;"></div>
                    </div>
                </div>
                <p style="margin: 0; color: var(--gray-600); font-size: 0.875rem;">{percentage:.1f}% of repositories</p>
            </div>""")
        
        return '\n'.join(cards)
    
    def _generate_vulnerability_filter_controls(self) -> str:
        """Generate vulnerability filtering controls for interactive filtering"""
        # This method is no longer needed as filtering controls are now integrated into the main table
        return ""
    
    def _generate_comprehensive_vulnerability_list(self, org_summary: Dict[str, Any]) -> str:
        """Generate comprehensive vulnerability list aggregated from all repositories"""
        # Get repositories list for counting repos with vulnerabilities
        repositories = org_summary.get('repositories', [])
        
        # Extract all vulnerabilities from the organization summary - these are already aggregated by the core
        all_vulnerabilities = org_summary.get('vulnerabilities', [])
        
        # Always collect vulnerabilities from individual repositories to ensure repository names are included
        repo_vulnerabilities = []
        for repo in repositories:
            repo_vulns = repo.get('vulnerabilities', [])
            for vuln in repo_vulns:
                vuln_with_repo = vuln.copy()
                vuln_with_repo['repository'] = repo.get('name', 'Unknown')
                repo_vulnerabilities.append(vuln_with_repo)
        
        # Use repository-level vulnerabilities if available, otherwise fall back to org-level
        if repo_vulnerabilities:
            all_vulnerabilities = repo_vulnerabilities
        elif not all_vulnerabilities:
            # Last resort: try to match org-level vulnerabilities to repositories
            for vuln in all_vulnerabilities:
                if 'repository' not in vuln:
                    # Try to find matching repository based on component
                    component_name = vuln.get('component', '')
                    matched_repo = None
                    for repo in repositories:
                        repo_components = repo.get('component_names', [])
                        if component_name in repo_components:
                            matched_repo = repo.get('name', 'Unknown')
                            break
                    vuln['repository'] = matched_repo or 'Multiple Repositories'
        
        if not all_vulnerabilities:
            return f"""
            <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: var(--border-radius); padding: 2rem; text-align: center; color: var(--success-green);">
                <div style="font-size: 3rem; margin-bottom: 1rem;">
                    <i class="fas fa-shield-check"></i>
                </div>
                <h3 style="color: var(--success-green); margin-bottom: 1rem;">🎉 No vulnerabilities detected!</h3>
                <p style="color: var(--gray-600); font-size: 1.125rem;">All {org_summary.get('successful_scans', 0)} scanned repositories are secure.</p>
            </div>
            """
        
        # Sort vulnerabilities by severity (critical first)
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'unknown': 4}
        all_vulnerabilities.sort(key=lambda v: (severity_order.get(v.get('severity', 'unknown'), 4), v.get('component', '')))
        
        # Generate vulnerability table
        vulnerability_rows = ""
        for vuln in all_vulnerabilities:
            severity = vuln.get('severity', 'unknown').lower()
            severity_colors = {
                'critical': '#dc2626',
                'high': '#ea580c',
                'medium': '#d97706',
                'low': '#0284c7',
                'unknown': '#6b7280'
            }
            severity_color = severity_colors.get(severity, '#6b7280')
            
            # Truncate description for table display
            description = vuln.get('description', 'No description available')[:150]
            if len(vuln.get('description', '')) > 150:
                description += '...'
            
            # Format references
            references_html = ""
            if vuln.get('references'):
                ref_links = []
                for ref in vuln.get('references', [])[:2]:  # Show first 2 references
                    ref_links.append(f'<a href="{ref}" target="_blank" style="color: {severity_color}; text-decoration: none; margin-right: 0.5rem;"><i class="fas fa-external-link-alt"></i></a>')
                references_html = ''.join(ref_links)
            
            cvss_score = vuln.get('cvss_score', '')
            cvss_display = f" (CVSS: {cvss_score})" if cvss_score else ""
            
            vulnerability_rows += f"""
            <tr class="vuln-row" data-repository="{vuln.get('repository', 'Unknown').lower()}" data-severity="{severity}" data-component="{vuln.get('component', 'Unknown').lower()}" style="border-bottom: 1px solid var(--gray-200);">
                <td style="padding: 1rem; vertical-align: top;">
                    <div style="font-weight: 600; color: var(--gray-900); margin-bottom: 0.25rem;">{vuln.get('repository', 'Unknown')}</div>
                    <div style="font-size: 0.875rem; color: var(--gray-600);">{vuln.get('component', 'Unknown')}</div>
                    <div style="font-size: 0.75rem; color: var(--gray-500); font-family: monospace;">{vuln.get('component_version', '')}</div>
                </td>
                <td style="padding: 1rem; vertical-align: top;">
                    <code style="background: var(--gray-100); padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.875rem;">{vuln.get('id', 'Unknown')}</code>
                </td>
                <td style="padding: 1rem; vertical-align: top;">
                    <span style="display: inline-block; padding: 0.375rem 0.75rem; background: {severity_color}; color: white; border-radius: 12px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">
                        {severity}{cvss_display}
                    </span>
                </td>
                <td style="padding: 1rem; vertical-align: top; max-width: 300px;">
                    <div style="margin-bottom: 0.5rem;">
                        <strong style="color: var(--gray-900);">{vuln.get('title', vuln.get('summary', 'Vulnerability'))}</strong>
                    </div>
                    <div style="font-size: 0.875rem; color: var(--gray-600); line-height: 1.4;">{description}</div>
                    <div style="margin-top: 0.5rem;">{references_html}</div>
                </td>
                <td style="padding: 1rem; vertical-align: top; text-align: center;">
                    <div style="font-size: 0.875rem; color: var(--gray-600);">{vuln.get('published', '')[:10] if vuln.get('published') else 'N/A'}</div>
                </td>
            </tr>
            """
        
        return f"""
        <div style="background: var(--white); border-radius: var(--border-radius); border: 1px solid var(--gray-200); margin-top: 2rem;">
            <div style="background: var(--gray-50); padding: 1.5rem; border-bottom: 1px solid var(--gray-200); border-radius: var(--border-radius) var(--border-radius) 0 0;">
                <h3 style="margin: 0; color: var(--gray-900); font-size: 1.25rem; font-weight: 600; display: flex; align-items: center; gap: 0.5rem;">
                    <i class="fas fa-list-alt"></i>
                    Complete Vulnerability Inventory ({len(all_vulnerabilities)} total)
                </h3>
                <p style="margin: 0.5rem 0 0 0; color: var(--gray-600); font-size: 0.875rem;">
                    Detailed list of all security vulnerabilities found across {len([r for r in repositories if r.get('vulnerabilities', 0) > 0])} repositories
                </p>
            </div>
            
            <!-- Vulnerability Filtering Controls -->
            <div style="padding: 1rem 1.5rem; background: var(--gray-50); border-bottom: 1px solid var(--gray-200); display: flex; gap: 1rem; flex-wrap: wrap; align-items: center;">
                <div style="display: flex; flex-direction: column; gap: 0.25rem;">
                    <label style="font-size: 0.75rem; font-weight: 600; color: var(--gray-700); text-transform: uppercase; letter-spacing: 0.05em;">Filter by Repository</label>
                    <select id="vulnerabilityRepoFilter" onchange="filterVulnerabilityTable()" style="padding: 0.5rem; border: 1px solid var(--gray-300); border-radius: 4px; font-size: 0.875rem; background: white;">
                        <option value="all">All Repositories</option>
                        {self._generate_vulnerability_repo_filter_options(repositories)}
                    </select>
                </div>
                <div style="display: flex; flex-direction: column; gap: 0.25rem;">
                    <label style="font-size: 0.75rem; font-weight: 600; color: var(--gray-700); text-transform: uppercase; letter-spacing: 0.05em;">Filter by Severity</label>
                    <select id="vulnerabilitySeverityFilter" onchange="filterVulnerabilityTable()" style="padding: 0.5rem; border: 1px solid var(--gray-300); border-radius: 4px; font-size: 0.875rem; background: white;">
                        <option value="all">All Severities</option>
                        <option value="critical">Critical</option>
                        <option value="high">High</option>
                        <option value="medium">Medium</option>
                        <option value="low">Low</option>
                        <option value="unknown">Unknown</option>
                    </select>
                </div>
                <div style="display: flex; flex-direction: column; gap: 0.25rem;">
                    <label style="font-size: 0.75rem; font-weight: 600; color: var(--gray-700); text-transform: uppercase; letter-spacing: 0.05em;">Search Components</label>
                    <input type="text" id="vulnerabilityComponentSearch" placeholder="Component name..." onkeyup="filterVulnerabilityTable()" style="padding: 0.5rem; border: 1px solid var(--gray-300); border-radius: 4px; font-size: 0.875rem; min-width: 200px;">
                </div>
                <div style="margin-left: auto; display: flex; align-items: end;">
                    <button onclick="resetVulnerabilityFilters()" style="padding: 0.5rem 1rem; background: var(--gray-600); color: white; border: none; border-radius: 4px; font-size: 0.875rem; cursor: pointer;">Reset Filters</button>
                </div>
            </div>
            
            <div style="overflow-x: auto;">
                <table id="vulnerabilityTable" style="width: 100%; border-collapse: collapse; margin: 0;">
                    <thead>
                        <tr style="background: var(--gray-50);">
                            <th onclick="sortVulnerabilityTable(0)" style="padding: 1rem; text-align: left; font-weight: 600; color: var(--gray-700); border-bottom: 2px solid var(--gray-200); font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; cursor: pointer;">Repository / Component <i class="fas fa-sort"></i></th>
                            <th onclick="sortVulnerabilityTable(1)" style="padding: 1rem; text-align: left; font-weight: 600; color: var(--gray-700); border-bottom: 2px solid var(--gray-200); font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; cursor: pointer;">Vulnerability ID <i class="fas fa-sort"></i></th>
                            <th onclick="sortVulnerabilityTable(2)" style="padding: 1rem; text-align: left; font-weight: 600; color: var(--gray-700); border-bottom: 2px solid var(--gray-200); font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; cursor: pointer;">Severity <i class="fas fa-sort"></i></th>
                            <th style="padding: 1rem; text-align: left; font-weight: 600; color: var(--gray-700); border-bottom: 2px solid var(--gray-200); font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em;">Description & References</th>
                            <th onclick="sortVulnerabilityTable(4)" style="padding: 1rem; text-align: left; font-weight: 600; color: var(--gray-700); border-bottom: 2px solid var(--gray-200); font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; cursor: pointer;">Published <i class="fas fa-sort"></i></th>
                        </tr>
                    </thead>
                    <tbody>
                        {vulnerability_rows}
                    </tbody>
                </table>
            </div>
            
            <div style="padding: 1.5rem; background: var(--gray-50); border-top: 1px solid var(--gray-200); border-radius: 0 0 var(--border-radius) var(--border-radius);">
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem;">
                    <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
                        <div style="font-size: 0.875rem; color: var(--gray-600);">Legend:</div>
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <span style="width: 12px; height: 12px; background: #dc2626; border-radius: 2px;"></span>
                            <span style="font-size: 0.75rem; color: var(--gray-600);">Critical</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <span style="width: 12px; height: 12px; background: #ea580c; border-radius: 2px;"></span>
                            <span style="font-size: 0.75rem; color: var(--gray-600);">High</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <span style="width: 12px; height: 12px; background: #d97706; border-radius: 2px;"></span>
                            <span style="font-size: 0.75rem; color: var(--gray-600);">Medium</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <span style="width: 12px; height: 12px; background: #0284c7; border-radius: 2px;"></span>
                            <span style="font-size: 0.75rem; color: var(--gray-600);">Low</span>
                        </div>
                    </div>
                    <div style="font-size: 0.875rem; color: var(--gray-600);">
                        💡 Click on vulnerability IDs to view detailed information from security databases
                    </div>
                </div>
            </div>
        </div>
        """
    
    def _generate_vulnerability_repo_filter_options(self, repositories: List[Dict[str, Any]]) -> str:
        """Generate repository filter options for vulnerability table"""
        options = []
        for repo in repositories:
            repo_name = repo.get('name', 'Unknown')
            vuln_count = repo.get('vulnerabilities', 0)
            if vuln_count > 0:
                options.append(f'<option value="{repo_name.lower()}">{repo_name} ({vuln_count} vulnerabilities)</option>')
        return '\n'.join(options)
    
    def _generate_enhanced_interactive_scripts(self, tech_chart_data: str, org_summary: Dict[str, Any]) -> str:
        """Generate enhanced JavaScript for organization dashboard interactivity"""
        org_summary_json = json.dumps(org_summary, default=str)
        
        return f"""
        // Tab switching functionality
        let activeTab = 'overview';
        
        function showTab(tabName) {{
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(function(tab) {{
                tab.classList.remove('active');
            }});
            
            // Remove active class from all nav tabs
            document.querySelectorAll('.nav-tab').forEach(function(tab) {{
                tab.classList.remove('active');
            }});
            
            // Show selected tab content
            const targetTab = document.getElementById(tabName + '-tab');
            if (targetTab) {{
                targetTab.classList.add('active');
            }}
            
            // Add active class to clicked nav tab
            const navTab = document.querySelector(`.nav-tab[onclick="showTab('${{tabName}}')"]`);
            if (navTab) {{
                navTab.classList.add('active');
            }}
            
            activeTab = tabName;
            
            // Initialize charts when switching to relevant tabs
            if (tabName === 'overview') {{
            setTimeout(function() {{ initTechChart(); }}, 100);
            }} else if (tabName === 'technologies') {{
                setTimeout(function() {{ initTechDetailsChart(); }}, 100);
            }}
        }}
        
        // Initialize technology distribution chart
        let techChart = null;
        function initTechChart() {{
            const ctx = document.getElementById('techChart');
            if (!ctx || techChart) return;
            
            try {{
                techChart = new Chart(ctx, {{
                    type: 'doughnut',
                    data: {tech_chart_data},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                position: 'bottom',
                                labels: {{
                                    padding: 20,
                                    usePointStyle: true,
                                    font: {{
                                        family: 'Inter',
                                        size: 12
                                    }}
                                }}
                            }},
                            tooltip: {{
                                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                                titleFont: {{
                                    family: 'Inter',
                                    size: 14
                                }},
                                bodyFont: {{
                                    family: 'Inter',
                                    size: 13
                                }},
                                cornerRadius: 8
                            }}
                        }},
                        animation: {{
                            animateScale: true,
                            duration: 1000
                        }}
                    }}
                }});
            }} catch (error) {{
                console.error('Error initializing tech chart:', error);
            }}
        }}
        
        // Initialize detailed technology chart
        let techDetailsChart = null;
        function initTechDetailsChart() {{
            const ctx = document.getElementById('techDetailsChart');
            if (!ctx || techDetailsChart) return;
            
            try {{
                techDetailsChart = new Chart(ctx, {{
                    type: 'bar',
                    data: {tech_chart_data},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                grid: {{
                                    color: 'rgba(0, 0, 0, 0.1)'
                                }},
                                ticks: {{
                                    font: {{
                                        family: 'Inter'
                                    }}
                                }}
                            }},
                            x: {{
                                grid: {{
                                    display: false
                                }},
                                ticks: {{
                                    font: {{
                                        family: 'Inter'
                                    }}
                                }}
                            }}
                        }},
                        plugins: {{
                            legend: {{
                                display: false
                            }},
                            tooltip: {{
                                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                                titleFont: {{
                                    family: 'Inter'
                                }},
                                bodyFont: {{
                                    family: 'Inter'
                                }},
                                cornerRadius: 8
                            }}
                        }},
                        animation: {{
                            duration: 1000,
                            easing: 'easeInOutQuart'
                        }}
                    }}
                }});
            }} catch (error) {{
                console.error('Error initializing tech details chart:', error);
            }}
        }}
        
        // Repository filtering functionality
        function filterRepositories() {{
            const search = document.getElementById('repoSearch').value.toLowerCase();
            const statusFilter = document.getElementById('statusFilter').value;
            const techFilter = document.getElementById('techFilter').value;
            const rows = document.querySelectorAll('#repoTable tbody tr');
            
            let visibleCount = 0;
            
            rows.forEach(function(row) {{
                const name = row.cells[0].textContent.toLowerCase();
                const status = row.dataset.status;
                const tech = row.dataset.tech;
                
                let visible = true;
                
                if (search \u0026\u0026 !name.includes(search)) visible = false;
                if (statusFilter !== 'all' \u0026\u0026 status !== statusFilter) visible = false;
                if (techFilter !== 'all' \u0026\u0026 !tech.includes(techFilter)) visible = false;
                
                row.style.display = visible ? '' : 'none';
                if (visible) visibleCount++;
            }});
            
            // Update visible count indicator if needed
            const countIndicator = document.getElementById('visibleCount');
            if (countIndicator) {{
                countIndicator.textContent = `Showing ${{visibleCount}} of ${{rows.length}} repositories`;
            }}
        }}
        
        // Table sorting functionality
        let sortDirection = {{}};
        function sortTable(columnIndex) {{
            const table = document.getElementById('repoTable');
            if (!table) return;
            
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr')).filter(function(row) {{ return row.style.display !== 'none'; }});
            
            const direction = sortDirection[columnIndex] = !sortDirection[columnIndex];
            
        rows.sort(function(a, b) {{
                const aVal = a.cells[columnIndex].textContent.trim();
                const bVal = b.cells[columnIndex].textContent.trim();
                
                // Handle numeric columns (Components, Vulnerabilities)
                if (columnIndex === 2 || columnIndex === 3) {{
                    const aNum = parseInt(aVal.replace(/,/g, '')) || 0;
                    const bNum = parseInt(bVal.replace(/,/g, '')) || 0;
                    return direction ? bNum - aNum : aNum - bNum;
                }} else {{
                    // Text columns
                    return direction ? bVal.localeCompare(aVal) : aVal.localeCompare(bVal);
                }}
            }});
            
            // Update sort indicators
            const headers = table.querySelectorAll('th');
            headers.forEach(function(header, index) {{
                const icon = header.querySelector('i');
                if (icon) {{
                    if (index === columnIndex) {{
                        icon.className = direction ? 'fas fa-sort-down' : 'fas fa-sort-up';
                    }} else {{
                        icon.className = 'fas fa-sort';
                    }}
                }}
            }});
            
            // Re-append sorted rows
            rows.forEach(function(row) {{ tbody.appendChild(row); }});
        }}
        
        // Action button handlers
        function viewDetails(repoName) {{
            // Try to open the repository-specific report
            const url = `./${{repoName}}/sbom.html`;
            window.open(url, '_blank');
        }}
        
        function downloadSBOM(repoName) {{
            // Try to download the SBOM file
            const url = `./${{repoName}}/sbom.cyclonedx.json`;
            window.open(url, '_blank');
        }}
        
        // Export functionality
        function exportData() {{
            const data = {org_summary_json};
            const blob = new Blob([JSON.stringify(data, null, 2)], {{ type: 'application/json' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'organization-sbom-summary.json';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }}
        
        function printReport() {{
            window.print();
        }}
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {{
            // Initialize with overview tab
            showTab('overview');
            
            // Initialize vulnerability filtering when security tab is first shown
            const securityTab = document.querySelector('.nav-tab[onclick="showTab(\'security\')"]');
            if (securityTab) {{
                securityTab.addEventListener('click', function() {{
                    setTimeout(function() {{
                        // Initialize filters if they exist
                        const vulnTable = document.getElementById('vulnerabilityTable');
                        if (vulnTable \u0026\u0026 typeof filterVulnerabilityTable === 'function') {{
                            filterVulnerabilityTable();
                        }}
                    }}, 100);
                }});
            }}
            
            // Add loading animation
            document.body.style.opacity = '0';
            setTimeout(function() {{
                document.body.style.transition = 'opacity 0.6s ease-in';
                document.body.style.opacity = '1';
            }}, 100);
            
            // Add smooth animations to cards
            const cards = document.querySelectorAll('.stat-card, .content-section');
            cards.forEach(function(card, index) {{
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                setTimeout(function() {{
                    card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }}, 150 * index);
            }});
        }});
        
        // Vulnerability table filtering functionality
        function filterVulnerabilityTable() {{
            const repoFilter = document.getElementById('vulnerabilityRepoFilter').value;
            const severityFilter = document.getElementById('vulnerabilitySeverityFilter').value;
            const componentSearch = document.getElementById('vulnerabilityComponentSearch').value.toLowerCase();
            const rows = document.querySelectorAll('#vulnerabilityTable tbody tr.vuln-row');
            
            let visibleCount = 0;
            
            rows.forEach(function(row) {{
                const repository = row.dataset.repository;
                const severity = row.dataset.severity;
                const component = row.dataset.component;
                
                let visible = true;
                
                if (repoFilter !== 'all' && repository !== repoFilter) visible = false;
                if (severityFilter !== 'all' && severity !== severityFilter) visible = false;
                if (componentSearch && !component.includes(componentSearch)) visible = false;
                
                row.style.display = visible ? '' : 'none';
                if (visible) visibleCount++;
            }});
            
            // Update count display if needed
            console.log(`Showing ${{visibleCount}} vulnerabilities`);
        }}
        
        function resetVulnerabilityFilters() {{
            document.getElementById('vulnerabilityRepoFilter').value = 'all';
            document.getElementById('vulnerabilitySeverityFilter').value = 'all';
            document.getElementById('vulnerabilityComponentSearch').value = '';
            filterVulnerabilityTable();
        }}
        
        // Vulnerability table sorting
        let vulnSortDirection = {{}};
        function sortVulnerabilityTable(columnIndex) {{
            const table = document.getElementById('vulnerabilityTable');
            if (!table) return;
            
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr.vuln-row')).filter(function(row) {{ return row.style.display !== 'none'; }});
            
            const direction = vulnSortDirection[columnIndex] = !vulnSortDirection[columnIndex];
            
            rows.sort(function(a, b) {{
                const aVal = a.cells[columnIndex].textContent.trim();
                const bVal = b.cells[columnIndex].textContent.trim();
                
                // Handle severity column with special ordering
                if (columnIndex === 2) {{
                    const severityOrder = {{ 'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'UNKNOWN': 4 }};
                    const aOrder = severityOrder[aVal.split(' ')[0]] || 4;
                    const bOrder = severityOrder[bVal.split(' ')[0]] || 4;
                    return direction ? bOrder - aOrder : aOrder - bOrder;
                }} else {{
                    // Text columns
                    return direction ? bVal.localeCompare(aVal) : aVal.localeCompare(bVal);
                }}
            }});
            
            // Update sort indicators
            const headers = table.querySelectorAll('th');
            headers.forEach(function(header, index) {{
                const icon = header.querySelector('i');
                if (icon) {{
                    if (index === columnIndex) {{
                        icon.className = direction ? 'fas fa-sort-down' : 'fas fa-sort-up';
                    }} else {{
                        icon.className = 'fas fa-sort';
                    }}
                }}
            }});
            
            // Re-append sorted rows
            rows.forEach(function(row) {{ tbody.appendChild(row); }});
        }}
        
        // Handle window resize for charts
        window.addEventListener('resize', function() {{
            if (techChart) techChart.resize();
            if (techDetailsChart) techDetailsChart.resize();
        }});
        
        // Add keyboard navigation
        document.addEventListener('keydown', function(e) {{
            if (e.ctrlKey || e.metaKey) {{
                switch (e.key) {{
                    case 'p':
                        e.preventDefault();
                        printReport();
                        break;
                    case 's':
                        e.preventDefault();
                        exportData();
                        break;
                }}
            }}
            
            // ESC to reset vulnerability filters
            if (e.key === 'Escape' && activeTab === 'security') {{
                resetVulnerabilityFilters();
            }}
        }});
        """
    
    def showTab(self, tab_name: str) -> None:
        """Show a specific tab (for programmatic control)"""
        # This is a placeholder method - the actual tab switching is handled by JavaScript
        pass


class MarkdownGenerator:
    """Generate Markdown format reports"""

    def generate(self, sbom_data: Dict[str, Any], output_path: Path):
        """Generate Markdown SBOM report"""
        content = self._generate_markdown_report(sbom_data)
        with open(output_path, "w") as f:
            f.write(content)

    def generate_org_summary(self, org_summary: Dict[str, Any], output_path: Path):
        """Generate organization summary Markdown report"""
        content = self._generate_org_markdown_report(org_summary)
        with open(output_path, "w") as f:
            f.write(content)

    def _generate_markdown_report(self, sbom_data: Dict[str, Any]) -> str:
        """Generate Markdown content for SBOM report"""
        metadata = sbom_data.get("metadata", {})
        components = sbom_data.get("components", [])
        stats = sbom_data.get("stats", {})
        vulnerabilities = sbom_data.get("vulnerabilities", [])

        content = f"""# Software Bill of Materials

## 📋 Metadata

- **Repository**: {metadata.get('repository_name', metadata.get('repository', 'Unknown'))}
- **Generated**: {metadata.get('timestamp', datetime.now().isoformat())}
- **Technologies**: {', '.join(metadata.get('technologies', ['None detected']))}
- **Tool**: {metadata.get('tool', {}).get('name', 'Unknown')} v{metadata.get('tool', {}).get('version', 'Unknown')}

## 📊 Statistics

| Metric | Value |
|--------|-------|
| Total Components | {stats.get('total_components', 0)} |
| Direct Dependencies | {stats.get('direct_deps', 0)} |
| Transitive Dependencies | {stats.get('transitive_deps', 0)} |
{f"| Vulnerabilities | {stats.get('vulnerabilities', 0)} |" if 'vulnerabilities' in stats else ''}

"""

        # Add vulnerabilities section if present
        if vulnerabilities:
            content += """## 🔒 Security Vulnerabilities

| Component | ID | Severity | Description |
|-----------|-------|----------|-------------|
"""
            for vuln in vulnerabilities:
                content += f"| {vuln.get('component', 'Unknown')} | {vuln.get('id', 'Unknown')} | {vuln.get('severity', 'Unknown').upper()} | {vuln.get('description', '')} |\n"
            content += "\n"

        # Add components section
        content += """## 📦 Components

| Name | Version | Type | License | Scope |
|------|---------|------|---------|-------|
"""
        for comp in sorted(components, key=lambda x: x.get("name", "")):
            content += f"| {comp.get('name', 'Unknown')} | {comp.get('version', 'Unknown')} | {comp.get('type', 'library')} | {comp.get('license', 'Unknown')} | {comp.get('scope', 'Unknown')} |\n"

        content += """\n---
*Generated by Firefly SBOM Tool v1.0.0 | Apache License 2.0*
"""

        return content

    def _generate_org_markdown_report(self, org_summary: Dict[str, Any]) -> str:
        """Generate Markdown content for organization summary"""
        content = f"""# Organization SBOM Summary

## 🏢 {org_summary.get('organization', 'Unknown')}

- **Scan Date**: {org_summary.get('scan_date', datetime.now().isoformat())}
- **Total Repositories**: {org_summary.get('total_repositories', 0)}
- **Successful Scans**: {org_summary.get('successful_scans', 0)}
- **Failed Scans**: {org_summary.get('failed_scans', 0)}

## 📊 Overall Statistics

| Metric | Value |
|--------|-------|
| Total Components | {org_summary.get('total_components', 0)} |
| Total Vulnerabilities | {org_summary.get('total_vulnerabilities', 0)} |

## 📂 Repository Summary

| Repository | Status | Components | Vulnerabilities | Technologies |
|------------|--------|------------|-----------------|-------------|
"""

        for repo in org_summary.get("repositories", []):
            content += f"| {repo.get('name', 'Unknown')} | {repo.get('status', 'Unknown').upper()} | {repo.get('components', 0)} | {repo.get('vulnerabilities', 0)} | {', '.join(repo.get('technologies', []))} |\n"

        content += """\n---
*Generated by Firefly SBOM Tool v1.0.0 | Apache License 2.0*
"""

        return content


class TextGenerator:
    """Generate plain text format reports"""

    def generate(self, sbom_data: Dict[str, Any], output_path: Path):
        """Generate text SBOM report"""
        content = self._generate_text_report(sbom_data)
        with open(output_path, "w") as f:
            f.write(content)

    def generate_org_summary(self, org_summary: Dict[str, Any], output_path: Path):
        """Generate organization summary text report"""
        content = self._generate_org_text_report(org_summary)
        with open(output_path, "w") as f:
            f.write(content)

    def _generate_text_report(self, sbom_data: Dict[str, Any]) -> str:
        """Generate plain text content for SBOM report"""
        metadata = sbom_data.get("metadata", {})
        components = sbom_data.get("components", [])
        stats = sbom_data.get("stats", {})

        content = f"""SOFTWARE BILL OF MATERIALS
{'=' * 60}

REPOSITORY: {metadata.get('repository_name', metadata.get('repository', 'Unknown'))}
GENERATED: {metadata.get('timestamp', datetime.now().isoformat())}
TECHNOLOGIES: {', '.join(metadata.get('technologies', ['None detected']))}

STATISTICS:
-----------
Total Components: {stats.get('total_components', 0)}
Direct Dependencies: {stats.get('direct_deps', 0)}
Transitive Dependencies: {stats.get('transitive_deps', 0)}
{f"Vulnerabilities: {stats.get('vulnerabilities', 0)}" if 'vulnerabilities' in stats else ''}

COMPONENTS:
-----------
"""

        for comp in sorted(components, key=lambda x: x.get("name", "")):
            content += f"{comp.get('name', 'Unknown')} @ {comp.get('version', 'Unknown')} [{comp.get('type', 'library')}] - {comp.get('license', 'Unknown')} ({comp.get('scope', 'Unknown')})\n"

        content += f"""\n{'=' * 60}
Generated by Firefly SBOM Tool v1.0.0 | Apache License 2.0
"""

        return content

    def _generate_org_text_report(self, org_summary: Dict[str, Any]) -> str:
        """Generate plain text content for organization summary"""
        content = f"""ORGANIZATION SBOM SUMMARY
{'=' * 60}

ORGANIZATION: {org_summary.get('organization', 'Unknown')}
SCAN DATE: {org_summary.get('scan_date', datetime.now().isoformat())}
TOTAL REPOSITORIES: {org_summary.get('total_repositories', 0)}

STATISTICS:
-----------
Successful Scans: {org_summary.get('successful_scans', 0)}
Failed Scans: {org_summary.get('failed_scans', 0)}
Total Components: {org_summary.get('total_components', 0)}
Total Vulnerabilities: {org_summary.get('total_vulnerabilities', 0)}

REPOSITORIES:
-------------
"""

        for repo in org_summary.get("repositories", []):
            content += f"{repo.get('name', 'Unknown')}: {repo.get('status', 'Unknown').upper()} - {repo.get('components', 0)} components, {repo.get('vulnerabilities', 0)} vulnerabilities\n"

        content += f"""\n{'=' * 60}
Generated by Firefly SBOM Tool v1.0.0 | Apache License 2.0
"""

        return content


__all__ = [
    "CycloneDXGenerator",
    "SPDXGenerator",
    "HTMLGenerator",
    "MarkdownGenerator",
    "TextGenerator",
]
