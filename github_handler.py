import os
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict
import git
import re
from urllib.parse import urlparse

class GitHubHandler:
    def __init__(self):
        self.temp_dirs = []
    
    def clone_repository(self, repo_url: str, branch: str = "main") -> Optional[str]:
        """Clone a GitHub repository to a temporary directory"""
        try:
            # Validate and normalize the URL
            normalized_url = self._normalize_github_url(repo_url)
            if not normalized_url:
                raise ValueError("Invalid GitHub repository URL")
            
            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix="github_repo_")
            self.temp_dirs.append(temp_dir)
            
            # Clone the repository
            try:
                repo = git.Repo.clone_from(normalized_url, temp_dir)
                
                # Try to checkout the specified branch
                try:
                    repo.git.checkout(branch)
                except git.exc.GitCommandError:
                    # If branch doesn't exist, try 'master'
                    if branch == "main":
                        try:
                            repo.git.checkout("master")
                        except git.exc.GitCommandError:
                            # Use whatever branch is default
                            pass
            except git.exc.GitCommandError as e:
                if "Authentication failed" in str(e):
                    raise ValueError("Repository is private or requires authentication")
                elif "not found" in str(e):
                    raise ValueError("Repository not found")
                else:
                    raise ValueError(f"Failed to clone repository: {str(e)}")
            
            return temp_dir
            
        except Exception as e:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            raise e
    
    def _normalize_github_url(self, url: str) -> Optional[str]:
        """Normalize GitHub URL to HTTPS format"""
        url = url.strip()
        
        # Handle various GitHub URL formats
        patterns = [
            r"https://github\.com/([^/]+)/([^/]+)(?:\.git)?/?$",
            r"git@github\.com:([^/]+)/([^/]+)(?:\.git)?$",
            r"github\.com/([^/]+)/([^/]+)/?$",
            r"^([^/]+)/([^/]+)$"  # Just owner/repo format
        ]
        
        for pattern in patterns:
            match = re.match(pattern, url)
            if match:
                owner, repo = match.groups()
                # Remove .git suffix if present
                if repo.endswith('.git'):
                    repo = repo[:-4]
                return f"https://github.com/{owner}/{repo}.git"
        
        return None
    
    def get_repository_info(self, repo_path: str) -> Dict:
        """Extract repository information"""
        try:
            repo = git.Repo(repo_path)
            
            # Get remote URL
            remote_url = None
            try:
                remote_url = repo.remotes.origin.url
                if remote_url.startswith('git@'):
                    # Convert SSH to HTTPS
                    remote_url = remote_url.replace('git@github.com:', 'https://github.com/')
                if remote_url.endswith('.git'):
                    remote_url = remote_url[:-4]
            except:
                pass
            
            # Get current branch
            try:
                current_branch = repo.active_branch.name
            except:
                current_branch = "unknown"
            
            # Get last commit info
            try:
                last_commit = repo.head.commit
                commit_info = {
                    'hash': last_commit.hexsha[:8],
                    'message': last_commit.message.strip(),
                    'author': str(last_commit.author),
                    'date': last_commit.committed_datetime.strftime("%Y-%m-%d %H:%M:%S")
                }
            except:
                commit_info = {}
            
            # Parse owner/repo from URL
            owner, repo_name = "unknown", "unknown"
            if remote_url:
                try:
                    parts = remote_url.replace('https://github.com/', '').split('/')
                    if len(parts) >= 2:
                        owner, repo_name = parts[0], parts[1]
                except:
                    pass
            
            return {
                'remote_url': remote_url,
                'owner': owner,
                'repo_name': repo_name,
                'branch': current_branch,
                'last_commit': commit_info,
                'local_path': repo_path
            }
        except:
            return {
                'remote_url': None,
                'owner': 'unknown',
                'repo_name': Path(repo_path).name,
                'branch': 'unknown',
                'last_commit': {},
                'local_path': repo_path
            }
    
    def cleanup(self):
        """Clean up all temporary directories"""
        for temp_dir in self.temp_dirs:
            if os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass
        self.temp_dirs.clear()
    
    def __del__(self):
        """Cleanup on destruction"""
        self.cleanup()
    
    def is_valid_github_url(self, url: str) -> bool:
        """Check if the URL appears to be a valid GitHub repository URL"""
        return self._normalize_github_url(url) is not None
    
    def extract_repo_details_from_url(self, url: str) -> Optional[Dict[str, str]]:
        """Extract owner and repo name from GitHub URL"""
        normalized = self._normalize_github_url(url)
        if not normalized:
            return None
        
        match = re.match(r"https://github\.com/([^/]+)/([^/]+)\.git", normalized)
        if match:
            return {
                'owner': match.group(1),
                'repo': match.group(2),
                'url': normalized
            }
        return None