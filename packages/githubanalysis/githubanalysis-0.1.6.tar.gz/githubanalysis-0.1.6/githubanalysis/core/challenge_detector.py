from typing import List, Dict, Any
from collections import defaultdict

class TechnicalChallengeDetector:
    def __init__(self):
        self.challenge_patterns = {
            'security': ['security', 'vulnerability', 'cve', 'exploit', 'fix'],
            'performance': ['performance', 'optimize', 'speed', 'latency', 'throughput'],
            'architecture': ['architect', 'design', 'structure', 'refactor'],
            'testing': ['test', 'spec', 'coverage', 'unit', 'integration'],
            'documentation': ['doc', 'readme', 'comment', 'guide'],
            'dependency': ['depend', 'package', 'library', 'version'],
            'compatibility': ['compat', 'version', 'upgrade', 'migration'],
            'scalability': ['scale', 'load', 'concurrent', 'parallel'],
            'reliability': ['reliab', 'stable', 'robust', 'error'],
            'maintenance': ['maintain', 'clean', 'refactor', 'technical debt']
        }

    def detect_challenges(self, commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect technical challenges from commit history."""
        if not commits:
            return []

        # Initialize challenge scores
        challenge_scores = defaultdict(float)
        challenge_commits = defaultdict(list)
        
        # Analyze each commit
        for commit in commits:
            message = commit['message'].lower()
            files = [f.lower() for f in commit['files_changed']]
            
            # Check each challenge pattern
            for challenge_type, patterns in self.challenge_patterns.items():
                # Check message
                if any(pattern in message for pattern in patterns):
                    challenge_scores[challenge_type] += 1.0
                    challenge_commits[challenge_type].append(commit)
                
                # Check files
                if any(pattern in ' '.join(files) for pattern in patterns):
                    challenge_scores[challenge_type] += 0.5
                    if commit not in challenge_commits[challenge_type]:
                        challenge_commits[challenge_type].append(commit)

        # Normalize scores
        total_commits = len(commits)
        normalized_scores = {
            challenge: score / total_commits 
            for challenge, score in challenge_scores.items()
        }

        # Get top challenges (all challenges with score > 0.1)
        top_challenges = [
            {
                'type': challenge,
                'score': round(score * 5, 2),  # Scale to 0-5
                'commits': challenge_commits[challenge]
            }
            for challenge, score in normalized_scores.items()
            if score > 0.1  # Threshold for considering a challenge
        ]

        # Sort by score
        top_challenges.sort(key=lambda x: x['score'], reverse=True)
        
        return top_challenges 