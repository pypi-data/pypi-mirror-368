"""
Parallel scanning utilities for efficient repository processing

Copyright 2024 Firefly OSS
Licensed under the Apache License, Version 2.0
"""

import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import git

from ..config import Config
from .logger import get_logger

logger = get_logger(__name__)


class ParallelScanner:
    """Handles parallel cloning and scanning of multiple repositories"""

    def __init__(self, config: Config, max_workers: int = 4):
        """Initialize parallel scanner"""
        self.config = config
        self.max_workers = max_workers

    def scan_repositories(
        self,
        repos: List[Dict[str, str]],
        audit: bool = False,
        include_dev: bool = False,
        progress_callback: callable = None,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Scan multiple repositories in parallel with temporary cloning

        Args:
            repos: List of repository information dicts
            audit: Whether to perform security audit
            include_dev: Whether to include dev dependencies

        Returns:
            Dictionary mapping repo names to SBOM data
        """
        results = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all repository scanning tasks
            futures = {
                executor.submit(self._scan_single_repo, repo, audit, include_dev): repo[
                    "name"
                ]
                for repo in repos
            }

            # Process completed tasks with progress tracking
            completed = 0
            total = len(repos)

            for future in as_completed(futures):
                repo_name = futures[future]
                
                # Call progress callback with current repository
                if progress_callback:
                    progress_callback(repo_name, completed, total)
                
                completed += 1

                try:
                    sbom_data = future.result()
                    results[repo_name] = sbom_data
                    logger.info(
                        f"[{completed}/{total}] Completed scanning: {repo_name}"
                    )

                except Exception as e:
                    logger.error(
                        f"[{completed}/{total}] Failed to scan {repo_name}: {e}"
                    )
                    results[repo_name] = self._empty_sbom(repo_name)

        return results

    def _scan_single_repo(
        self, repo: Dict[str, str], audit: bool, include_dev: bool
    ) -> Dict[str, Any]:
        """
        Clone and scan a single repository in a temporary directory

        Args:
            repo: Repository information dict
            audit: Whether to perform security audit
            include_dev: Whether to include dev dependencies

        Returns:
            SBOM data for the repository
        """
        repo_name = repo["name"]
        repo_url = repo["url"]

        # Create temporary directory for cloning
        with tempfile.TemporaryDirectory(prefix=f"sbom_{repo_name}_") as tmpdir:
            repo_path = Path(tmpdir) / repo_name

            try:
                # Clone repository with shallow depth for speed
                logger.debug(f"Cloning {repo_name} from {repo_url}")
                git.Repo.clone_from(repo_url, repo_path, depth=1, single_branch=True)

                # Import here to avoid circular dependency
                from ..core import SBOMGenerator

                # Create generator and scan
                generator = SBOMGenerator(self.config)
                sbom_data = generator.scan_repository(
                    path=repo_path, include_dev=include_dev, audit=audit
                )

                # Add repository metadata
                sbom_data["metadata"]["repository_name"] = repo_name
                sbom_data["metadata"]["repository_url"] = repo_url
                sbom_data["metadata"]["description"] = repo.get("description", "")
                sbom_data["metadata"]["primary_language"] = repo.get(
                    "language", "Unknown"
                )

                return sbom_data

            except git.GitCommandError as e:
                logger.error(f"Git error cloning {repo_name}: {e}")
                return self._empty_sbom(repo_name)

            except Exception as e:
                logger.error(f"Unexpected error scanning {repo_name}: {e}")
                return self._empty_sbom(repo_name)

            finally:
                # Ensure cleanup of repository directory
                if repo_path.exists():
                    try:
                        shutil.rmtree(repo_path, ignore_errors=True)
                    except Exception:
                        pass

    def _empty_sbom(self, repo_name: str) -> Dict[str, Any]:
        """Return empty SBOM structure for failed scans"""
        return {
            "metadata": {
                "repository_name": repo_name,
                "timestamp": datetime.now().isoformat(),
                "technologies": [],
                "error": "Scan failed",
                "tool": {"name": "Firefly SBOM Tool", "version": "1.0.0"},
            },
            "components": [],
            "stats": {
                "total_components": 0,
                "direct_deps": 0,
                "transitive_deps": 0,
            },
        }


class BatchProcessor:
    """Process repositories in batches for memory efficiency"""

    def __init__(self, batch_size: int = 10):
        """Initialize batch processor"""
        self.batch_size = batch_size

    def process_in_batches(self, items: List[Any], process_func, **kwargs) -> List[Any]:
        """
        Process items in batches

        Args:
            items: List of items to process
            process_func: Function to process each batch
            **kwargs: Additional arguments for process_func

        Returns:
            Combined results from all batches
        """
        results = []

        for i in range(0, len(items), self.batch_size):
            batch = items[i : i + self.batch_size]
            logger.info(
                f"Processing batch {i//self.batch_size + 1} of {len(items)//self.batch_size + 1}"
            )

            batch_results = process_func(batch, **kwargs)
            results.extend(batch_results)

        return results
