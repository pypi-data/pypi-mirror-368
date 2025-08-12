import os
import logging
from pathlib import Path
import json
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class Config:
    """Secure configuration management with environment variable support"""
    
    def __init__(self):
        self.config_file = self._find_config_file()
        self._config_data = {}
        self._load_config()
    
    def _find_config_file(self):
        """Find configuration file in order of priority"""
        possible_paths = [
            Path.cwd() / '.prcodesnip.json',
            Path.cwd() / 'prcodesnip.json', 
            Path.home() / '.prcodesnip.json',
            Path.home() / '.config' / 'prcodesnip.json'
        ]
        
        for path in possible_paths:
            if path.exists():
                logger.info(f"Using config file: {path}")
                return path
        
        return None
    
    def _load_config(self):
        """Load configuration from file if it exists"""
        if self.config_file and self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self._config_data = json.load(f)
                logger.debug(f"Loaded configuration from {self.config_file}")
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load config file: {e}")
                self._config_data = {}
    
    def get_github_token(self, token_arg=None):
        """Get GitHub token with priority: CLI arg > env var > config file"""
        if token_arg:
            return token_arg.strip()
        
        # Try environment variable
        token = os.getenv('GITHUB_TOKEN') or os.getenv('GH_TOKEN')
        if token:
            return token.strip()
        
        # Try config file
        token = self._config_data.get('github', {}).get('token')
        if token:
            if token.startswith('env:'):
                env_var = token[4:]  # Remove 'env:' prefix
                return os.getenv(env_var, '').strip()
            return token.strip()
        
        return None
    
    def get_openai_key(self, key_arg=None):
        """Get OpenAI API key with priority: CLI arg > env var > config file"""
        if key_arg:
            return key_arg.strip()
        
        # Try environment variable
        key = os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_KEY')
        if key:
            return key.strip()
        
        # Try config file
        key = self._config_data.get('openai', {}).get('api_key')
        if key:
            if key.startswith('env:'):
                env_var = key[4:]  # Remove 'env:' prefix
                return os.getenv(env_var, '').strip()
            return key.strip()
        
        return None
    
    def get_default_repo(self, repo_arg=None):
        """Get default repository"""
        if repo_arg:
            return repo_arg.strip()
        
        repo = os.getenv('CODESNIP_DEFAULT_REPO')
        if repo:
            return repo.strip()
        
        repo = self._config_data.get('github', {}).get('default_repo')
        if repo:
            return repo.strip()
        
        return None
    
    def get_user_preference(self, key: str, default=None):
        """Get user preference from configuration"""
        preferences = self._config_data.get('user_preferences', {})
        return preferences.get(key, default)
    
    def set_user_preference(self, key: str, value):
        """Set user preference in configuration"""
        if 'user_preferences' not in self._config_data:
            self._config_data['user_preferences'] = {}
        
        self._config_data['user_preferences'][key] = value
        self._save_config()
    
    def get_language_config(self, language: str) -> Dict[str, Any]:
        """Get language-specific configuration"""
        lang_configs = self._config_data.get('languages', {})
        return lang_configs.get(language, {})
    
    def set_language_config(self, language: str, config: Dict[str, Any]):
        """Set language-specific configuration"""
        if 'languages' not in self._config_data:
            self._config_data['languages'] = {}
        
        self._config_data['languages'][language] = config
        self._save_config()
    
    def get_enterprise_config(self) -> Optional[Dict[str, Any]]:
        """Get enterprise configuration"""
        return self._config_data.get('enterprise')
    
    def set_enterprise_config(self, config: Dict[str, Any]):
        """Set enterprise configuration"""
        self._config_data['enterprise'] = config
        self._save_config()
    
    def _save_config(self):
        """Save configuration to file"""
        if not self.config_file:
            # Create config file in user's home directory
            self.config_file = Path.home() / '.prcodesnip.json'
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config_data, f, indent=2)
            logger.debug(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def create_sample_config(self):
        """Create a sample configuration file"""
        sample_config = {
            "github": {
                "token": "env:GITHUB_TOKEN",
                "default_repo": "owner/repo"
            },
            "openai": {
                "api_key": "env:OPENAI_API_KEY",
                "model": "gpt-4o-mini"
            },
            "quality": {
                "tools": ["pytest", "pylint", "bandit", "coverage"],
                "timeout": 300
            },
            "output": {
                "default_format": "markdown",
                "default_file": "release-notes.md"
            }
        }
        
        config_path = Path.cwd() / '.prcodesnip.json'
        try:
            with open(config_path, 'w') as f:
                json.dump(sample_config, f, indent=2)
            logger.info(f"Created sample config file: {config_path}")
            return config_path
        except IOError as e:
            logger.error(f"Failed to create config file: {e}")
            return None

def get_config():
    """Get global configuration instance"""
    return Config()