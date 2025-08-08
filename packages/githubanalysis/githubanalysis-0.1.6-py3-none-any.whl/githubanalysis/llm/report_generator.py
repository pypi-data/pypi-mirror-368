from typing import Dict, Any
import json
from datetime import datetime
import os
import re
from githubanalysis.core.enhanced_git_analyzer import EnhancedGitAnalyzer

class ReportGenerator:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_report(self, analysis_results: Dict[str, Any], 
                       repository_name: str,
                       format: str = "json") -> str:
        """Generate a comprehensive report from analysis results and an Excel file with commit info."""
        # Generate report filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{repository_name}_{timestamp}_report"
        
        # Generate Excel file with commit info
        commits = analysis_results.get('commits', [])
        if commits:
            try:
                import pandas as pd
                import re
                
                # Extract commit references from the LLM report
                referenced_commits = {}
                if 'llm_analysis' in analysis_results and analysis_results['llm_analysis'].get('technical_challenges'):
                    technical_challenges = analysis_results['llm_analysis']['technical_challenges']
                    
                    # Look for the "Commit Reference Reasons" section
                    if "## Commit Reference Reasons" in technical_challenges:
                        reasons_section = technical_challenges.split("## Commit Reference Reasons")[1]
                        # Extract commit hash and reason pairs
                        reason_lines = re.findall(r'- `([0-9a-f]{7,40})`: (.+?)(?=\n- `|\n\n|$)', reasons_section, re.DOTALL)
                        for commit_hash, reason in reason_lines:
                            referenced_commits[commit_hash] = reason.strip()
                
                excel_data = [
                    {
                        'Commit Hash': c['hash'],
                        'Author': c['author'],
                        'Date': c['date'],
                        'Insertions': c['insertions'],
                        'Deletions': c['deletions'],
                        'Files Changed': len(c['files_changed']),
                        'Message': c['message'],
                        'Reason': self._get_commit_reason(c['hash'], referenced_commits)
                    }
                    for c in commits
                ]
                df = pd.DataFrame(excel_data)
                excel_filename = f"{self.output_dir}/{base_filename}.xlsx"
                df.to_excel(excel_filename, index=False)
                print(f"Excel file generated: {excel_filename}")
            except ImportError as e:
                print(f"pandas import error: {e}. Excel file will not be generated.")
            except Exception as e:
                print(f"Excel generation error: {e}. Excel file will not be generated.")
        
        if format.lower() == "markdown":
            # Generate markdown report
            md_content = self._generate_markdown_report(analysis_results)
            filename = f"{self.output_dir}/{base_filename}.md"
            with open(filename, 'w') as f:
                f.write(md_content)
        else:
            # Generate JSON report
            filename = f"{self.output_dir}/{base_filename}.json"
            with open(filename, 'w') as f:
                json.dump(analysis_results, f, indent=2)
            
        return filename

    def _generate_markdown_report(self, report_data: dict) -> str:
        """Generate a markdown formatted report."""
        md = []
        
        # Header
        md.append(f"# Technical Challenges Analysis: {report_data['repository']}")
        md.append(f"\nGenerated at: {report_data['generated_at']}")
        
        # Analysis Period
        if report_data['analysis_period']['start'] or report_data['analysis_period']['end']:
            md.append("\n## Analysis Period")
            period = []
            if report_data['analysis_period']['start']:
                period.append(f"From: {report_data['analysis_period']['start']}")
            if report_data['analysis_period']['end']:
                period.append(f"To: {report_data['analysis_period']['end']}")
            md.append("\n".join(period))
        
        # Technical Challenges (Only)
        if 'llm_analysis' in report_data and report_data['llm_analysis'].get('technical_challenges'):
            md.append("\n## Technical Challenges")
            technical_challenges = report_data['llm_analysis']['technical_challenges']
            
            # Remove the "Commit Reference Reasons" section from the report
            if "## Commit Reference Reasons" in technical_challenges:
                technical_challenges = technical_challenges.split("## Commit Reference Reasons")[0].strip()
            
            # Post-process commit hashes to URLs
            repo_url = report_data.get('repo_url')
            if repo_url:
                analyzer = EnhancedGitAnalyzer(repo_url)
                def repl(match):
                    commit_hash = match.group(1)
                    url = analyzer.get_commit_url(commit_hash)
                    return f'[`{commit_hash}`]({url})'
                # Replace backtick-wrapped hashes of length 7-40
                technical_challenges = re.sub(r'`([0-9a-f]{7,40})`', repl, technical_challenges)
            md.append(technical_challenges)
        
        # Repository Statistics (Last)
        md.append("\n## Repository Statistics")
        md.append(f"- Total Commits: {report_data['total_commits']}")
        md.append(f"- Total Authors: {report_data['total_authors']}")
        md.append(f"- Total Files Changed: {report_data['total_files_changed']}")
        md.append(f"- Total Insertions: {report_data['total_insertions']}")
        md.append(f"- Total Deletions: {report_data['total_deletions']}")
        
        return "\n".join(md)

    def _get_commit_reason(self, full_hash: str, referenced_commits: dict) -> str:
        """Get the reason for a commit by matching short hash with full hash."""
        # Check if any short hash from the report matches the beginning of this full hash
        for short_hash, reason in referenced_commits.items():
            if full_hash.startswith(short_hash):
                return reason
        return ''

         
