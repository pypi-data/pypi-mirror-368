from typing import List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict

class CommitClusterer:
    def __init__(self, time_window_hours: int = 24):
        self.time_window = timedelta(hours=time_window_hours)

    def cluster_commits(self, commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Cluster commits based on time proximity and author."""
        if not commits:
            return []

        # Sort commits by date
        sorted_commits = sorted(commits, key=lambda x: datetime.fromisoformat(x['date']))
        clusters = []
        current_cluster = []

        for commit in sorted_commits:
            if not current_cluster:
                current_cluster.append(commit)
                continue

            last_commit = current_cluster[-1]
            last_date = datetime.fromisoformat(last_commit['date'])
            current_date = datetime.fromisoformat(commit['date'])
            
            # Check if commits are close in time and from same author
            if (current_date - last_date <= self.time_window and 
                commit['author'] == last_commit['author']):
                current_cluster.append(commit)
            else:
                if len(current_cluster) > 1:
                    clusters.append(self._create_cluster_info(current_cluster))
                current_cluster = [commit]

        # Add the last cluster if it has multiple commits
        if len(current_cluster) > 1:
            clusters.append(self._create_cluster_info(current_cluster))

        return clusters

    def _create_cluster_info(self, commits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a summary of a commit cluster."""
        start_date = datetime.fromisoformat(commits[0]['date'])
        end_date = datetime.fromisoformat(commits[-1]['date'])
        
        return {
            'author': commits[0]['author'],
            'start_date': commits[0]['date'],
            'end_date': commits[-1]['date'],
            'duration_hours': (end_date - start_date).total_seconds() / 3600,
            'commit_count': len(commits),
            'total_insertions': sum(c['insertions'] for c in commits),
            'total_deletions': sum(c['deletions'] for c in commits),
            'files_changed': list(set(f for c in commits for f in c['files_changed'])),
            'commits': commits
        } 