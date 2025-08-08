import re
from typing import List, Dict, Any
from collections import defaultdict

class TechnicalChallengeDetector:
    def __init__(self):
        # Patterns for detecting technical challenges
        self.patterns = {
            'bug_fix': re.compile(r'fix|bug|issue|error|exception|crash', re.IGNORECASE),
            'performance': re.compile(r'performance|optimize|slow|bottleneck|memory leak', re.IGNORECASE),
            'security': re.compile(r'security|vulnerability|exploit|attack|injection', re.IGNORECASE),
            'refactoring': re.compile(r'refactor|restructure|cleanup|technical debt', re.IGNORECASE),
            'compatibility': re.compile(r'compatibility|version|upgrade|migration', re.IGNORECASE),
            'architecture': re.compile(r'architecture|design|pattern|structure', re.IGNORECASE)
        }

    def detect_challenges(self, commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect technical challenges in commit history."""
        challenges = []
        
        for commit in commits:
            message = commit['message'].lower()
            files_changed = [f.lower() for f in commit['files_changed']]
            
            # Check message and files for challenge patterns
            detected_challenges = self._analyze_commit(message, files_changed)
            
            if detected_challenges:
                challenges.append({
                    'hash': commit['hash'],
                    'date': commit['date'],
                    'author': commit['author'],
                    'message': commit['message'],
                    'challenges': detected_challenges,
                    'files_changed': commit['files_changed']
                })
        
        return challenges

    def _analyze_commit(self, message: str, files: List[str]) -> List[str]:
        """Analyze a commit message and changed files for technical challenges."""
        detected = set()
        
        # Check message for challenge patterns
        for challenge_type, pattern in self.patterns.items():
            if pattern.search(message):
                detected.add(challenge_type)
        
        # Check files for challenge patterns
        for file in files:
            for challenge_type, pattern in self.patterns.items():
                if pattern.search(file):
                    detected.add(challenge_type)
        
        return list(detected) 