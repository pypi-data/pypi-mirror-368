"""
Git platform integrations for GitScribe.
Supports GitHub, GitLab, Bitbucket, and Azure DevOps.
"""

import os
import re
import logging
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import requests
from dataclasses import dataclass

from .config import GitScribeConfig

logger = logging.getLogger(__name__)


@dataclass
class GitRepository:
    """Represents a Git repository with metadata."""
    url: str
    platform: str
    owner: str
    repo: str
    branch: str = "main"
    docs_path: str = ""
    api_url: str = ""
    
    def __post_init__(self):
        """Initialize API URL based on platform."""
        if self.platform == "github.com":
            self.api_url = f"https://api.github.com/repos/{self.owner}/{self.repo}"
        elif self.platform == "gitlab.com":
            self.api_url = f"https://gitlab.com/api/v4/projects/{self.owner}%2F{self.repo}"


class GitIntegration:
    """Base class for Git platform integrations."""
    
    def __init__(self, config: GitScribeConfig):
        self.config = config
        self.session = requests.Session()
        
        # Setup proper headers for GitHub API
        headers = {
            "User-Agent": "GitScribe/1.0.0 (Documentation Scanner)",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        self.session.headers.update(headers)
        
        # Setup authentication if available
        self._setup_auth()
    
    def _setup_auth(self):
        """Setup authentication for Git platforms."""
        github_token = os.getenv("GITHUB_TOKEN")
        gitlab_token = os.getenv("GITLAB_TOKEN")
        
        if github_token:
            self.session.headers["Authorization"] = f"token {github_token}"
        if gitlab_token:
            self.session.headers["PRIVATE-TOKEN"] = gitlab_token
    
    def parse_git_url(self, url: str) -> Optional[GitRepository]:
        """Parse a Git URL and extract repository information."""
        # Clean up the URL
        url = url.strip().rstrip('/')
        
        # Handle different URL formats
        patterns = [
            # HTTPS URLs
            r'https://([^/]+)/([^/]+)/([^/]+)/?(?:tree/([^/]+))?(?:/(.+))?',
            # SSH URLs
            r'git@([^:]+):([^/]+)/([^/]+)\.git',
            # HTTP URLs
            r'http://([^/]+)/([^/]+)/([^/]+)/?(?:tree/([^/]+))?(?:/(.+))?'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, url)
            if match:
                groups = match.groups()
                platform = groups[0]
                owner = groups[1]
                repo = groups[2].replace('.git', '')
                branch = groups[3] if len(groups) > 3 and groups[3] else "main"
                docs_path = groups[4] if len(groups) > 4 and groups[4] else ""
                
                if platform in self.config.git_platforms:
                    return GitRepository(
                        url=url,
                        platform=platform,
                        owner=owner,
                        repo=repo,
                        branch=branch,
                        docs_path=docs_path
                    )
        
        logger.warning(f"Could not parse Git URL: {url}")
        return None
    
    def get_repository_info(self, repo: GitRepository) -> Dict:
        """Get repository information from API."""
        try:
            response = self.session.get(repo.api_url, timeout=self.config.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get repository info for {repo.url}: {e}")
            return {}
    
    def list_documentation_files(self, repo: GitRepository) -> List[Dict]:
        """List documentation files in the repository."""
        files = []
        
        if repo.platform == "github.com":
            files = self._list_github_files(repo)
        elif repo.platform == "gitlab.com":
            files = self._list_gitlab_files(repo)
        
        # Filter for documentation files
        doc_files = []
        for file in files:
            file_path = file.get('path', '')
            if self.config.is_supported_format(file_path) and not self.config.should_ignore(file_path):
                doc_files.append(file)
        
        return doc_files
    
    def _list_github_files(self, repo: GitRepository) -> List[Dict]:
        """List files from GitHub repository."""
        files = []
        try:
            # Get tree recursively
            tree_url = f"{repo.api_url}/git/trees/{repo.branch}?recursive=1"
            response = self.session.get(tree_url, timeout=self.config.timeout)
            response.raise_for_status()
            
            tree_data = response.json()
            for item in tree_data.get('tree', []):
                if item['type'] == 'blob':  # Only files, not directories
                    files.append({
                        'path': item['path'],
                        'url': item['url'],
                        'download_url': f"https://raw.githubusercontent.com/{repo.owner}/{repo.repo}/{repo.branch}/{item['path']}",
                        'size': item.get('size', 0)
                    })
        
        except requests.RequestException as e:
            logger.error(f"Failed to list GitHub files for {repo.url}: {e}")
        
        return files
    
    def _list_gitlab_files(self, repo: GitRepository) -> List[Dict]:
        """List files from GitLab repository."""
        files = []
        try:
            # Get repository tree
            tree_url = f"{repo.api_url}/repository/tree?recursive=true&ref={repo.branch}"
            response = self.session.get(tree_url, timeout=self.config.timeout)
            response.raise_for_status()
            
            tree_data = response.json()
            for item in tree_data:
                if item['type'] == 'blob':  # Only files, not directories
                    files.append({
                        'path': item['path'],
                        'url': f"{repo.api_url}/repository/files/{item['path']}/raw?ref={repo.branch}",
                        'download_url': f"{repo.api_url}/repository/files/{item['path']}/raw?ref={repo.branch}",
                        'size': item.get('size', 0)
                    })
        
        except requests.RequestException as e:
            logger.error(f"Failed to list GitLab files for {repo.url}: {e}")
        
        return files
    
    def download_file_content(self, file_info: Dict) -> Optional[str]:
        """Download file content from repository."""
        try:
            response = self.session.get(
                file_info['download_url'], 
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            # Try to decode as UTF-8, fallback to latin-1
            try:
                return response.content.decode('utf-8')
            except UnicodeDecodeError:
                return response.content.decode('latin-1', errors='ignore')
                
        except requests.RequestException as e:
            logger.error(f"Failed to download file {file_info['path']}: {e}")
            return None
    
    def discover_documentation_structure(self, repo: GitRepository) -> Dict:
        """Discover documentation structure in repository."""
        structure = {
            "repository": repo,
            "documentation_files": [],
            "readme_files": [],
            "api_docs": [],
            "code_examples": [],
            "config_files": []
        }
        
        files = self.list_documentation_files(repo)
        
        for file in files:
            path = file['path'].lower()
            
            if 'readme' in path:
                structure["readme_files"].append(file)
            elif any(api_term in path for api_term in ['api', 'swagger', 'openapi']):
                structure["api_docs"].append(file)
            elif any(example_term in path for example_term in ['example', 'sample', 'demo']):
                structure["code_examples"].append(file)
            elif any(doc_term in path for doc_term in ['doc', 'guide', 'tutorial']):
                structure["documentation_files"].append(file)
            elif path.endswith(('.json', '.yaml', '.yml', '.toml')):
                structure["config_files"].append(file)
            else:
                structure["documentation_files"].append(file)
        
        logger.info(f"Discovered {len(files)} documentation files in {repo.url}")
        return structure


class GitHubIntegration(GitIntegration):
    """Specialized GitHub integration."""
    
    def get_latest_commit_info(self, repo: GitRepository) -> Dict:
        """Get latest commit information."""
        try:
            commits_url = f"{repo.api_url}/commits/{repo.branch}"
            response = self.session.get(commits_url, timeout=self.config.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get commit info for {repo.url}: {e}")
            return {}
    
    def check_rate_limit(self) -> Dict:
        """Check GitHub API rate limits."""
        try:
            response = self.session.get("https://api.github.com/rate_limit")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to check rate limit: {e}")
            return {}


class GitLabIntegration(GitIntegration):
    """Specialized GitLab integration."""
    
    def get_latest_commit_info(self, repo: GitRepository) -> Dict:
        """Get latest commit information."""
        try:
            commits_url = f"{repo.api_url}/repository/commits/{repo.branch}"
            response = self.session.get(commits_url, timeout=self.config.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get commit info for {repo.url}: {e}")
            return {}


def create_git_integration(config: GitScribeConfig, platform: str = None) -> GitIntegration:
    """Factory function to create appropriate Git integration."""
    if platform == "github.com":
        return GitHubIntegration(config)
    elif platform == "gitlab.com":
        return GitLabIntegration(config)
    else:
        return GitIntegration(config)
