"""
Copyright 2024 Firefly OSS

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

try:
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    # Fallback to minimal runtime requirements if requirements.txt is not present when building from sdist
    requirements = [
        "click>=8.0",
        "PyYAML>=6.0",
        "requests>=2.31",
        "rich>=13.0",
        "Jinja2>=3.1",
        "cyclonedx-python-lib>=6.4",
        "spdx-tools>=0.8",
        "packageurl-python>=0.11",
        "pip-audit>=2.7",
        "pandas>=2.0",
        "tabulate>=0.9",
        "GitPython>=3.1",
    ]

setup(
    name="firefly-sbom-tool",
    version="1.0.0",
    author="Firefly OSS",
    author_email="oss@firefly.com",
    description="Comprehensive SBOM generation and auditing tool for Firefly Open Banking Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/firefly-oss/sbom-tool",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Security",
        "Topic :: System :: Software Distribution",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "firefly-sbom=firefly_sbom.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "firefly_sbom": ["templates/*.html", "templates/*.css"],
    },
)
