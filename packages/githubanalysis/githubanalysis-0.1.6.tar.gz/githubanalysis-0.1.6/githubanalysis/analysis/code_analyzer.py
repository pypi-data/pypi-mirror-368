from typing import Dict, List, Any, Optional
import re
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class CodeChange:
    file_path: str
    change_type: str  # 'addition', 'deletion', 'modification'
    impact_score: float
    complexity_change: float
    dependencies_affected: List[str]
    api_changes: List[str]
    test_coverage_change: float
    documentation_changes: bool
    security_impact: float
    performance_impact: float

class CodeAnalyzer:
    def __init__(self):
        self.patterns = {
            'api_change': r'(def|class)\s+(\w+)',
            'dependency': r'(import|from)\s+(\w+)',
            'security': r'(password|token|key|auth|security)',
            'performance': r'(optimize|performance|speed|efficiency)',
            'test': r'(test|assert|mock)',
            'documentation': r'(docstring|comment|documentation)'
        }

    def analyze_commit(self, commit: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single commit for deeper insights."""
        changes = []
        for file_change in commit.get('files', []):
            change = self._analyze_file_change(file_change)
            if change:
                changes.append(change)
        
        return {
            'changes': changes,
            'patterns': self._identify_patterns(commit),
            'dependencies': self._analyze_dependencies(commit),
            'api_changes': self._analyze_api_changes(commit)
        }

    def _analyze_file_change(self, file_change: Dict[str, Any]) -> Optional[CodeChange]:
        """Analyze changes in a single file."""
        if not file_change.get('patch'):
            return None

        # Convert patch to string if it's a dictionary
        patch = str(file_change['patch'])
        
        # Analyze the patch content
        api_changes = self._extract_api_changes(patch)
        dependencies = self._extract_dependencies(patch)
        
        return CodeChange(
            file_path=file_change['filename'],
            change_type=self._determine_change_type(file_change),
            impact_score=0.0,  # Removed scoring
            complexity_change=0.0,  # Removed scoring
            dependencies_affected=dependencies,
            api_changes=api_changes,
            test_coverage_change=0.0,  # Removed scoring
            documentation_changes=self._has_documentation_changes(patch),
            security_impact=0.0,  # Removed scoring
            performance_impact=0.0  # Removed scoring
        )

    def _extract_api_changes(self, patch: str) -> List[str]:
        """Extract API changes from the patch."""
        api_changes = []
        
        # Look for function and class definitions
        for line in patch.split('\n'):
            if line.startswith('+') or line.startswith('-'):
                match = re.search(self.patterns['api_change'], line)
                if match:
                    api_changes.append(match.group(2))
                    
        return api_changes

    def _extract_dependencies(self, patch: str) -> List[str]:
        """Extract dependency changes from the patch."""
        dependencies = []
        
        for line in patch.split('\n'):
            if line.startswith('+') or line.startswith('-'):
                match = re.search(self.patterns['dependency'], line)
                if match:
                    dependencies.append(match.group(2))
                    
        return dependencies

    def _has_documentation_changes(self, patch: str) -> bool:
        """Check if there are documentation changes."""
        for line in patch.split('\n'):
            if line.startswith('+') or line.startswith('-'):
                if re.search(self.patterns['documentation'], line.lower()):
                    return True
        return False

    def _determine_change_type(self, file_change: Dict[str, Any]) -> str:
        """Determine the type of change."""
        if file_change.get('status') == 'added':
            return 'addition'
        elif file_change.get('status') == 'removed':
            return 'deletion'
        else:
            return 'modification'

    def _identify_patterns(self, commit: Dict[str, Any]) -> Dict[str, Any]:
        """Identify patterns in the commit."""
        patterns = defaultdict(int)
        
        # Analyze commit message
        message = commit.get('message', '').lower()
        for pattern_name, pattern in self.patterns.items():
            if re.search(pattern, message):
                patterns[pattern_name] += 1
                
        return dict(patterns)

    def _analyze_dependencies(self, commit: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze dependency changes in the commit."""
        dependencies = defaultdict(int)
        
        for file_change in commit.get('files', []):
            if file_change.get('patch'):
                deps = self._extract_dependencies(file_change['patch'])
                for dep in deps:
                    dependencies[dep] += 1
                    
        return dict(dependencies)

    def _analyze_api_changes(self, commit: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze API changes in the commit."""
        api_changes = defaultdict(int)
        
        for file_change in commit.get('files', []):
            if file_change.get('patch'):
                apis = self._extract_api_changes(file_change['patch'])
                for api in apis:
                    api_changes[api] += 1
                    
        return dict(api_changes) 