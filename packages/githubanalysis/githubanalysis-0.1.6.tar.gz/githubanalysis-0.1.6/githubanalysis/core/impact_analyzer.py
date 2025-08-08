from typing import List, Dict, Any
from collections import defaultdict
import math
from datetime import datetime
import re

class ImpactAnalyzer:
    def __init__(self):
        self.impact_weights = {
            'code_quality': 0.25,      # Code quality metrics
            'commit_quality': 0.20,    # Commit quality metrics
            'team_activity': 0.20,     # Team activity metrics
            'technical_depth': 0.20,   # Technical depth metrics
            'project_health': 0.15     # Project health metrics
        }

    def analyze_impact(self, commits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the impact of commits on the repository."""
        if not commits:
            return self._create_empty_impact()

        # Calculate basic metrics
        total_insertions = sum(c['insertions'] for c in commits)
        total_deletions = sum(c['deletions'] for c in commits)
        total_files = len(set(f for c in commits for f in c['files_changed']))
        
        # Calculate commit frequency and distribution
        commit_dates = sorted(datetime.fromisoformat(c['date']) for c in commits)
        if len(commit_dates) > 1:
            time_span = (commit_dates[-1] - commit_dates[0]).total_seconds() / 3600  # hours
            commit_frequency = len(commits) / max(time_span, 1)
            
            # Calculate commit distribution
            commit_distribution = self._calculate_commit_distribution(commit_dates)
        else:
            commit_frequency = 1
            commit_distribution = 1.0

        # Calculate author diversity and activity
        authors = set(c['author'] for c in commits)
        author_commits = defaultdict(int)
        for commit in commits:
            author_commits[commit['author']] += 1
        
        author_diversity = len(authors) / len(commits)
        author_activity = self._calculate_author_activity(author_commits)

        # Calculate code quality metrics
        code_quality = self._calculate_code_quality(commits)
        
        # Calculate commit quality metrics
        commit_quality = self._calculate_commit_quality(commits)
        
        # Calculate technical depth
        technical_depth = self._calculate_technical_depth(commits)

        # Calculate project health
        project_health = self._calculate_project_health(commits, commit_frequency, author_diversity)

        # Calculate overall impact score
        scores = {
            'code_quality': code_quality,
            'commit_quality': commit_quality,
            'team_activity': author_activity,
            'technical_depth': technical_depth,
            'project_health': project_health
        }

        overall_score = sum(score * self.impact_weights[metric] 
                          for metric, score in scores.items())

        return {
            'quality_metrics': {
                'quality_score': round(overall_score * 5, 2),  # Scale to 0-5
                'code_quality': round(code_quality * 5, 2),
                'commit_quality': round(commit_quality * 5, 2),
                'technical_depth': round(technical_depth * 5, 2),
                'project_health': round(project_health * 5, 2)
            },
            'activity_metrics': {
                'total_commits': len(commits),
                'total_insertions': total_insertions,
                'total_deletions': total_deletions,
                'total_files_changed': total_files,
                'commit_frequency': round(commit_frequency, 2),
                'unique_authors': len(authors),
                'commit_distribution': round(commit_distribution, 2),
                'author_activity': round(author_activity * 5, 2)
            },
            'impact_breakdown': {
                metric: round(score * 5, 2)  # Scale to 0-5
                for metric, score in scores.items()
            }
        }

    def _calculate_commit_distribution(self, commit_dates: List[datetime]) -> float:
        """Calculate how evenly distributed the commits are over time."""
        if len(commit_dates) < 2:
            return 1.0
            
        # Group commits by week
        weeks = defaultdict(int)
        for date in commit_dates:
            week = date.isocalendar()[1]  # Get week number
            weeks[week] += 1
            
        # Calculate standard deviation of commits per week
        values = list(weeks.values())
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = math.sqrt(variance)
        
        # Normalize to 0-1 scale (lower std_dev = better distribution)
        max_std_dev = len(commit_dates)  # Theoretical maximum
        return 1.0 - min(1.0, std_dev / max_std_dev)

    def _calculate_author_activity(self, author_commits: Dict[str, int]) -> float:
        """Calculate how evenly distributed the commits are among authors."""
        if not author_commits:
            return 0.0
            
        total_commits = sum(author_commits.values())
        values = list(author_commits.values())
        
        # Calculate Gini coefficient (measure of inequality)
        values.sort()
        n = len(values)
        index = range(1, n + 1)
        return 1 - (2 * sum(i * y for i, y in zip(index, values)) / (n * sum(values)))

    def _calculate_code_quality(self, commits: List[Dict[str, Any]]) -> float:
        """Calculate code quality score based on various metrics."""
        if not commits:
            return 0.0
            
        # Calculate average commit size
        avg_commit_size = sum(c['insertions'] + c['deletions'] for c in commits) / len(commits)
        
        # Calculate documentation ratio
        doc_changes = sum(1 for c in commits if any('doc' in f.lower() or 'readme' in f.lower() 
                                                  for f in c['files_changed']))
        doc_ratio = doc_changes / len(commits)
        
        # Calculate test ratio
        test_changes = sum(1 for c in commits if any('test' in f.lower() or 'spec' in f.lower() 
                                                   for f in c['files_changed']))
        test_ratio = test_changes / len(commits)
        
        # Calculate security-related changes
        security_changes = sum(1 for c in commits if any(word in c['message'].lower() 
                                                       for word in ['security', 'vulnerability', 'cve', 'exploit', 'fix']))
        security_ratio = security_changes / len(commits)
        
        # Calculate code review indicators
        review_indicators = sum(1 for c in commits if any(word in c['message'].lower() 
                                                        for word in ['review', 'feedback', 'suggest', 'improve']))
        review_ratio = review_indicators / len(commits)
        
        # Normalize metrics
        size_score = 1.0 - min(1.0, avg_commit_size / 1000)  # Smaller commits are better
        doc_score = min(1.0, doc_ratio * 2)  # More documentation is better
        test_score = min(1.0, test_ratio * 2)  # More tests are better
        security_score = min(1.0, security_ratio * 3)  # Security fixes are important
        review_score = min(1.0, review_ratio * 2)  # Code reviews are good
        
        return (size_score * 0.25 + doc_score * 0.2 + test_score * 0.2 + 
                security_score * 0.2 + review_score * 0.15)

    def _calculate_commit_quality(self, commits: List[Dict[str, Any]]) -> float:
        """Calculate commit quality score based on commit messages and changes."""
        if not commits:
            return 0.0
            
        # Analyze commit messages
        message_scores = []
        for commit in commits:
            message = commit['message'].lower()
            score = 0.0
            
            # Check for common good practices
            if len(message) > 10:  # Non-empty message
                score += 0.15
            if any(word in message for word in ['fix', 'bug', 'issue']):  # Bug fixes
                score += 0.15
            if any(word in message for word in ['feat', 'feature', 'add']):  # Features
                score += 0.15
            if any(word in message for word in ['refactor', 'improve', 'optimize']):  # Improvements
                score += 0.15
            if any(word in message for word in ['test', 'spec']):  # Tests
                score += 0.15
            if any(word in message for word in ['security', 'vulnerability', 'cve']):  # Security
                score += 0.15
            if any(word in message for word in ['doc', 'readme', 'comment']):  # Documentation
                score += 0.1
                
            message_scores.append(min(1.0, score))
            
        return sum(message_scores) / len(message_scores)

    def _calculate_technical_depth(self, commits: List[Dict[str, Any]]) -> float:
        """Calculate technical depth score based on code complexity and patterns."""
        if not commits:
            return 0.0
            
        # Calculate file type diversity
        file_types = set()
        for commit in commits:
            for file in commit['files_changed']:
                ext = file.split('.')[-1].lower() if '.' in file else ''
                if ext:
                    file_types.add(ext)
                    
        type_diversity = min(1.0, len(file_types) / 10)  # More file types = more complex
        
        # Calculate change complexity
        complex_changes = sum(1 for c in commits 
                            if c['insertions'] + c['deletions'] > 500)  # Large changes
        change_complexity = min(1.0, complex_changes / len(commits))
        
        # Calculate architectural changes
        arch_changes = sum(1 for c in commits if any(word in c['message'].lower() 
                                                   for word in ['architect', 'design', 'structure', 'refactor']))
        arch_score = min(1.0, arch_changes / len(commits))
        
        # Calculate security complexity
        security_complexity = sum(1 for c in commits if any(word in c['message'].lower() 
                                                          for word in ['security', 'vulnerability', 'cve', 'exploit']))
        security_score = min(1.0, security_complexity / len(commits))
        
        return (type_diversity * 0.3 + change_complexity * 0.3 + 
                arch_score * 0.2 + security_score * 0.2)

    def _calculate_project_health(self, commits: List[Dict[str, Any]], 
                                commit_frequency: float, author_diversity: float) -> float:
        """Calculate overall project health score."""
        if not commits:
            return 0.0
            
        # Calculate commit frequency score
        freq_score = min(1.0, commit_frequency / 10)  # Normalize to 0-1
        
        # Calculate author diversity score
        diversity_score = author_diversity
        
        # Calculate activity consistency
        dates = [datetime.fromisoformat(c['date']) for c in commits]
        if len(dates) > 1:
            time_span = (dates[-1] - dates[0]).total_seconds() / 3600
            consistency = len(commits) / max(time_span, 1)
            consistency_score = min(1.0, consistency / 5)  # Normalize to 0-1
        else:
            consistency_score = 0.0
            
        # Calculate security health
        security_commits = sum(1 for c in commits if any(word in c['message'].lower() 
                                                       for word in ['security', 'vulnerability', 'cve', 'exploit']))
        security_score = min(1.0, security_commits / len(commits))
        
        # Calculate maintenance health
        maintenance_commits = sum(1 for c in commits if any(word in c['message'].lower() 
                                                          for word in ['maintain', 'update', 'upgrade', 'depend']))
        maintenance_score = min(1.0, maintenance_commits / len(commits))
            
        return (freq_score * 0.25 + diversity_score * 0.2 + consistency_score * 0.2 + 
                security_score * 0.2 + maintenance_score * 0.15)

    def _normalize_score(self, value: float, max_value: float) -> float:
        """Normalize a value to a 0-1 scale using a logarithmic function."""
        return min(1.0, math.log1p(value) / math.log1p(max_value))

    def _create_empty_impact(self) -> Dict[str, Any]:
        """Create an empty impact analysis result."""
        return {
            'quality_metrics': {
                'quality_score': 0,
                'code_quality': 0,
                'commit_quality': 0,
                'technical_depth': 0,
                'project_health': 0
            },
            'activity_metrics': {
                'total_commits': 0,
                'total_insertions': 0,
                'total_deletions': 0,
                'total_files_changed': 0,
                'commit_frequency': 0,
                'unique_authors': 0,
                'commit_distribution': 0,
                'author_activity': 0
            },
            'impact_breakdown': {
                'code_quality': 0,
                'commit_quality': 0,
                'team_activity': 0,
                'technical_depth': 0,
                'project_health': 0
            }
        } 