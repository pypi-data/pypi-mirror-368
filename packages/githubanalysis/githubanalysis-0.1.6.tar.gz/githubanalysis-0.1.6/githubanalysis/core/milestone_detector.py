import re
from typing import List, Dict, Any
from datetime import datetime

class MilestoneDetector:
    def __init__(self):
        # Patterns for detecting milestones
        self.patterns = {
            'release': re.compile(r'release\s+v?(\d+\.\d+\.\d+)', re.IGNORECASE),
            'major_update': re.compile(r'major\s+update|version\s+(\d+\.\d+)', re.IGNORECASE),
            'initial_release': re.compile(r'initial\s+release|first\s+version', re.IGNORECASE),
            'feature_complete': re.compile(r'feature\s+complete|all\s+features\s+implemented', re.IGNORECASE),
            'beta': re.compile(r'beta\s+release|beta\s+v?(\d+\.\d+)', re.IGNORECASE),
            'stable': re.compile(r'stable\s+release|stable\s+v?(\d+\.\d+)', re.IGNORECASE)
        }

    def detect_milestones(self, commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect significant milestones in commit history."""
        milestones = []
        
        for commit in commits:
            message = commit['message'].lower()
            date = datetime.fromisoformat(commit['date'])
            
            # Check each pattern
            for milestone_type, pattern in self.patterns.items():
                if pattern.search(message):
                    version = pattern.search(message).group(1) if pattern.groups > 0 else None
                    milestones.append({
                        'hash': commit['hash'],
                        'date': commit['date'],
                        'message': commit['message'],
                        'type': milestone_type,
                        'version': version
                    })
                    break  # Only count one milestone type per commit
        
        return milestones 