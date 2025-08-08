from git import Repo, Git
import json
from datetime import datetime, timedelta
import os
import tempfile
import shutil
import openai
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from githubanalysis.core import (
    EnhancedGitAnalyzer,
    MilestoneDetector,
    CommitClusterer,
    TechnicalChallengeDetector,
    ImpactAnalyzer,
    ContributorAnalyzer
)
from githubanalysis.llm import LLMAnalyzer, ReportGenerator
import argparse
import sys
from pathlib import Path
import re
import time
from tqdm import tqdm
import signal
from contextlib import contextmanager
import requests
from requests.exceptions import Timeout, RequestException

# Load environment variables from .env file
load_dotenv()

# Constants
DEFAULT_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

class TimeoutError(Exception):
    pass

@contextmanager
def timeout(seconds):
    def signal_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")
    
    # Register the signal handler
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        # Disable the alarm
        signal.alarm(0)

def validate_date(date_str: str) -> bool:
    """Validate date format and ensure it's a valid date."""
    if not date_str:
        return True
    
    try:
        # Check format
        datetime.strptime(date_str, '%Y-%m-%d')
        
        # Additional validation for reasonable date range
        date = datetime.strptime(date_str, '%Y-%m-%d')
        if date.year < 1970 or date.year > datetime.now().year + 1:
            return False
            
        return True
    except ValueError:
        return False

def validate_repo_url(url: str) -> bool:
    """Validate repository URL format and accessibility."""
    if not url:
        return False
        
    # Check URL format
    if not url.startswith(('http://', 'https://', 'git@')):
        return False
        
    # For HTTPS URLs
    if url.startswith(('http://', 'https://')):
        # Basic URL pattern validation
        pattern = r'^https?://(?:[\w-]+\.)+[\w-]+(?:/[\w-]+)*(?:\.git)?$'
        if not re.match(pattern, url):
            return False
            
    # For SSH URLs
    elif url.startswith('git@'):
        pattern = r'^git@(?:[\w-]+\.)+[\w-]+:[\w-]+/[\w-]+(?:\.git)?$'
        if not re.match(pattern, url):
            return False
            
    return True

def ensure_output_dir(output_dir: str) -> None:
    """Ensure output directory exists and is writable."""
    try:
        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)
        
        # Test if directory is writable
        test_file = path / '.write_test'
        try:
            test_file.touch()
            test_file.unlink()
        except (IOError, OSError):
            print(f"Error: Output directory '{output_dir}' is not writable")
            sys.exit(1)
    except Exception as e:
        print(f"Error creating output directory: {str(e)}")
        sys.exit(1)

def validate_date_range(start_date: Optional[str], end_date: Optional[str]) -> bool:
    """Validate that start_date is before end_date if both are provided."""
    if not start_date or not end_date:
        return True
        
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        return start <= end
    except ValueError:
        return False

def retry_with_timeout(func, timeout_seconds: int, *args, **kwargs):
    """Retry a function with timeout handling."""
    for attempt in range(MAX_RETRIES):
        try:
            with timeout(timeout_seconds):
                return func(*args, **kwargs)
        except TimeoutError:
            if attempt < MAX_RETRIES - 1:
                print(f"Operation timed out. Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                raise TimeoutError(f"Operation failed after {MAX_RETRIES} attempts")
        except Exception as e:
            raise e

def main():
    parser = argparse.ArgumentParser(description='Analyze a Git repository and generate a report.')
    parser.add_argument('repo_url', help='URL of the Git repository')
    parser.add_argument('--start-date', help='Start date for analysis (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='End date for analysis (YYYY-MM-DD)')
    parser.add_argument('--output-dir', default='reports', help='Output directory for reports')
    parser.add_argument('--format', default='markdown', choices=['json', 'markdown'], help='Output format (json or markdown)')
    parser.add_argument('--openai-key', help='OpenAI API key')
    parser.add_argument('--custom-prompts', help='Path to custom prompts JSON file')
    parser.add_argument('--model', default='gpt-4o-mini', help='OpenAI model to use')
    parser.add_argument('--timeout', type=int, default=DEFAULT_TIMEOUT, help='Timeout for API calls in seconds')
    
    args = parser.parse_args()
    
    # Validate repository URL
    if not validate_repo_url(args.repo_url):
        print("Error: Invalid repository URL format. Must be a valid GitHub/GitLab URL or SSH format")
        print("Examples:")
        print("  - https://github.com/username/repo.git")
        print("  - git@github.com:username/repo.git")
        sys.exit(1)
    
    # Validate dates
    if args.start_date and not validate_date(args.start_date):
        print("Error: Invalid start date format or date out of range")
        print("Date must be in YYYY-MM-DD format and between 1970 and next year")
        sys.exit(1)
        
    if args.end_date and not validate_date(args.end_date):
        print("Error: Invalid end date format or date out of range")
        print("Date must be in YYYY-MM-DD format and between 1970 and next year")
        sys.exit(1)
        
    # Validate date range
    if not validate_date_range(args.start_date, args.end_date):
        print("Error: Start date must be before or equal to end date")
        sys.exit(1)
    
    # Ensure output directory exists and is writable
    ensure_output_dir(args.output_dir)
    
    # Get OpenAI API key
    api_key = args.openai_key or os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OpenAI API key not provided")
        print("Please provide your API key using one of these methods:")
        print("  1. Command line: --openai-key your-api-key")
        print("  2. Environment variable: export OPENAI_API_KEY=your-api-key")
        print("  3. .env file: Create a .env file with OPENAI_API_KEY=your-api-key")
        sys.exit(1)
    
    try:
        print("\nStarting repository analysis...")
        # Initialize components
        with EnhancedGitAnalyzer(args.repo_url, args.start_date, args.end_date) as analyzer:
            print("Fetching repository data...")
            
            # Extract commits with progress bar
            commits = []
            with tqdm(desc="Extracting commits", unit="commit") as pbar:
                for commit in analyzer.extract_all_commits():
                    commits.append(commit)
                    pbar.update(1)
            
            if not commits:
                print("Error: No commits found in the repository")
                sys.exit(1)
            print(f"\nFound {len(commits)} commits")
            
            # Initialize analyzers
            print("\nInitializing analyzers...")
            milestone_detector = MilestoneDetector()
            commit_clusterer = CommitClusterer()
            challenge_detector = TechnicalChallengeDetector()
            impact_analyzer = ImpactAnalyzer()
            contributor_analyzer = ContributorAnalyzer()
            
            print("\nRunning analysis...")
            # Run all analyses with progress tracking
            with tqdm(total=5, desc="Analysis progress") as pbar:
                milestones = retry_with_timeout(milestone_detector.detect_milestones, args.timeout, commits)
                pbar.update(1)
                
                clusters = retry_with_timeout(commit_clusterer.cluster_commits, args.timeout, commits)
                pbar.update(1)
                
                challenges = retry_with_timeout(challenge_detector.detect_challenges, args.timeout, commits)
                pbar.update(1)
                
                impact_data = retry_with_timeout(impact_analyzer.analyze_impact, args.timeout, commits)
                pbar.update(1)
                
                contributor_data = retry_with_timeout(contributor_analyzer.analyze_contributors, args.timeout, commits)
                pbar.update(1)
            
            # Create analysis report
            print("\nCompiling analysis results...")
            report = {
                "repository": analyzer.get_repository_name(),
                "repo_url": args.repo_url,
                "generated_at": datetime.now().isoformat(),
                "analysis_period": {
                    "start": args.start_date,
                    "end": args.end_date
                },
                "total_commits": len(commits),
                "total_authors": len(set(c['author'] for c in commits)),
                "total_files_changed": len(set(f for c in commits for f in c['files_changed'])),
                "total_insertions": sum(c['insertions'] for c in commits),
                "total_deletions": sum(c['deletions'] for c in commits),
                "milestones": milestones,
                "commit_clusters": clusters,
                "technical_challenges": challenges,
                "impact_analysis": impact_data,
                "contributor_analysis": contributor_data,
                "commits": commits
            }
            
            print("\nPerforming LLM analysis...")
            # Perform LLM analysis with timeout
            llm_analyzer = LLMAnalyzer(
                api_key=api_key,
                model=args.model,
                custom_prompts_path=args.custom_prompts
            )
            try:
                llm_analysis = retry_with_timeout(
                    llm_analyzer.analyze_repository,
                    args.timeout,
                    commits,
                    milestones=milestones,
                    challenges=challenges,
                    contributor_data=contributor_data,
                    impact_data=impact_data
                )
                report['llm_analysis'] = llm_analysis
            except Exception as e:
                print(f"\nWarning: LLM analysis failed: {str(e)}")
                print("Continuing without LLM analysis...")
                report['llm_analysis'] = None
            
            print("\nGenerating report...")
            # Generate report
            report_generator = ReportGenerator(output_dir=args.output_dir)
            report_file = report_generator.generate_report(
                report,
                report['repository'],
                format=args.format
            )
            
            print(f"\n✅ Report generated successfully: {report_file}")
            
    except TimeoutError as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 