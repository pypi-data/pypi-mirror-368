"""
GitHub API utility module for repository management and authentication

Copyright 2024 Firefly OSS
Licensed under the Apache License, Version 2.0
"""

import os
from typing import Dict, List, Optional, Set
import requests
from urllib.parse import urlparse
import time

from ..utils.logger import get_logger

logger = get_logger(__name__)


class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors"""
    pass


class GitHubAPI:
    """GitHub API client with authentication support"""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub API client
        
        Args:
            token: GitHub personal access token or None for unauthenticated access
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        
        # Set up authentication headers
        if self.token:
            self.session.headers.update({
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Firefly-SBOM-Tool/1.0.0"
            })
        else:
            self.session.headers.update({
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Firefly-SBOM-Tool/1.0.0"
            })
            
        logger.info(f"GitHub API client initialized {'with authentication' if self.token else 'without authentication'}")
    
    def _make_request(self, url: str, params: Dict = None) -> Dict:
        """Make authenticated request to GitHub API with rate limit handling
        
        Args:
            url: API endpoint URL
            params: Query parameters
            
        Returns:
            JSON response data
            
        Raises:
            GitHubAPIError: If request fails
        """
        try:
            response = self.session.get(url, params=params or {})
            
            # Handle rate limiting
            if response.status_code == 403 and 'rate limit' in response.text.lower():
                reset_time = int(response.headers.get('X-RateLimit-Reset', time.time() + 60))
                wait_time = max(reset_time - int(time.time()), 1)
                logger.warning(f"Rate limit hit, waiting {wait_time} seconds...")
                time.sleep(wait_time + 1)
                response = self.session.get(url, params=params or {})
            
            if response.status_code == 401:
                raise GitHubAPIError("Authentication failed. Please check your GitHub token.")
            elif response.status_code == 403:
                raise GitHubAPIError("Access forbidden. You may not have permission to access this resource.")
            elif response.status_code == 404:
                raise GitHubAPIError("Resource not found. Please check organization/repository name.")
            elif response.status_code != 200:
                raise GitHubAPIError(f"API request failed with status {response.status_code}: {response.text}")
                
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(f"Network error: {str(e)}")
    
    def get_organization_repositories(
        self, 
        org: str, 
        repo_type: str = "all",
        include_private: bool = True,
        include_forks: bool = False,
        include_archived: bool = False
    ) -> List[Dict]:
        """Get all repositories for an organization
        
        Args:
            org: Organization name
            repo_type: Repository type filter ('all', 'public', 'private', 'member')
            include_private: Whether to include private repositories
            include_forks: Whether to include forked repositories
            include_archived: Whether to include archived repositories
            
        Returns:
            List of repository information dictionaries
        """
        repos = []
        page = 1
        per_page = 100
        
        logger.info(f"Fetching repositories for organization: {org}")
        
        while True:
            params = {
                "page": page,
                "per_page": per_page,
                "type": repo_type,
                "sort": "updated",
                "direction": "desc"
            }
            
            url = f"{self.base_url}/orgs/{org}/repos"
            data = self._make_request(url, params)
            
            if not data:
                break
                
            for repo in data:
                # Apply filters
                if not include_private and repo.get("private", False):
                    continue
                    
                if not include_forks and repo.get("fork", False):
                    continue
                    
                if not include_archived and repo.get("archived", False):
                    continue
                
                repo_info = {
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "private": repo.get("private", False),
                    "fork": repo.get("fork", False),
                    "archived": repo.get("archived", False),
                    "clone_url": repo.get("clone_url"),
                    "ssh_url": repo.get("ssh_url"),
                    "html_url": repo.get("html_url"),
                    "description": repo.get("description", ""),
                    "language": repo.get("language", "Unknown"),
                    "size": repo.get("size", 0),
                    "updated_at": repo.get("updated_at"),
                    "topics": repo.get("topics", []),
                    "default_branch": repo.get("default_branch", "main")
                }
                repos.append(repo_info)
            
            page += 1
            
        logger.info(f"Found {len(repos)} repositories in organization {org}")
        return repos
    
    def get_user_repositories(
        self,
        username: str,
        repo_type: str = "all",
        include_private: bool = True,
        include_forks: bool = False
    ) -> List[Dict]:
        """Get repositories for a specific user
        
        Args:
            username: GitHub username
            repo_type: Repository type filter ('all', 'owner', 'member')
            include_private: Whether to include private repositories
            include_forks: Whether to include forked repositories
            
        Returns:
            List of repository information dictionaries
        """
        repos = []
        page = 1
        per_page = 100
        
        logger.info(f"Fetching repositories for user: {username}")
        
        while True:
            params = {
                "page": page,
                "per_page": per_page,
                "type": repo_type,
                "sort": "updated",
                "direction": "desc"
            }
            
            url = f"{self.base_url}/users/{username}/repos"
            data = self._make_request(url, params)
            
            if not data:
                break
                
            for repo in data:
                # Apply filters
                if not include_private and repo.get("private", False):
                    continue
                    
                if not include_forks and repo.get("fork", False):
                    continue
                
                repo_info = {
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "private": repo.get("private", False),
                    "fork": repo.get("fork", False),
                    "archived": repo.get("archived", False),
                    "clone_url": repo.get("clone_url"),
                    "ssh_url": repo.get("ssh_url"),
                    "html_url": repo.get("html_url"),
                    "description": repo.get("description", ""),
                    "language": repo.get("language", "Unknown"),
                    "size": repo.get("size", 0),
                    "updated_at": repo.get("updated_at"),
                    "topics": repo.get("topics", []),
                    "default_branch": repo.get("default_branch", "main")
                }
                repos.append(repo_info)
            
            page += 1
            
        logger.info(f"Found {len(repos)} repositories for user {username}")
        return repos
    
    def get_repository_info(self, owner: str, repo: str) -> Dict:
        """Get information about a specific repository
        
        Args:
            owner: Repository owner (user or organization)
            repo: Repository name
            
        Returns:
            Repository information dictionary
        """
        url = f"{self.base_url}/repos/{owner}/{repo}"
        data = self._make_request(url)
        
        return {
            "name": data["name"],
            "full_name": data["full_name"],
            "private": data.get("private", False),
            "fork": data.get("fork", False),
            "archived": data.get("archived", False),
            "clone_url": data.get("clone_url"),
            "ssh_url": data.get("ssh_url"),
            "html_url": data.get("html_url"),
            "description": data.get("description", ""),
            "language": data.get("language", "Unknown"),
            "size": data.get("size", 0),
            "updated_at": data.get("updated_at"),
            "topics": data.get("topics", []),
            "default_branch": data.get("default_branch", "main")
        }
    
    def filter_repositories(
        self,
        repos: List[Dict],
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        languages: Optional[List[str]] = None,
        topics: Optional[List[str]] = None,
        min_size_kb: Optional[int] = None,
        max_size_kb: Optional[int] = None
    ) -> List[Dict]:
        """Filter repositories based on various criteria
        
        Args:
            repos: List of repository dictionaries to filter
            include_patterns: Repository name patterns to include (glob-style)
            exclude_patterns: Repository name patterns to exclude (glob-style)  
            languages: List of programming languages to include
            topics: List of topics that repositories must have
            min_size_kb: Minimum repository size in KB
            max_size_kb: Maximum repository size in KB
            
        Returns:
            Filtered list of repositories
        """
        import fnmatch
        
        filtered_repos = []
        
        for repo in repos:
            repo_name = repo["name"]
            
            # Include patterns filter
            if include_patterns:
                if not any(fnmatch.fnmatch(repo_name, pattern) for pattern in include_patterns):
                    continue
                    
            # Exclude patterns filter
            if exclude_patterns:
                if any(fnmatch.fnmatch(repo_name, pattern) for pattern in exclude_patterns):
                    continue
                    
            # Language filter
            if languages:
                repo_language = repo.get("language", "").lower()
                if repo_language not in [lang.lower() for lang in languages]:
                    continue
                    
            # Topics filter
            if topics:
                repo_topics = [topic.lower() for topic in repo.get("topics", [])]
                if not any(topic.lower() in repo_topics for topic in topics):
                    continue
                    
            # Size filters
            repo_size = repo.get("size", 0)
            if min_size_kb is not None and repo_size < min_size_kb:
                continue
            if max_size_kb is not None and repo_size > max_size_kb:
                continue
                
            filtered_repos.append(repo)
        
        logger.info(f"Filtered {len(repos)} repositories down to {len(filtered_repos)}")
        return filtered_repos
    
    def get_clone_url(self, repo: Dict, use_ssh: bool = False) -> str:
        """Get appropriate clone URL for repository
        
        Args:
            repo: Repository dictionary
            use_ssh: Whether to use SSH URL instead of HTTPS
            
        Returns:
            Clone URL string
        """
        if use_ssh:
            return repo["ssh_url"]
        else:
            # For private repos with authentication, use token in HTTPS URL
            if repo["private"] and self.token:
                clone_url = repo["clone_url"]
                # Replace https:// with https://token@
                return clone_url.replace("https://", f"https://{self.token}@")
            return repo["clone_url"]
    
    def validate_access(self, org: str) -> Dict[str, bool]:
        """Validate access to organization and capabilities
        
        Args:
            org: Organization name
            
        Returns:
            Dictionary with access capabilities
        """
        capabilities = {
            "org_access": False,
            "private_repos": False,
            "member_repos": False,
            "admin_access": False
        }
        
        try:
            # Test organization access
            url = f"{self.base_url}/orgs/{org}"
            org_data = self._make_request(url)
            capabilities["org_access"] = True
            
            # Test private repository access by trying to list repos
            url = f"{self.base_url}/orgs/{org}/repos"
            params = {"type": "private", "per_page": 1}
            try:
                private_repos = self._make_request(url, params)
                capabilities["private_repos"] = len(private_repos) > 0 or self.token is not None
            except GitHubAPIError:
                pass
                
            # Test member repository access
            params = {"type": "member", "per_page": 1}
            try:
                member_repos = self._make_request(url, params)
                capabilities["member_repos"] = True
            except GitHubAPIError:
                pass
                
        except GitHubAPIError as e:
            logger.warning(f"Access validation failed for {org}: {e}")
            
        return capabilities
