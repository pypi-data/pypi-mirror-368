# Firefly SBOM Tool 🔒

<div align="center">

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![GitHub Stars](https://img.shields.io/github/stars/firefly-oss/sbom-tool?style=social)](https://github.com/firefly-oss/sbom-tool)
[![Docker Pulls](https://img.shields.io/docker/pulls/fireflyoss/sbom-tool)](https://hub.docker.com/r/fireflyoss/sbom-tool)

**A comprehensive Software Bill of Materials (SBOM) generation and security auditing tool for modern multi-technology stacks**

[Quick Installation](#-quick-installation) • [Quick Start](#-quick-start) • [Key Features](#-key-features) • [Documentation](docs/) • [Contributing](docs/CONTRIBUTING.md)

</div>

---

## 🎯 Overview

The **Firefly SBOM Tool** is an enterprise-grade solution for generating Software Bill of Materials (SBOM) documents and performing comprehensive security audits across multiple programming languages and frameworks.

**🆕 NEW: GitHub Organization Scanning with parallel processing and advanced filtering!**

## ⭐ Key Features

- 🐙 **GitHub Organization Scanning** - Scan entire organizations with filtering by language, topics, type
- 🚀 **Parallel Processing** - High-performance scanning with configurable workers
- 📦 **Multi-Language Support** - Python, Java, Node.js, Go, Ruby, Rust, Flutter/Dart, and more
- 🛡️ **Security Auditing** - Vulnerability scanning using NVD, OSV, and GitHub Security Advisories
- 📊 **Rich Reports** - Interactive HTML, CycloneDX, SPDX, Markdown formats
- ⚡ **High Performance** - Efficient caching and batch processing
- 🐳 **Container Ready** - Full Docker support
- ⚙️ **CI/CD Integration** - GitHub Actions, GitLab CI, Jenkins ready

## 📦 Quick Installation

```bash
# Quick install (recommended)
curl -sSL https://raw.githubusercontent.com/firefly-oss/sbom-tool/main/install.sh | bash

# From PyPI
pip install firefly-sbom-tool

# From source
git clone https://github.com/firefly-oss/sbom-tool.git && cd sbom-tool && pip install -e .

# Docker
docker pull ghcr.io/firefly-oss/sbom-tool:latest
```

## 🚀 Quick Start

### CI: GitHub Actions (Quick Example)
Add this workflow to .github/workflows/sbom.yml in your repository to run the scan on every push/PR:

```yaml
name: SBOM Scan

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:

jobs:
  sbom:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Install Firefly SBOM Tool
        run: pip install firefly-sbom-tool
      - name: Run SBOM scan (current repo)
        run: firefly-sbom scan --path . --audit --format cyclonedx-json --format html --output sbom-report
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: sbom-reports
          path: sbom-report*
```

For advanced CI usage, see the dedicated guide: docs/ci/github-actions.md.

### Single Repository Scan
```bash
# Basic scan
firefly-sbom scan --path ./my-project

# With security audit
firefly-sbom scan --path ./my-project --audit --format html
```

### 🆕 GitHub Organization Scan  
```bash
# Set GitHub token
export GITHUB_TOKEN="your_token_here"

# Scan entire organization
firefly-sbom scan-org --org firefly-oss --parallel 8 --audit

# Advanced filtering
firefly-sbom scan-org --org firefly-oss \
  --languages Python JavaScript \
  --topics microservice api \
  --include-private --no-forks --no-archived \
  --format html --format cyclonedx-json
```

### Technology Detection
```bash
# Detect tech stack
firefly-sbom detect --path ./my-project
```

## 🛠️ Supported Technologies

| Language | Package Managers | Lock Files | Status |
|----------|------------------|------------|--------|
| **Python** | pip, Poetry, Pipenv | requirements.txt, poetry.lock | ✅ Full support |
| **Java** | Maven | pom.xml | ✅ Multi-module support, improved license extraction |
| **Node.js** | npm, yarn, pnpm | package-lock.json, yarn.lock | ✅ Framework detection |
| **Go** | go modules | go.mod, go.sum | ✅ Replace directives |
| **Ruby** | Bundler | Gemfile.lock | ✅ Group dependencies |
| **Rust** | Cargo | Cargo.lock | ✅ Workspace support |
| **Flutter/Dart** | pub | pubspec.lock | ✅ SDK version tracking |

## 📚 Documentation

Comprehensive documentation is available in the [`docs/`](docs/) directory:

- **[Installation Guide](docs/installation.md)** - Detailed installation methods
- **[GitHub Integration](docs/github-integration.md)** - Organization scanning guide  
- **[Configuration](docs/configuration.md)** - Complete configuration reference
- **[API Reference](docs/api-reference.md)** - Python API documentation
- **[Examples](docs/examples/)** - Usage examples and templates

### Quick Links
- **[Getting Started](docs/#-quick-links)** - Jump right in
- **[GitHub API Setup](docs/github-integration.md#-setup)** - Token configuration
- **[CI/CD Examples](docs/configuration.md#cicd-configuration)** - Pipeline templates
- **[Changelog](docs/CHANGELOG.md)** - Version history

## 🐳 Docker Usage

```bash
# Scan current directory
docker run --rm -v $(pwd):/workspace ghcr.io/firefly-oss/sbom-tool:latest scan --path /workspace

# Organization scan with GitHub token
docker run --rm -e GITHUB_TOKEN=$GITHUB_TOKEN -v $(pwd)/reports:/reports \
  ghcr.io/firefly-oss/sbom-tool:latest scan-org --org firefly-oss --output-dir /reports
```

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](docs/CONTRIBUTING.md) for details.

```bash
# Development setup
git clone https://github.com/firefly-oss/sbom-tool.git
cd sbom-tool
python -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
pytest
```

## 📄 License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.

---

<div align="center">

**Made with ❤️ by the Firefly OSS Team**

[📚 Documentation](docs/) • [🐛 Issues](https://github.com/firefly-oss/sbom-tool/issues) • [💬 Discussions](https://github.com/firefly-oss/sbom-tool/discussions)

</div>
