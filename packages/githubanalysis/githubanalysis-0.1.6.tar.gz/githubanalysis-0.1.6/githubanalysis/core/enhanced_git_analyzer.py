from git import Repo
from typing import List, Dict, Any
from datetime import datetime
import tempfile
import shutil
import os
import re

class EnhancedGitAnalyzer:
    def __init__(self, repo_url: str, start_date: str = None, end_date: str = None):
        self.repo_url = repo_url
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
        self.temp_dir = None
        self.repo = None

    def __enter__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.repo = Repo.clone_from(self.repo_url, self.temp_dir)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.temp_dir:
            shutil.rmtree(self.temp_dir)

    def extract_all_commits(self) -> List[Dict[str, Any]]:
        """Extract all commits from the repository within the date range."""
        commits = []
        for commit in self.repo.iter_commits():
            commit_date = datetime.fromtimestamp(commit.committed_date)
            
            # Apply date filters if specified
            if self.start_date and commit_date < self.start_date:
                continue
            if self.end_date and commit_date > self.end_date:
                continue

            commits.append({
                'hash': commit.hexsha,
                'author': commit.author.name,
                'email': commit.author.email,
                'date': commit_date.isoformat(),
                'message': commit.message,
                'files_changed': list(commit.stats.files.keys()),
                'insertions': commit.stats.total['insertions'],
                'deletions': commit.stats.total['deletions']
            })
        
        return commits

    def get_repository_name(self) -> str:
        """Get the repository name from the URL."""
        return os.path.basename(self.repo_url).replace('.git', '') 

    def get_commit_url(self, commit_hash: str) -> str:
        """Generate the web URL for a commit given its hash."""
        # Support GitHub and GitLab style URLs
        if self.repo_url.startswith('git@'):
            # SSH URL: git@github.com:user/repo.git
            match = re.match(r'git@([^:]+):([^/]+)/([^/]+)\.git', self.repo_url)
            if match:
                host, user, repo = match.groups()
                return f"https://{host}/{user}/{repo}/commit/{commit_hash}"
        elif self.repo_url.startswith('http'):
            # HTTPS URL: https://github.com/user/repo.git
            match = re.match(r'https?://([^/]+)/([^/]+)/([^/]+)\.git', self.repo_url)
            if match:
                host, user, repo = match.groups()
                return f"https://{host}/{user}/{repo}/commit/{commit_hash}"
        # Fallback: just return the hash
        return commit_hash 