"""
CLI interface for Firefly SBOM Tool

Copyright 2024 Firefly OSS
Licensed under the Apache License, Version 2.0
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import click
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from . import __version__
from .config import Config
from .core import SBOMGenerator
from .utils.logger import setup_logger

console = Console()
logger = setup_logger()


@click.group()
@click.version_option(version=__version__, prog_name="firefly-sbom")
@click.option(
    "--config", "-c", type=click.Path(exists=True), help="Configuration file path"
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx, config, verbose):
    """Firefly SBOM Tool - Generate Software Bill of Materials for multi-tech repositories"""
    ctx.ensure_object(dict)

    if config:
        ctx.obj["config"] = Config.from_file(config)
    else:
        ctx.obj["config"] = Config()

    ctx.obj["verbose"] = verbose

    if verbose:
        console.print(f"[cyan]Firefly SBOM Tool v{__version__}[/cyan]")


@cli.command()
@click.option(
    "--path",
    "-p",
    type=click.Path(exists=True),
    required=True,
    help="Repository path to scan",
)
@click.option(
    "--format",
    "-f",
    multiple=True,
    type=click.Choice(
        ["cyclonedx-json", "cyclonedx-xml", "spdx-json", "spdx-yaml", "html", "all"]
    ),
    default=["cyclonedx-json"],
    help="Output format for SBOM (can specify multiple)",
)
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--audit", is_flag=True, help="Enable security audit")
@click.option("--include-dev", is_flag=True, help="Include development dependencies")
@click.pass_context
def scan(ctx, path, format, output, audit, include_dev):
    """Scan a single repository and generate SBOM"""
    config = ctx.obj["config"]
    verbose = ctx.obj["verbose"]

    console.print(f"\n[bold green]Scanning repository:[/bold green] {path}")

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Analyzing dependencies...", total=None)

            generator = SBOMGenerator(config)
            sbom_data = generator.scan_repository(
                path=Path(path), include_dev=include_dev, audit=audit
            )

            progress.update(task, description="Generating SBOM report...")

            if "all" in format:
                formats = [
                    "cyclonedx-json",
                    "cyclonedx-xml",
                    "spdx-json",
                    "spdx-yaml",
                    "html",
                ]
            else:
                formats = list(format)

            for fmt in formats:
                output_path = generator.generate_report(
                    sbom_data=sbom_data, format=fmt, output_path=output
                )
                console.print(f"[green]✓[/green] Generated {fmt} report: {output_path}")

            progress.update(task, description="Complete!", completed=True)

        # Display summary
        _display_summary(sbom_data, audit)

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        if verbose:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.option("--org", "-o", required=True, help="GitHub organization name")
@click.option(
    "--output-dir",
    "-d",
    type=click.Path(),
    default="./sbom-reports",
    help="Output directory for reports",
)
@click.option(
    "--repos",
    "-r",
    multiple=True,
    help="Specific repositories to scan (can specify multiple). If not provided, scans all repositories",
)
@click.option(
    "--repos-file",
    type=click.Path(exists=True),
    help="File containing list of repositories to scan (one per line)",
)
@click.option(
    "--format",
    "-f",
    multiple=True,
    type=click.Choice(
        [
            "cyclonedx-json",
            "cyclonedx-xml",
            "spdx-json",
            "spdx-yaml",
            "html",
            "markdown",
            "text",
            "json",
        ]
    ),
    default=["html", "json", "markdown"],
    help="Output formats (can specify multiple)",
)
@click.option("--audit", is_flag=True, help="Enable security audit")
@click.option("--include-dev", is_flag=True, help="Include development dependencies")
@click.option(
    "--include-private/--no-private",
    default=True,
    help="Include private repositories (requires GitHub token with appropriate permissions)",
)
@click.option(
    "--include-forks/--no-forks",
    default=False,
    help="Include forked repositories",
)
@click.option(
    "--include-archived/--no-archived",
    default=False,
    help="Include archived repositories",
)
@click.option(
    "--languages",
    multiple=True,
    help="Filter repositories by programming language (can specify multiple)",
)
@click.option(
    "--topics",
    multiple=True,
    help="Filter repositories by topic/tag (can specify multiple)",
)
@click.option(
    "--github-token",
    help="GitHub personal access token (can also be set via GITHUB_TOKEN env var)",
)
@click.option(
    "--parallel", "-p", type=int, default=4, help="Number of parallel workers"
)
@click.option(
    "--combined/--no-combined",
    default=True,
    help="Generate combined organization report",
)
@click.option(
    "--batch-size", type=int, default=10, help="Batch size for processing repositories"
)
@click.pass_context
def scan_org(
    ctx, 
    org, 
    output_dir, 
    repos, 
    repos_file, 
    format, 
    audit, 
    include_dev, 
    include_private, 
    include_forks, 
    include_archived, 
    languages, 
    topics, 
    github_token, 
    parallel, 
    combined, 
    batch_size
):
    """🏢 Scan all repositories in a GitHub organization with parallel processing"""
    config = ctx.obj["config"]
    verbose = ctx.obj["verbose"]
    
    # Override GitHub token if provided via CLI
    if github_token:
        config.github_token = github_token
    
    # Prepare repository filter list
    repo_filter = None
    if repos:
        repo_filter = list(repos)
    elif repos_file:
        # Read repositories from file
        with open(repos_file, 'r') as f:
            repo_filter = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        console.print(f"[cyan]📄 Loaded {len(repo_filter)} repositories from file[/cyan]")
    
    # Build filter description for display
    filter_desc = []
    if repo_filter:
        filter_desc.append(f"Specific repos: {len(repo_filter)} selected")
    else:
        filter_desc.append("All repositories")
    
    if not include_private:
        filter_desc.append("Public only")
    if include_forks:
        filter_desc.append("Including forks")
    if include_archived:
        filter_desc.append("Including archived")
    if languages:
        filter_desc.append(f"Languages: {', '.join(languages)}")
    if topics:
        filter_desc.append(f"Topics: {', '.join(topics)}")
    
    # Show scan configuration
    config_text = f"""[bold cyan]Organization Scan Configuration[/bold cyan]
        
🏢 Organization: [bold]{org}[/bold]
📂 Output Directory: [bold]{output_dir}[/bold]
📄 Formats: [bold]{', '.join(format) if format else 'html, json, markdown'}[/bold]
🔍 Security Audit: [bold]{'Enabled' if audit else 'Disabled'}[/bold]
⚡ Parallel Workers: [bold]{parallel}[/bold]
📦 Include Dev Dependencies: [bold]{'Yes' if include_dev else 'No'}[/bold]
📊 Combined Report: [bold]{'Yes' if combined else 'No'}[/bold]
🔒 Authentication: [bold]{'GitHub Token' if (github_token or config.github_token) else 'Public Access'}[/bold]
🎯 Repository Filter: [bold]{'; '.join(filter_desc)}[/bold]"""
    
    console.print(
        Panel.fit(
            config_text,
            title="Scan Settings",
            border_style="bright_blue",
        )
    )

    try:
        # Initialize generator with spinner
        with console.status("[bold green]Initializing SBOM generator...") as status:
            generator = SBOMGenerator(config)

            # Fetch repositories
            status.update("[bold yellow]Fetching organization repositories...")
            repos = generator.list_org_repositories(
                org=org,
                repo_filter=repo_filter,
                include_private=include_private,
                include_forks=include_forks,
                include_archived=include_archived,
                languages=list(languages) if languages else None,
                topics=list(topics) if topics else None
            )

            if not repos:
                console.print("[red]✗[/red] No repositories found in organization")
                return

        # Display repository summary
        repo_table = Table(title=f"Found {len(repos)} Repositories in {org}")
        repo_table.add_column("Repository", style="cyan", no_wrap=True)
        repo_table.add_column("Primary Language", style="magenta")
        repo_table.add_column("Description", style="dim", overflow="fold")

        for repo in repos[:10]:  # Show first 10
            repo_table.add_row(
                repo["name"],
                repo.get("language", "Unknown"),
                repo.get("description", "")[:50],
            )

        if len(repos) > 10:
            repo_table.add_row("...", f"and {len(repos) - 10} more", "")

        console.print(repo_table)
        console.print()

        # Start parallel scanning with progress tracking
        console.print(
            f"[bold green]🚀 Starting parallel scan with {parallel} workers...[/bold green]\n"
        )

        # Create progress tracking
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            "•",
            TextColumn("[bold blue]{task.completed}/{task.total} repositories"),
            console=console,
        ) as progress:
            # Add main scanning task
            scan_task = progress.add_task(
                "🔍 Scanning repositories...", 
                total=len(repos)
            )
            
            # Use enhanced organization scan method with progress callback
            def progress_callback(current_repo, completed, total):
                try:
                    # Handle None repo name safely
                    repo_name = str(current_repo) if current_repo is not None else "unknown"
                    description = f"🔍 Scanning {repo_name}..."
                    
                    progress.update(
                        scan_task, 
                        completed=completed,
                        description=description
                    )
                except Exception as e:
                    # Print error for debugging and fallback
                    console.print(f"[yellow]Progress callback error: {e}[/yellow]")
                    try:
                        progress.update(scan_task, completed=completed)
                    except Exception:
                        pass  # Silently ignore if even basic update fails
            
            org_summary = generator.scan_organization(
                org=org,
                output_dir=Path(output_dir),
                audit=audit,
                include_dev=include_dev,
                parallel=parallel,
                formats=list(format) if format else ["html", "json", "markdown"],
                combined_report=combined,
                progress_callback=progress_callback,
            )
            
            # Final update
            progress.update(
                scan_task,
                completed=len(repos),
                description="✅ Scan completed!"
            )

        # Display results summary
        _display_org_scan_results(org_summary)

        console.print(f"\n[bold green]✅ Scan complete![/bold green]")
        console.print(f"📁 Reports saved to: [bold cyan]{output_dir}[/bold cyan]")

        # Show quick stats
        stats_table = Table(show_header=False, box=None)
        stats_table.add_column(style="cyan")
        stats_table.add_column(style="bold")

        stats_table.add_row(
            "Total Components:", str(org_summary.get("total_components", 0))
        )
        stats_table.add_row(
            "Total Vulnerabilities:", str(org_summary.get("total_vulnerabilities", 0))
        )
        stats_table.add_row(
            "Successful Scans:",
            f"{org_summary.get('successful_scans', 0)}/{org_summary.get('total_repositories', 0)}",
        )

        console.print(
            Panel(stats_table, title="Summary Statistics", border_style="green")
        )

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Scan interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]❌ Error:[/red] {str(e)}")
        if verbose:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.option(
    "--path", "-p", type=click.Path(exists=True), required=True, help="Repository path"
)
def detect(path):
    """Detect technology stack in a repository"""
    console.print(f"\n[bold green]Detecting technology stack in:[/bold green] {path}")

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Scanning for technology stack files...", total=None)
            
            generator = SBOMGenerator(Config())
            tech_stack = generator.detect_technology_stack(Path(path))
            
            progress.update(task, description="Analysis complete!", completed=True)

        table = Table(title="Detected Technologies")
        table.add_column("Technology", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Files Found", style="green")

        for tech in tech_stack:
            table.add_row(
                tech["name"],
                tech["type"],
                ", ".join(tech["files"][:3])
                + ("..." if len(tech["files"]) > 3 else ""),
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)


@cli.command()
@click.option(
    "--template",
    "-t",
    type=click.Choice(["basic", "github-actions", "gitlab-ci", "jenkins"]),
    default="basic",
    help="Configuration template type",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default=".sbom-config.yaml",
    help="Output file path",
)
def init(template, output):
    """Initialize configuration file"""
    templates = {
        "basic": {
            "scan": {
                "include_dev_dependencies": False,
                "max_depth": 5,
                "parallel_workers": 4,
                "ignore_patterns": [
                    "*.test.*",
                    "*.spec.*",
                    "node_modules/",
                    "venv/",
                    ".git/",
                ],
            },
            "audit": {
                "vulnerability_databases": ["nvd", "osv", "ghsa"],
                "fail_on_critical": True,
                "severity_threshold": "medium",
            },
            "output": {
                "formats": ["cyclonedx-json", "html"],
                "include_metadata": True,
                "timestamp": True,
            },
        },
        "github-actions": {
            "scan": {
                "include_dev_dependencies": False,
                "max_depth": 5,
                "parallel_workers": 4,
            },
            "audit": {
                "vulnerability_databases": ["nvd", "osv", "ghsa"],
                "fail_on_critical": True,
                "create_issues": True,
                "issue_labels": ["security", "dependencies"],
            },
            "output": {
                "formats": ["cyclonedx-json", "spdx-json"],
                "artifact_retention_days": 30,
                "upload_to_github": True,
            },
            "github": {
                "token": "${{ secrets.GITHUB_TOKEN }}",
                "create_pr_on_vulnerabilities": True,
            },
        },
    }

    config = templates.get(template, templates["basic"])

    with open(output, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    console.print(f"[green]✓[/green] Created configuration file: {output}")
    console.print(f"[cyan]Template:[/cyan] {template}")


def _display_summary(sbom_data, audit):
    """Display SBOM summary"""
    table = Table(title="SBOM Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("Total Components", str(len(sbom_data.get("components", []))))
    table.add_row(
        "Direct Dependencies", str(sbom_data.get("stats", {}).get("direct_deps", 0))
    )
    table.add_row(
        "Transitive Dependencies",
        str(sbom_data.get("stats", {}).get("transitive_deps", 0)),
    )

    if audit and "vulnerabilities" in sbom_data:
        vulns = sbom_data["vulnerabilities"]
        table.add_row("Total Vulnerabilities", str(len(vulns)))
        table.add_row(
            "Critical", str(sum(1 for v in vulns if v.get("severity") == "critical"))
        )
        table.add_row("High", str(sum(1 for v in vulns if v.get("severity") == "high")))
        table.add_row(
            "Medium", str(sum(1 for v in vulns if v.get("severity") == "medium"))
        )
        table.add_row("Low", str(sum(1 for v in vulns if v.get("severity") == "low")))

    # License summary
    licenses = {}
    for comp in sbom_data.get("components", []):
        license_name = comp.get("license", "Unknown")
        licenses[license_name] = licenses.get(license_name, 0) + 1

    table.add_row("Unique Licenses", str(len(licenses)))
    table.add_row(
        "Most Common License",
        max(licenses.items(), key=lambda x: x[1])[0] if licenses else "N/A",
    )

    console.print("\n")
    console.print(table)


def _display_org_scan_results(org_summary):
    """Display organization scan results in a formatted table"""
    if not org_summary or "repositories" not in org_summary:
        return

    # Create results table
    table = Table(title="Repository Scan Results")
    table.add_column("Repository", style="cyan", no_wrap=True)
    table.add_column("Status", style="magenta")
    table.add_column("Components", style="green", justify="right")
    table.add_column("Vulnerabilities", style="red", justify="right")
    table.add_column("Technologies", style="blue")

    for repo in org_summary.get("repositories", []):
        status_icon = "✓" if repo["status"] == "success" else "✗"
        status_color = "green" if repo["status"] == "success" else "red"

        table.add_row(
            repo["name"],
            f"[{status_color}]{status_icon} {repo['status']}[/{status_color}]",
            str(repo.get("components", 0)),
            str(repo.get("vulnerabilities", 0)),
            ", ".join(repo.get("technologies", [])[:3]),
        )

    console.print(table)


def _generate_org_report(org, results, output_path):
    """Generate organization-wide summary report"""
    summary = {
        "organization": org,
        "scan_date": datetime.now().isoformat(),
        "total_repositories": len(results),
        "successful_scans": sum(1 for r in results if r["status"] == "success"),
        "failed_scans": sum(1 for r in results if r["status"] == "failed"),
        "total_components": sum(
            r.get("components", 0) for r in results if r["status"] == "success"
        ),
        "total_vulnerabilities": sum(
            r.get("vulnerabilities", 0) for r in results if r["status"] == "success"
        ),
        "repositories": results,
    }

    # Save JSON summary
    with open(output_path / "org-summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    # Display summary table
    table = Table(title=f"Organization Scan Summary: {org}")
    table.add_column("Repository", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Components", style="green")
    table.add_column("Vulnerabilities", style="red")

    for result in results:
        status_color = "green" if result["status"] == "success" else "red"
        table.add_row(
            result["repo"],
            f"[{status_color}]{result['status']}[/{status_color}]",
            str(result.get("components", "-")),
            str(result.get("vulnerabilities", "-")),
        )

    console.print("\n")
    console.print(table)


def main():
    """Main entry point"""
    cli(obj={})


if __name__ == "__main__":
    main()
