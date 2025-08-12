import click
import os
import json
import getpass
import requests
from pathlib import Path
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class SetupWizard:
    """Interactive setup wizard for CodeSnip CLI"""
    
    def __init__(self):
        self.config_path = Path.cwd() / '.prcodesnip.json'
        self.config_data = {}
    
    def run_interactive_setup(self) -> bool:
        """Run the complete interactive setup process"""
        click.echo("🚀 Welcome to PRCodeSnip Setup Wizard!")
        click.echo("=" * 50)
        
        try:
            # Step 1: Basic information
            if not self._get_basic_info():
                return False
            
            # Step 2: GitHub credentials
            if not self._setup_github_credentials():
                return False
            
            # Step 3: OpenAI credentials (optional)
            self._setup_openai_credentials()
            
            # Step 4: Default settings
            self._setup_default_settings()
            
            # Step 5: Save configuration
            if not self._save_configuration():
                return False
            
            # Step 6: Test configuration
            self._test_configuration()
            
            click.echo("\n✅ Setup completed successfully!")
            click.echo(f"Configuration saved to: {self.config_path}")
            return True
            
        except KeyboardInterrupt:
            click.echo("\n\n❌ Setup cancelled by user.")
            return False
        except Exception as e:
            click.echo(f"\n❌ Setup failed: {e}")
            return False
    
    def _get_basic_info(self) -> bool:
        """Get basic user information"""
        click.echo("\n📋 Step 1: Basic Information")
        click.echo("-" * 30)
        
        # Get default repository
        repo_hint = "Leave empty to specify per command"
        default_repo = click.prompt(
            f"Default GitHub repository (owner/repo) [{repo_hint}]", 
            default="", 
            show_default=False
        )
        
        if default_repo and not self._validate_repo_format(default_repo):
            click.echo("❌ Invalid repository format. Please use 'owner/repo' format.")
            return False
        
        self.config_data['github'] = {'default_repo': default_repo or None}
        return True
    
    def _setup_github_credentials(self) -> bool:
        """Setup GitHub credentials with multiple options"""
        click.echo("\n🔑 Step 2: GitHub Authentication")
        click.echo("-" * 35)
        
        click.echo("Choose how you want to provide your GitHub token:")
        click.echo("1. Enter token now (will be stored securely)")
        click.echo("2. Use environment variable (GITHUB_TOKEN)")
        click.echo("3. Get help creating a GitHub token")
        
        choice = click.prompt("Enter your choice", type=click.Choice(['1', '2', '3']))
        
        if choice == '1':
            return self._enter_github_token()
        elif choice == '2':
            return self._use_github_env_var()
        elif choice == '3':
            self._show_github_help()
            return self._setup_github_credentials()  # Ask again after help
    
    def _enter_github_token(self) -> bool:
        """Allow user to enter GitHub token directly"""
        click.echo("\n🔐 Enter your GitHub Personal Access Token:")
        click.echo("(Your input will be hidden for security)")
        
        token = getpass.getpass("GitHub Token: ").strip()
        
        if not token:
            click.echo("❌ Token cannot be empty.")
            return False
        
        # Validate token
        if self._validate_github_token(token):
            self.config_data['github']['token'] = token
            click.echo("✅ GitHub token validated and saved.")
            return True
        else:
            click.echo("❌ Invalid GitHub token. Please check your token and try again.")
            
            if click.confirm("Would you like to try again?"):
                return self._enter_github_token()
            return False
    
    def _use_github_env_var(self) -> bool:
        """Use environment variable for GitHub token"""
        env_token = os.getenv('GITHUB_TOKEN')
        
        if env_token:
            if self._validate_github_token(env_token):
                self.config_data['github']['token'] = 'env:GITHUB_TOKEN'
                click.echo("✅ Using GITHUB_TOKEN environment variable.")
                return True
            else:
                click.echo("❌ GITHUB_TOKEN environment variable contains invalid token.")
                return False
        else:
            click.echo("❌ GITHUB_TOKEN environment variable not found.")
            click.echo("\nTo set it, run:")
            click.echo("export GITHUB_TOKEN='your_token_here'")
            
            if click.confirm("Set it now and continue?"):
                return self._use_github_env_var()
            return False
    
    def _show_github_help(self):
        """Show help for creating GitHub token"""
        click.echo("\n📖 How to Create a GitHub Personal Access Token:")
        click.echo("-" * 50)
        click.echo("1. Go to GitHub.com → Settings → Developer settings")
        click.echo("2. Click 'Personal access tokens' → 'Tokens (classic)'")
        click.echo("3. Click 'Generate new token (classic)'")
        click.echo("4. Give it a name like 'CodeSnip CLI'")
        click.echo("5. Select these scopes:")
        click.echo("   ✓ repo (Full control of private repositories)")
        click.echo("   ✓ read:org (Read org membership)")
        click.echo("6. Click 'Generate token'")
        click.echo("7. Copy the token (you won't see it again!)")
        click.echo("\n🔗 Direct link: https://github.com/settings/tokens/new")
        
        click.pause("Press any key to continue...")
    
    def _setup_openai_credentials(self):
        """Setup OpenAI credentials (optional)"""
        click.echo("\n🤖 Step 3: OpenAI Integration (Optional)")
        click.echo("-" * 40)
        
        if not click.confirm("Do you want to enable AI-powered release notes?"):
            self.config_data['openai'] = {'api_key': None}
            return
        
        click.echo("\nChoose how to provide your OpenAI API key:")
        click.echo("1. Enter API key now")
        click.echo("2. Use environment variable (OPENAI_API_KEY)")
        click.echo("3. Skip for now (can be added later)")
        click.echo("4. Get help creating an OpenAI API key")
        
        choice = click.prompt("Enter your choice", type=click.Choice(['1', '2', '3', '4']))
        
        if choice == '1':
            self._enter_openai_key()
        elif choice == '2':
            self._use_openai_env_var()
        elif choice == '3':
            self.config_data['openai'] = {'api_key': None}
        elif choice == '4':
            self._show_openai_help()
            self._setup_openai_credentials()
    
    def _enter_openai_key(self):
        """Allow user to enter OpenAI API key"""
        click.echo("\n🔐 Enter your OpenAI API Key:")
        api_key = getpass.getpass("OpenAI API Key: ").strip()
        
        if not api_key:
            self.config_data['openai'] = {'api_key': None}
            return
        
        if api_key.startswith('sk-'):
            self.config_data['openai'] = {'api_key': api_key, 'model': 'gpt-4o-mini'}
            click.echo("✅ OpenAI API key saved.")
        else:
            click.echo("⚠️ API key format looks unusual, but saved anyway.")
            self.config_data['openai'] = {'api_key': api_key, 'model': 'gpt-4o-mini'}
    
    def _use_openai_env_var(self):
        """Use environment variable for OpenAI API key"""
        env_key = os.getenv('OPENAI_API_KEY')
        
        if env_key:
            self.config_data['openai'] = {'api_key': 'env:OPENAI_API_KEY', 'model': 'gpt-4o-mini'}
            click.echo("✅ Using OPENAI_API_KEY environment variable.")
        else:
            click.echo("❌ OPENAI_API_KEY environment variable not found.")
            self.config_data['openai'] = {'api_key': None}
    
    def _show_openai_help(self):
        """Show help for creating OpenAI API key"""
        click.echo("\n📖 How to Get an OpenAI API Key:")
        click.echo("-" * 35)
        click.echo("1. Go to https://platform.openai.com")
        click.echo("2. Sign up or log in to your account")
        click.echo("3. Go to 'API keys' section")
        click.echo("4. Click 'Create new secret key'")
        click.echo("5. Give it a name like 'CodeSnip CLI'")
        click.echo("6. Copy the key (starts with sk-...)")
        click.echo("7. Add billing information (small usage costs)")
        click.echo("\n💰 Pricing: ~$0.01-0.05 per analysis (very affordable)")
        
        click.pause("Press any key to continue...")
    
    def _setup_default_settings(self):
        """Setup default settings"""
        click.echo("\n⚙️ Step 4: Default Settings")
        click.echo("-" * 25)
        
        # Quality tools
        tools = ['pytest', 'pylint', 'bandit', 'coverage']
        self.config_data['quality'] = {
            'tools': tools,
            'timeout': 300
        }
        
        # Output settings
        self.config_data['output'] = {
            'default_format': 'markdown',
            'default_file': 'release-notes.md'
        }
        
        click.echo("✅ Default settings configured.")
    
    def _save_configuration(self) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config_data, f, indent=2)
            click.echo(f"✅ Configuration saved to {self.config_path}")
            return True
        except Exception as e:
            click.echo(f"❌ Failed to save configuration: {e}")
            return False
    
    def _test_configuration(self):
        """Test the configuration"""
        click.echo("\n🧪 Step 5: Testing Configuration")
        click.echo("-" * 30)
        
        # Test GitHub token
        github_token = self._get_token_value(self.config_data.get('github', {}).get('token'))
        if github_token:
            if self._validate_github_token(github_token):
                click.echo("✅ GitHub token is working")
            else:
                click.echo("❌ GitHub token test failed")
        else:
            click.echo("⚠️ No GitHub token to test")
        
        # Test OpenAI key
        openai_key = self._get_token_value(self.config_data.get('openai', {}).get('api_key'))
        if openai_key:
            click.echo("✅ OpenAI key configured (not tested to avoid charges)")
        else:
            click.echo("ℹ️ OpenAI key not configured (optional)")
    
    def _validate_github_token(self, token: str) -> bool:
        """Validate GitHub token by making a test API call"""
        try:
            headers = {'Authorization': f'token {token}', 'User-Agent': 'CodeSnip-CLI'}
            response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"GitHub token validation failed: {e}")
            return False
    
    def _validate_repo_format(self, repo: str) -> bool:
        """Validate repository format"""
        import re
        return bool(re.match(r'^[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+$', repo))
    
    def _get_token_value(self, token_config: Optional[str]) -> Optional[str]:
        """Get actual token value from config (handle env: prefix)"""
        if not token_config:
            return None
        
        if token_config.startswith('env:'):
            env_var = token_config[4:]
            return os.getenv(env_var)
        
        return token_config

def run_setup_wizard() -> bool:
    """Public function to run the setup wizard"""
    wizard = SetupWizard()
    return wizard.run_interactive_setup()