from typing import List, Dict, Any
from collections import defaultdict
from datetime import datetime, timedelta

class ContributorAnalyzer:
    def __init__(self):
        self.activity_threshold = timedelta(days=30)  # Consider active within 30 days

    def analyze_contributors(self, commits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze contributor patterns and metrics."""
        if not commits:
            return self._create_empty_analysis()

        # Group commits by author
        author_commits = defaultdict(list)
        for commit in commits:
            author_commits[commit['author']].append(commit)

        # Calculate metrics for each author
        author_metrics = {}
        for author, author_commits_list in author_commits.items():
            author_metrics[author] = self._calculate_author_metrics(author_commits_list)

        # Calculate team metrics
        team_metrics = self._calculate_team_metrics(author_metrics, commits)

        return {
            'team_metrics': team_metrics,
            'contributor_details': author_metrics,
            'collaboration_patterns': self._analyze_collaboration(commits)
        }

    def _calculate_author_metrics(self, commits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate metrics for a single contributor."""
        if not commits:
            return {}

        # Sort commits by date
        sorted_commits = sorted(commits, key=lambda x: datetime.fromisoformat(x['date']))
        first_commit = datetime.fromisoformat(sorted_commits[0]['date'])
        last_commit = datetime.fromisoformat(sorted_commits[-1]['date'])
        
        # Calculate time-based metrics
        total_days = (last_commit - first_commit).days + 1
        commit_frequency = len(commits) / max(total_days, 1)
        
        # Calculate activity metrics
        total_insertions = sum(c['insertions'] for c in commits)
        total_deletions = sum(c['deletions'] for c in commits)
        files_changed = set(f for c in commits for f in c['files_changed'])
        
        # Calculate recent activity
        now = datetime.now()
        recent_commits = [c for c in commits 
                         if (now - datetime.fromisoformat(c['date'])) <= self.activity_threshold]
        
        return {
            'commit_count': len(commits),
            'first_commit': sorted_commits[0]['date'],
            'last_commit': sorted_commits[-1]['date'],
            'commit_frequency': round(commit_frequency, 2),
            'total_insertions': total_insertions,
            'total_deletions': total_deletions,
            'files_changed': len(files_changed),
            'recent_activity': len(recent_commits),
            'is_active': len(recent_commits) > 0
        }

    def _calculate_team_metrics(self, author_metrics: Dict[str, Dict[str, Any]], 
                              commits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate team-level metrics."""
        total_contributors = len(author_metrics)
        active_contributors = sum(1 for m in author_metrics.values() if m.get('is_active', False))
        
        # Calculate team activity metrics
        total_commits = sum(m['commit_count'] for m in author_metrics.values())
        total_insertions = sum(m['total_insertions'] for m in author_metrics.values())
        total_deletions = sum(m['total_deletions'] for m in author_metrics.values())
        
        # Calculate team health metrics
        if total_contributors > 0:
            activity_ratio = active_contributors / total_contributors
            commit_distribution = self._calculate_commit_distribution(author_metrics)
        else:
            activity_ratio = 0
            commit_distribution = {'high': 0, 'medium': 0, 'low': 0}

        return {
            'total_contributors': total_contributors,
            'active_contributors': active_contributors,
            'activity_ratio': round(activity_ratio, 2),
            'total_commits': total_commits,
            'total_insertions': total_insertions,
            'total_deletions': total_deletions,
            'commit_distribution': commit_distribution
        }

    def _calculate_commit_distribution(self, author_metrics: Dict[str, Dict[str, Any]]) -> Dict[str, int]:
        """Calculate the distribution of commit activity among contributors."""
        commit_counts = [m['commit_count'] for m in author_metrics.values()]
        if not commit_counts:
            return {'high': 0, 'medium': 0, 'low': 0}
            
        avg_commits = sum(commit_counts) / len(commit_counts)
        return {
            'high': sum(1 for c in commit_counts if c > avg_commits * 1.5),
            'medium': sum(1 for c in commit_counts if avg_commits * 0.5 <= c <= avg_commits * 1.5),
            'low': sum(1 for c in commit_counts if c < avg_commits * 0.5)
        }

    def _analyze_collaboration(self, commits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze collaboration patterns between contributors."""
        # Group commits by date (day)
        daily_commits = defaultdict(list)
        for commit in commits:
            date = datetime.fromisoformat(commit['date']).date()
            daily_commits[date].append(commit)
        
        # Analyze collaboration
        collaboration_days = 0
        for day_commits in daily_commits.values():
            if len(set(c['author'] for c in day_commits)) > 1:
                collaboration_days += 1
        
        return {
            'collaboration_days': collaboration_days,
            'total_days': len(daily_commits),
            'collaboration_ratio': round(collaboration_days / len(daily_commits), 2) if daily_commits else 0
        }

    def _create_empty_analysis(self) -> Dict[str, Any]:
        """Create an empty contributor analysis result."""
        return {
            'team_metrics': {
                'total_contributors': 0,
                'active_contributors': 0,
                'activity_ratio': 0,
                'total_commits': 0,
                'total_insertions': 0,
                'total_deletions': 0,
                'commit_distribution': {'high': 0, 'medium': 0, 'low': 0}
            },
            'contributor_details': {},
            'collaboration_patterns': {
                'collaboration_days': 0,
                'total_days': 0,
                'collaboration_ratio': 0
            }
        } 