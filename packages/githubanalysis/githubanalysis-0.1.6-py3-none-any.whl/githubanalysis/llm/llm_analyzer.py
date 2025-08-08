import openai
from typing import Dict, Any, Optional, List
import os
import json
from dotenv import load_dotenv
from ..analysis.code_analyzer import CodeAnalyzer

# Load environment variables from .env file
load_dotenv()

class LLMAnalyzer:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini", 
                 custom_prompts_path: Optional[str] = None):
        self.model = model
        # Try to get API key from different sources
        self.api_key = (
            api_key or  # Direct parameter
            os.getenv("OPENAI_API_KEY") or  # Environment variable
            os.getenv("OPENAI_KEY")  # Alternative environment variable
        )
        
        if not self.api_key:
            print("Warning: No OpenAI API key found. Will use mock analysis.")
            self.client = None
        else:
            try:
                self.client = openai.OpenAI(api_key=self.api_key)
                # Test the API key with a simple request
                self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=5
                )
            except Exception as e:
                print(f"Error initializing OpenAI client: {str(e)}")
                print("Will use mock analysis instead.")
                self.client = None
            
        # Load prompts
        self.prompts = self._load_prompts(custom_prompts_path)
        
        # Initialize code analyzer
        self.code_analyzer = CodeAnalyzer()

    def _load_prompts(self, custom_prompts_path: Optional[str] = None) -> Dict[str, Any]:
        """Load prompts from default or custom configuration."""
        default_prompts_path = os.path.join(os.path.dirname(__file__), 'prompts', 'default_prompts.json')
        
        try:
            if custom_prompts_path and os.path.exists(custom_prompts_path):
                with open(custom_prompts_path, 'r') as f:
                    return json.load(f)
            elif os.path.exists(default_prompts_path):
                with open(default_prompts_path, 'r') as f:
                    return json.load(f)
            else:
                print("Warning: No prompts configuration found. Using basic prompts.")
                return self._get_basic_prompts()
        except Exception as e:
            print(f"Error loading prompts: {str(e)}. Using basic prompts.")
            return self._get_basic_prompts()

    def _get_basic_prompts(self) -> Dict[str, Any]:
        """Return basic prompts if no configuration is available."""
        return {
            "system_prompt": "You are an expert repository analyst specializing in identifying and analyzing technical challenges in software development projects. Your task is to analyze the entire project history and provide a comprehensive, detailed analysis of the most significant technical challenges.",
            "analysis_prompts": {
                "technical_challenges": "Analyze the entire repository history to identify the most significant technical challenges.",
                "technical_context": "Provide a comprehensive technical context of the project.",
                "implementation_details": "For each technical challenge, provide detailed implementation specifics."
            }
        }

    def analyze_repository(self, commits: List[Dict[str, Any]], milestones: List[Dict[str, Any]] = None, 
                         challenges: List[Dict[str, Any]] = None, contributor_data: Dict[str, Any] = None,
                         impact_data: Dict[str, Any] = None) -> Dict[str, str]:
        """Analyze repository data using LLM."""
        if not self.client:
            print("Warning: OpenAI client not initialized. Using mock analysis.")
            return self._generate_mock_analysis(commits)
            
        try:
            print("\n=== Starting Repository Analysis ===")
            print(f"Number of commits: {len(commits)}")
            
            # Prepare the analysis prompt
            prompt = self._prepare_analysis_prompt(commits, milestones, challenges, 
                                                 contributor_data, impact_data)
            print("\n=== Prompt Prepared ===")
            
            # Get analysis from OpenAI
            print("\n=== Calling OpenAI API ===")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.prompts["system_prompt"]},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000,
                temperature=0.7
            )
            
            print("\n=== OpenAI Response Received ===")
            print("Response type:", type(response))
            print("Response dir:", dir(response))
            print("Response choices type:", type(response.choices))
            print("First choice type:", type(response.choices[0]))
            print("Message type:", type(response.choices[0].message))
            print("Content type:", type(response.choices[0].message.content))
            print("Content:", response.choices[0].message.content[:200] + "..." if len(response.choices[0].message.content) > 200 else response.choices[0].message.content)
            
            # Get the content and return it directly
            content = response.choices[0].message.content
            print("\n=== Processing Content ===")
            print("Content type after assignment:", type(content))
            
            # Return the content directly in the expected format
            result = {
                "technical_challenges": content
            }
            print("\n=== Final Result ===")
            print("Result type:", type(result))
            print("Result keys:", result.keys())
            
            return result
            
        except Exception as e:
            print("\n=== Error Details ===")
            print(f"Error in LLM analysis: {str(e)}")
            print(f"Error type: {type(e)}")
            print(f"Error details: {e.__dict__ if hasattr(e, '__dict__') else 'No details available'}")
            print(f"Error location: {e.__traceback__.tb_lineno if hasattr(e, '__traceback__') else 'Unknown'}")
            import traceback
            print("Full traceback:")
            traceback.print_exc()
            return self._generate_mock_analysis(commits)

    def _prepare_analysis_prompt(self, commits, milestones=None, challenges=None, 
                               contributor_data=None, impact_data=None) -> str:
        """Prepare the analysis prompt using configured prompts."""
        # Get commit statistics
        commit_stats = self._analyze_commits(commits)
        
        # Analyze commits using the code analyzer
        commit_analysis = self._analyze_commits_deep(commits)
        
        metrics = f"""Repository Analysis Request

Repository Statistics:
- Total Commits: {len(commits)}
- Analysis Period: {commit_stats['first_commit']} to {commit_stats['last_commit']}
- Significant Milestones: {len(milestones) if milestones else 0}
- Technical Challenges: {len(challenges) if challenges else 0}
- Contributors: {contributor_data.get('team_metrics', {}).get('total_contributors', 0) if contributor_data else 0}
- Impact Score: {impact_data.get('quality_metrics', {}).get('quality_score', 0) if impact_data else 0}/5.0

Commit Activity:
- Most Active Period: {commit_stats['most_active_period']}
- Key Contributors: {', '.join(commit_stats['top_contributors'][:3])}
- Major Changes: {commit_stats['major_changes']}
- Major Code Changes: {len(commit_stats['major_code_changes'])}

Major Code Changes (Top 10 Commits by Insertions):
{self._format_major_code_changes(commit_stats['major_code_changes'])}

Deep Code Analysis:
{commit_analysis}

Please provide a comprehensive analysis of the entire project history, focusing on the significant technical challenges. For each challenge, you must:

1. Write a detailed technical description of the challenge and its context
2. Explain the key technical difficulties and complexities
3. Describe ALL attempts to solve the problem in detail
4. Provide a comprehensive current status
5. Reference specific commits with their detailed analysis

Follow this exact format:

Technical Challenges:
{self.prompts['analysis_prompts']['technical_challenges']}

Important Requirements:
- You MUST identify and analyze the significant technical challenges
- Each challenge MUST be described in detail with proper paragraphs
- Each challenge MUST include multiple solution attempts with specific technical details
- Each challenge MUST have a clear current status with next steps
- Each challenge MUST reference specific commits with their detailed analysis
- Use technical language and be specific about the challenges
- Include specific code patterns, algorithms, or systems involved
- Explain the impact of each challenge on the project
- Write in a clear, professional style with proper paragraphs
- Pay special attention to the top commits by insertions as they often indicate significant technical challenges or solutions
"""
        return metrics

    def _analyze_commits(self, commits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze commit history to provide additional context."""
        if not commits:
            return {
                'first_commit': 'N/A',
                'last_commit': 'N/A',
                'most_active_period': 'N/A',
                'top_contributors': [],
                'major_changes': 'N/A',
                'major_code_changes': []
            }
            
        # Get commit dates
        dates = [commit['date'] for commit in commits]
        first_commit = min(dates)
        last_commit = max(dates)
        
        # Get top contributors
        contributors = {}
        for commit in commits:
            author = commit['author']
            contributors[author] = contributors.get(author, 0) + 1
        
        top_contributors = sorted(contributors.items(), key=lambda x: x[1], reverse=True)
        top_contributors = [name for name, _ in top_contributors]
        
        # Identify major changes (commits with large number of changes)
        major_changes = [commit for commit in commits 
                        if commit['insertions'] + commit['deletions'] > 1000]
        major_changes = f"Found {len(major_changes)} major changes"
        
        # Identify major code changes based on insertions (more robust for technical challenges)
        major_code_changes = []
        
        # Get top 10 commits by insertions
        if commits:
            # Sort commits by insertions and take top 10
            top_commits_by_insertions = sorted(commits, key=lambda x: x['insertions'], reverse=True)[:10]
            
            for commit in top_commits_by_insertions:
                major_code_changes.append({
                    'hash': commit['hash'][:8],
                    'date': commit['date'],
                    'author': commit['author'],
                    'message': commit['message'][:100] + '...' if len(commit['message']) > 100 else commit['message'],
                    'insertions': commit['insertions'],
                    'deletions': commit['deletions'],
                    'files_changed': len(commit['files_changed'])
                })
        
        # Sort by insertions (highest first)
        major_code_changes.sort(key=lambda x: x['insertions'], reverse=True)
        
        return {
            'first_commit': first_commit,
            'last_commit': last_commit,
            'most_active_period': f"{first_commit} to {last_commit}",
            'top_contributors': top_contributors,
            'major_changes': major_changes,
            'major_code_changes': major_code_changes
        }

    def _format_major_code_changes(self, major_code_changes: List[Dict[str, Any]]) -> str:
        """Formats major code changes for prompt."""
        if not major_code_changes:
            return "No major code changes found."

        formatted_changes = []
        for change in major_code_changes:
            formatted_changes.append(
                f"Commit: {change['hash'][:8]} ({change['date']})"
                f" - Author: {change['author']}"
                f" - Message: {change['message']}"
                f" - Insertions: {change['insertions']}"
                f" - Deletions: {change['deletions']}"
                f" - Files Changed: {change['files_changed']}"
            )
        return "\n".join(formatted_changes)

    def _analyze_commits_deep(self, commits: List[Dict[str, Any]]) -> str:
        """Perform deep analysis of commits using the code analyzer."""
        if not commits:
            return "No commits found."
            
        # Analyze each commit
        commit_analyses = []
        for commit in commits:
            analysis = self.code_analyzer.analyze_commit(commit)
            
            # Format the analysis
            commit_info = [
                f"Commit: {commit['hash'][:8]} ({commit['date']})",
                f"Message: {commit['message']}",
                f"API Changes: {', '.join(str(k) for k in analysis['api_changes'].keys()) if analysis['api_changes'] else 'None'}",
                f"Dependencies: {', '.join(str(k) for k in analysis['dependencies'].keys()) if analysis['dependencies'] else 'None'}",
                f"Patterns: {', '.join(f'{k}: {v}' for k, v in analysis['patterns'].items()) if analysis['patterns'] else 'None'}"
            ]
            
            # Add detailed file changes
            if analysis['changes']:
                commit_info.append("\nFile Changes:")
                for change in analysis['changes']:
                    commit_info.extend([
                        f"  - {change.file_path}",
                        f"    Type: {change.change_type}",
                        f"    Documentation: {'Yes' if change.documentation_changes else 'No'}"
                    ])
            
            commit_analyses.append("\n".join(commit_info))
        
        return "\n\n".join(commit_analyses)

    def _generate_mock_analysis(self, commits: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate mock analysis when no API key is available."""
        return {
            "technical_challenges": "This is a mock analysis generated without an OpenAI API key. Please provide an API key for real analysis.",
            "technical_context": f"Found {len(commits)} commits in the repository.",
            "implementation_details": "Mock implementation details analysis."
        } 