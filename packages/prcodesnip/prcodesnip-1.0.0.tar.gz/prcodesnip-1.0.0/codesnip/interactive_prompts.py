import click
import requests
import logging
from typing import Optional, List, Dict, Any, Tuple
import re

logger = logging.getLogger(__name__)

class InteractivePrompter:
    """Interactive prompts for repository and PR selection"""
    
    def __init__(self, github_token: str):
        self.github_token = github_token
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "CodeSnip-CLI"
        }
        self.base_url = "https://api.github.com"
    
    def get_repository_interactive(self, default_repo: Optional[str] = None) -> str:
        """Interactively get repository from user"""
        click.echo("🏗️ Repository Selection")
        click.echo("-" * 22)
        
        if default_repo:
            if click.confirm(f"Use default repository '{default_repo}'?", default=True):
                return default_repo
        
        # Show options for getting repository
        click.echo("\nHow would you like to specify the repository?")
        click.echo("1. Enter repository manually (owner/repo)")
        click.echo("2. Browse your repositories")
        click.echo("3. Browse recent repositories")
        
        choice = click.prompt("Choose option", type=click.Choice(['1', '2', '3']), default='1')
        
        if choice == '1':
            return self._manual_repo_entry()
        elif choice == '2':
            return self._browse_user_repositories()
        elif choice == '3':
            return self._browse_recent_repositories()
    
    def get_pr_number_interactive(self, repository: str, provided_pr: Optional[int] = None) -> int:
        """Interactively get PR number from user"""
        if provided_pr:
            return provided_pr
        
        click.echo(f"\n📋 Pull Request Selection for {repository}")
        click.echo("-" * 50)
        
        click.echo("How would you like to select the PR?")
        click.echo("1. Enter PR number manually")
        click.echo("2. Browse open PRs")
        click.echo("3. Browse recent PRs (open + closed)")
        
        choice = click.prompt("Choose option", type=click.Choice(['1', '2', '3']), default='2')
        
        if choice == '1':
            return self._manual_pr_entry()
        elif choice == '2':
            return self._browse_open_prs(repository)
        elif choice == '3':
            return self._browse_recent_prs(repository)
    
    def _manual_repo_entry(self) -> str:
        """Manual repository entry with validation"""
        while True:
            repo = click.prompt("Enter repository (owner/repo)")
            
            if self._validate_repo_format(repo):
                # Test if repository is accessible
                if self._test_repository_access(repo):
                    return repo
                else:
                    click.echo("❌ Repository not found or not accessible.")
                    if not click.confirm("Try again?"):
                        click.get_current_context().exit(1)
            else:
                click.echo("❌ Invalid format. Please use 'owner/repo' format (e.g., 'microsoft/vscode')")
    
    def _browse_user_repositories(self) -> str:
        """Browse user's repositories"""
        click.echo("\n🔍 Fetching your repositories...")
        
        try:
            # Get user's repositories
            repos = self._fetch_user_repositories()
            
            if not repos:
                click.echo("❌ No repositories found or accessible.")
                return self._manual_repo_entry()
            
            return self._select_from_repo_list(repos, "Your Repositories")
            
        except Exception as e:
            logger.error(f"Failed to fetch repositories: {e}")
            click.echo("❌ Failed to fetch repositories. Using manual entry.")
            return self._manual_repo_entry()
    
    def _browse_recent_repositories(self) -> str:
        """Browse recently active repositories"""
        click.echo("\n🔍 Fetching recent repositories...")
        
        try:
            # Get repositories with recent activity
            repos = self._fetch_recent_repositories()
            
            if not repos:
                click.echo("❌ No recent repositories found.")
                return self._manual_repo_entry()
            
            return self._select_from_repo_list(repos, "Recent Repositories")
            
        except Exception as e:
            logger.error(f"Failed to fetch recent repositories: {e}")
            click.echo("❌ Failed to fetch repositories. Using manual entry.")
            return self._manual_repo_entry()
    
    def _manual_pr_entry(self) -> int:
        """Manual PR number entry with validation"""
        while True:
            try:
                pr_number = click.prompt("Enter PR number", type=int)
                if pr_number > 0:
                    return pr_number
                else:
                    click.echo("❌ PR number must be positive.")
            except click.Abort:
                click.get_current_context().exit(1)
    
    def _browse_open_prs(self, repository: str) -> int:
        """Browse open PRs for the repository"""
        click.echo(f"\n🔍 Fetching open PRs for {repository}...")
        
        try:
            prs = self._fetch_prs(repository, state='open')
            
            if not prs:
                click.echo("❌ No open PRs found.")
                return self._manual_pr_entry()
            
            return self._select_from_pr_list(prs, f"Open PRs in {repository}")
            
        except Exception as e:
            logger.error(f"Failed to fetch PRs: {e}")
            click.echo("❌ Failed to fetch PRs. Using manual entry.")
            return self._manual_pr_entry()
    
    def _browse_recent_prs(self, repository: str) -> int:
        """Browse recent PRs (open + closed) for the repository"""
        click.echo(f"\n🔍 Fetching recent PRs for {repository}...")
        
        try:
            prs = self._fetch_prs(repository, state='all', limit=20)
            
            if not prs:
                click.echo("❌ No PRs found.")
                return self._manual_pr_entry()
            
            return self._select_from_pr_list(prs, f"Recent PRs in {repository}")
            
        except Exception as e:
            logger.error(f"Failed to fetch PRs: {e}")
            click.echo("❌ Failed to fetch PRs. Using manual entry.")
            return self._manual_pr_entry()
    
    def _fetch_user_repositories(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch user's repositories"""
        url = f"{self.base_url}/user/repos"
        params = {
            'sort': 'updated',
            'per_page': limit,
            'type': 'all'
        }
        
        response = requests.get(url, headers=self.headers, params=params, timeout=10)
        response.raise_for_status()
        
        repos = response.json()
        return [
            {
                'full_name': repo['full_name'],
                'description': repo['description'] or 'No description',
                'updated_at': repo['updated_at'],
                'private': repo['private'],
                'language': repo['language']
            }
            for repo in repos
        ]
    
    def _fetch_recent_repositories(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch recently active repositories from user's activity"""
        # This could be enhanced to fetch from user's activity feed
        # For now, use user repos sorted by recent activity
        return self._fetch_user_repositories(limit)
    
    def _fetch_prs(self, repository: str, state: str = 'open', limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch PRs for a repository"""
        url = f"{self.base_url}/repos/{repository}/pulls"
        params = {
            'state': state,
            'sort': 'updated',
            'per_page': limit
        }
        
        response = requests.get(url, headers=self.headers, params=params, timeout=10)
        response.raise_for_status()
        
        prs = response.json()
        return [
            {
                'number': pr['number'],
                'title': pr['title'],
                'state': pr['state'],
                'author': pr['user']['login'],
                'created_at': pr['created_at'],
                'updated_at': pr['updated_at'],
                'url': pr['html_url']
            }
            for pr in prs
        ]
    
    def _select_from_repo_list(self, repos: List[Dict[str, Any]], title: str) -> str:
        """Display repository list for selection"""
        click.echo(f"\n📋 {title}")
        click.echo("-" * len(title))
        
        for i, repo in enumerate(repos[:15], 1):  # Limit to 15 for readability
            privacy = "🔒" if repo['private'] else "🌐"
            language = f"[{repo['language']}]" if repo['language'] else ""
            description = repo['description'][:50] + "..." if len(repo['description']) > 50 else repo['description']
            
            click.echo(f"{i:2d}. {privacy} {repo['full_name']} {language}")
            click.echo(f"    {description}")
            click.echo()
        
        if len(repos) > 15:
            click.echo(f"... and {len(repos) - 15} more")
        
        click.echo("0. Enter repository manually")
        
        while True:
            try:
                choice = click.prompt(f"Select repository (1-{min(len(repos), 15)}, 0 for manual)", type=int)
                
                if choice == 0:
                    return self._manual_repo_entry()
                elif 1 <= choice <= min(len(repos), 15):
                    selected_repo = repos[choice - 1]['full_name']
                    click.echo(f"✅ Selected: {selected_repo}")
                    return selected_repo
                else:
                    click.echo(f"❌ Please enter a number between 0 and {min(len(repos), 15)}")
                    
            except (click.Abort, ValueError):
                click.echo("❌ Invalid input. Please enter a number.")
    
    def _select_from_pr_list(self, prs: List[Dict[str, Any]], title: str) -> int:
        """Display PR list for selection"""
        click.echo(f"\n📋 {title}")
        click.echo("-" * len(title))
        
        for i, pr in enumerate(prs[:10], 1):  # Limit to 10 for readability
            state_icon = "✅" if pr['state'] == 'open' else "🔒"
            title_truncated = pr['title'][:60] + "..." if len(pr['title']) > 60 else pr['title']
            
            click.echo(f"{i:2d}. {state_icon} #{pr['number']}: {title_truncated}")
            click.echo(f"    👤 {pr['author']} • {pr['updated_at'][:10]}")
            click.echo()
        
        if len(prs) > 10:
            click.echo(f"... and {len(prs) - 10} more")
        
        click.echo("0. Enter PR number manually")
        
        while True:
            try:
                choice = click.prompt(f"Select PR (1-{min(len(prs), 10)}, 0 for manual)", type=int)
                
                if choice == 0:
                    return self._manual_pr_entry()
                elif 1 <= choice <= min(len(prs), 10):
                    selected_pr = prs[choice - 1]['number']
                    click.echo(f"✅ Selected PR #{selected_pr}: {prs[choice - 1]['title']}")
                    return selected_pr
                else:
                    click.echo(f"❌ Please enter a number between 0 and {min(len(prs), 10)}")
                    
            except (click.Abort, ValueError):
                click.echo("❌ Invalid input. Please enter a number.")
    
    def _validate_repo_format(self, repo: str) -> bool:
        """Validate repository format"""
        repo_pattern = r'^[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+$'
        return bool(re.match(repo_pattern, repo)) and len(repo) <= 100
    
    def _test_repository_access(self, repo: str) -> bool:
        """Test if repository is accessible"""
        try:
            url = f"{self.base_url}/repos/{repo}"
            response = requests.get(url, headers=self.headers, timeout=10)
            return response.status_code == 200
        except Exception:
            return False

def get_repository_and_pr_interactive(
    github_token: str,
    provided_repo: Optional[str] = None,
    provided_pr: Optional[int] = None,
    default_repo: Optional[str] = None
) -> Tuple[str, int]:
    """
    Interactively get repository and PR number from user
    
    Args:
        github_token: GitHub API token
        provided_repo: Repository provided via CLI argument
        provided_pr: PR number provided via CLI argument  
        default_repo: Default repository from config
    
    Returns:
        Tuple of (repository, pr_number)
    """
    prompter = InteractivePrompter(github_token)
    
    # Get repository
    if provided_repo:
        repository = provided_repo
        click.echo(f"🏗️ Using repository: {repository}")
    else:
        repository = prompter.get_repository_interactive(default_repo)
    
    # Get PR number
    if provided_pr:
        pr_number = provided_pr
        click.echo(f"📋 Using PR #{pr_number}")
    else:
        pr_number = prompter.get_pr_number_interactive(repository, provided_pr)
    
    return repository, pr_number