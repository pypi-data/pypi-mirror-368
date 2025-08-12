"""
Dynamic package installation and management system for different languages
"""
import os
import json
import logging
import subprocess
import shlex
import platform
from typing import Dict, List, Optional, Set, Tuple, Any
from pathlib import Path
import yaml
import tempfile
import shutil

logger = logging.getLogger(__name__)

class LanguagePackageManager:
    """Manages packages and dependencies for different programming languages"""
    
    def __init__(self):
        self.system_os = platform.system().lower()
        self.architecture = platform.machine().lower()
        self.installed_packages = {}
        self.package_cache = {}
    
    def install_language_environment(self, languages: List[str], project_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Install complete environment for detected languages
        
        Args:
            languages: List of detected programming languages
            project_path: Optional path to project for context
            
        Returns:
            Installation results and environment information
        """
        logger.info(f"🚀 Setting up environment for languages: {', '.join(languages)}")
        
        results = {
            'success': True,
            'installed_runtimes': [],
            'installed_tools': [],
            'failed_installations': [],
            'environment_info': {},
            'next_steps': []
        }
        
        for language in languages:
            try:
                # Install runtime/compiler
                runtime_result = self._install_language_runtime(language)
                if runtime_result['success']:
                    results['installed_runtimes'].append(language)
                    results['environment_info'][language] = runtime_result['info']
                else:
                    results['failed_installations'].append({
                        'language': language,
                        'component': 'runtime',
                        'error': runtime_result.get('error', 'Unknown error')
                    })
                
                # Install package manager
                pm_result = self._install_package_manager(language)
                if pm_result['success']:
                    results['installed_tools'].extend(pm_result['tools'])
                
                # Install development tools
                tools_result = self._install_development_tools(language)
                results['installed_tools'].extend(tools_result.get('tools', []))
                
                # Generate language-specific workflow
                workflow = self._generate_workflow_config(language, project_path)
                self._save_workflow_config(language, workflow, project_path)
                
            except Exception as e:
                logger.error(f"Failed to setup {language}: {e}")
                results['failed_installations'].append({
                    'language': language,
                    'error': str(e)
                })
                results['success'] = False
        
        # Generate next steps
        results['next_steps'] = self._generate_setup_instructions(languages, results)
        
        return results
    
    def _install_language_runtime(self, language: str) -> Dict[str, Any]:
        """Install language runtime/compiler"""
        
        installers = {
            'python': self._install_python_runtime,
            'javascript': self._install_nodejs_runtime,
            'typescript': self._install_nodejs_runtime,  # TypeScript runs on Node.js
            'go': self._install_go_runtime,
            'java': self._install_java_runtime,
            'csharp': self._install_dotnet_runtime,
            'rust': self._install_rust_runtime,
            'cpp': self._install_cpp_runtime,
            'c': self._install_c_runtime,
            'php': self._install_php_runtime,
            'ruby': self._install_ruby_runtime,
            'swift': self._install_swift_runtime,
            'kotlin': self._install_kotlin_runtime,
            'scala': self._install_scala_runtime,
            'cpp': self._install_generic_runtime,  # C++ handled generically
            'c': self._install_generic_runtime,    # C handled generically
            # Add comprehensive language support - fallback to generic installer
            'haskell': self._install_generic_runtime,
            'ocaml': self._install_generic_runtime,
            'erlang': self._install_generic_runtime,
            'elixir': self._install_generic_runtime,
            'fsharp': self._install_dotnet_runtime,  # F# runs on .NET
            'clojure': self._install_java_runtime,   # Clojure runs on JVM
            'groovy': self._install_java_runtime,    # Groovy runs on JVM
            'vbnet': self._install_dotnet_runtime,   # VB.NET runs on .NET
            'powershell': self._install_powershell_runtime,
            'assembly': self._install_generic_runtime,
            'zig': self._install_generic_runtime,
            'html': self._install_web_runtime,
            'css': self._install_web_runtime,
            'sql': self._install_generic_runtime,
            'r': self._install_generic_runtime,
            'matlab': self._install_generic_runtime,
            'julia': self._install_generic_runtime,
            'dart': self._install_generic_runtime,
            'objectivec': self._install_generic_runtime,
            'perl': self._install_generic_runtime,
            'bash': self._install_generic_runtime,
            'fish': self._install_generic_runtime,
            'lua': self._install_generic_runtime,
            'crystal': self._install_generic_runtime,
            'nim': self._install_generic_runtime,
            'vlang': self._install_generic_runtime,
            'solidity': self._install_nodejs_runtime,  # Solidity tools run on Node.js
            'vyper': self._install_python_runtime,     # Vyper runs on Python
            'gdscript': self._install_generic_runtime,
            'actionscript': self._install_generic_runtime,
            'verilog': self._install_generic_runtime,
            'vhdl': self._install_generic_runtime,
            'systemverilog': self._install_generic_runtime,
            'yaml': self._install_web_runtime,
            'toml': self._install_web_runtime,
            'json': self._install_web_runtime,
            'xml': self._install_web_runtime,
            'markdown': self._install_web_runtime,
            'dockerfile': self._install_docker_runtime,
            'makefile': self._install_generic_runtime,
            'terraform': self._install_terraform_runtime
        }
        
        installer = installers.get(language)
        if installer:
            return installer()
        else:
            return {
                'success': False,
                'error': f'No installer available for {language}'
            }
    
    def _install_python_runtime(self) -> Dict[str, Any]:
        """Install Python runtime and tools"""
        if self._is_command_available('python3'):
            version = self._get_command_output('python3 --version')
            return {
                'success': True,
                'info': {
                    'runtime': 'python3',
                    'version': version,
                    'path': shutil.which('python3')
                }
            }
        
        # Install Python based on OS
        if self.system_os == 'darwin':
            success, output, error = self._safe_execute('brew install python3')
        elif self.system_os == 'linux':
            # Try different package managers
            if self._is_command_available('apt-get'):
                success, output, error = self._safe_execute('sudo apt-get update && sudo apt-get install -y python3 python3-pip')
            elif self._is_command_available('yum'):
                success, output, error = self._safe_execute('sudo yum install -y python3 python3-pip')
            elif self._is_command_available('pacman'):
                success, output, error = self._safe_execute('sudo pacman -S python python-pip')
            else:
                return {'success': False, 'error': 'No supported package manager found'}
        else:
            return {'success': False, 'error': 'Unsupported operating system'}
        
        if success == 0:
            version = self._get_command_output('python3 --version')
            return {
                'success': True,
                'info': {
                    'runtime': 'python3',
                    'version': version,
                    'path': shutil.which('python3')
                }
            }
        else:
            return {'success': False, 'error': error}
    
    def _install_nodejs_runtime(self) -> Dict[str, Any]:
        """Install Node.js runtime"""
        if self._is_command_available('node'):
            version = self._get_command_output('node --version')
            npm_version = self._get_command_output('npm --version')
            return {
                'success': True,
                'info': {
                    'runtime': 'node',
                    'version': version,
                    'npm_version': npm_version,
                    'path': shutil.which('node')
                }
            }
        
        if self.system_os == 'darwin':
            success, output, error = self._safe_execute('brew install node')
        elif self.system_os == 'linux':
            # Install via NodeSource repository for latest version
            commands = [
                'curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -',
                'sudo apt-get install -y nodejs'
            ]
            for cmd in commands:
                success, output, error = self._safe_execute(cmd)
                if success != 0:
                    break
        else:
            return {'success': False, 'error': 'Unsupported operating system'}
        
        if success == 0:
            version = self._get_command_output('node --version')
            return {
                'success': True,
                'info': {
                    'runtime': 'node',
                    'version': version,
                    'path': shutil.which('node')
                }
            }
        else:
            return {'success': False, 'error': error}
    
    def _install_go_runtime(self) -> Dict[str, Any]:
        """Install Go runtime"""
        if self._is_command_available('go'):
            version = self._get_command_output('go version')
            return {
                'success': True,
                'info': {
                    'runtime': 'go',
                    'version': version,
                    'path': shutil.which('go')
                }
            }
        
        if self.system_os == 'darwin':
            success, output, error = self._safe_execute('brew install go')
        elif self.system_os == 'linux':
            # Download and install Go from official source
            go_version = "1.21.3"  # Update as needed
            arch_map = {'x86_64': 'amd64', 'aarch64': 'arm64', 'arm64': 'arm64'}
            arch = arch_map.get(self.architecture, 'amd64')
            
            commands = [
                f'wget https://golang.org/dl/go{go_version}.linux-{arch}.tar.gz',
                'sudo rm -rf /usr/local/go',
                f'sudo tar -C /usr/local -xzf go{go_version}.linux-{arch}.tar.gz',
                'echo "export PATH=$PATH:/usr/local/go/bin" >> ~/.bashrc'
            ]
            
            for cmd in commands:
                success, output, error = self._safe_execute(cmd)
                if success != 0:
                    break
        else:
            return {'success': False, 'error': 'Unsupported operating system'}
        
        if success == 0:
            # Source bashrc to get Go in PATH
            os.environ['PATH'] += ':/usr/local/go/bin'
            version = self._get_command_output('go version')
            return {
                'success': True,
                'info': {
                    'runtime': 'go',
                    'version': version,
                    'path': '/usr/local/go/bin/go'
                }
            }
        else:
            return {'success': False, 'error': error}
    
    def _install_java_runtime(self) -> Dict[str, Any]:
        """Install Java runtime"""
        if self._is_command_available('java'):
            version = self._get_command_output('java -version')
            return {
                'success': True,
                'info': {
                    'runtime': 'java',
                    'version': version,
                    'path': shutil.which('java')
                }
            }
        
        if self.system_os == 'darwin':
            success, output, error = self._safe_execute('brew install openjdk@17')
        elif self.system_os == 'linux':
            if self._is_command_available('apt-get'):
                success, output, error = self._safe_execute('sudo apt-get install -y openjdk-17-jdk')
            elif self._is_command_available('yum'):
                success, output, error = self._safe_execute('sudo yum install -y java-17-openjdk-devel')
            else:
                return {'success': False, 'error': 'No supported package manager found'}
        else:
            return {'success': False, 'error': 'Unsupported operating system'}
        
        if success == 0:
            version = self._get_command_output('java -version')
            return {
                'success': True,
                'info': {
                    'runtime': 'java',
                    'version': version,
                    'path': shutil.which('java')
                }
            }
        else:
            return {'success': False, 'error': error}
    
    def _install_dotnet_runtime(self) -> Dict[str, Any]:
        """Install .NET runtime"""
        if self._is_command_available('dotnet'):
            version = self._get_command_output('dotnet --version')
            return {
                'success': True,
                'info': {
                    'runtime': 'dotnet',
                    'version': version,
                    'path': shutil.which('dotnet')
                }
            }
        
        if self.system_os == 'darwin':
            success, output, error = self._safe_execute('brew install dotnet')
        elif self.system_os == 'linux':
            # Install via Microsoft repository
            commands = [
                'wget https://packages.microsoft.com/config/ubuntu/22.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb',
                'sudo dpkg -i packages-microsoft-prod.deb',
                'sudo apt-get update',
                'sudo apt-get install -y dotnet-sdk-7.0'
            ]
            
            for cmd in commands:
                success, output, error = self._safe_execute(cmd)
                if success != 0:
                    break
        else:
            return {'success': False, 'error': 'Unsupported operating system'}
        
        if success == 0:
            version = self._get_command_output('dotnet --version')
            return {
                'success': True,
                'info': {
                    'runtime': 'dotnet',
                    'version': version,
                    'path': shutil.which('dotnet')
                }
            }
        else:
            return {'success': False, 'error': error}
    
    def _install_rust_runtime(self) -> Dict[str, Any]:
        """Install Rust runtime"""
        if self._is_command_available('rustc'):
            version = self._get_command_output('rustc --version')
            return {
                'success': True,
                'info': {
                    'runtime': 'rustc',
                    'version': version,
                    'path': shutil.which('rustc')
                }
            }
        
        # Install Rust via rustup (cross-platform)
        success, output, error = self._safe_execute('curl --proto "=https" --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y')
        
        if success == 0:
            # Source the cargo env
            cargo_env = os.path.expanduser('~/.cargo/env')
            if os.path.exists(cargo_env):
                # Add cargo to PATH
                cargo_bin = os.path.expanduser('~/.cargo/bin')
                os.environ['PATH'] = f"{cargo_bin}:{os.environ['PATH']}"
                
            version = self._get_command_output('rustc --version')
            return {
                'success': True,
                'info': {
                    'runtime': 'rustc',
                    'version': version,
                    'path': os.path.expanduser('~/.cargo/bin/rustc')
                }
            }
        else:
            return {'success': False, 'error': error}
    
    def _install_generic_runtime(self) -> Dict[str, Any]:
        """Generic runtime installer - indicates language detected but no specific installer"""
        return {
            'success': True,
            'info': {
                'runtime': 'generic',
                'message': 'Language detected but no specific runtime installer available',
                'suggestion': 'Install manually or use system package manager'
            }
        }
    
    def _install_web_runtime(self) -> Dict[str, Any]:
        """Install web development runtime (Node.js for web tools)"""
        return self._install_nodejs_runtime()
    
    def _install_docker_runtime(self) -> Dict[str, Any]:
        """Install Docker runtime"""
        if self._is_command_available('docker'):
            version = self._get_command_output('docker --version')
            return {
                'success': True,
                'info': {
                    'runtime': 'docker',
                    'version': version,
                    'path': shutil.which('docker')
                }
            }
        
        return {
            'success': False,
            'error': 'Please install Docker from https://docker.com'
        }
    
    def _install_powershell_runtime(self) -> Dict[str, Any]:
        """Install PowerShell runtime"""
        if self._is_command_available('pwsh') or self._is_command_available('powershell'):
            version = self._get_command_output('pwsh --version') or self._get_command_output('powershell --version')
            return {
                'success': True,
                'info': {
                    'runtime': 'powershell',
                    'version': version,
                    'path': shutil.which('pwsh') or shutil.which('powershell')
                }
            }
        
        return {
            'success': False,
            'error': 'Please install PowerShell from https://github.com/PowerShell/PowerShell'
        }
    
    def _install_terraform_runtime(self) -> Dict[str, Any]:
        """Install Terraform runtime"""
        if self._is_command_available('terraform'):
            version = self._get_command_output('terraform version')
            return {
                'success': True,
                'info': {
                    'runtime': 'terraform',
                    'version': version,
                    'path': shutil.which('terraform')
                }
            }
        
        return {
            'success': False,
            'error': 'Please install Terraform from https://terraform.io'
        }
    
    def _install_package_manager(self, language: str) -> Dict[str, Any]:
        """Install package manager for language"""
        
        package_managers = {
            'python': ['pip', 'poetry', 'pipenv'],
            'javascript': ['npm', 'yarn', 'pnpm'],
            'typescript': ['npm', 'yarn', 'pnpm'],
            'go': ['go mod'],
            'java': ['maven', 'gradle'],
            'csharp': ['nuget'],
            'rust': ['cargo'],
            'cpp': ['vcpkg', 'conan'],
            'php': ['composer'],
            'ruby': ['gem', 'bundler'],
            'swift': ['swift package manager'],
            'kotlin': ['gradle', 'maven'],
            'scala': ['sbt']
        }
        
        managers = package_managers.get(language, [])
        installed_tools = []
        
        for manager in managers:
            if self._install_single_package_manager(manager):
                installed_tools.append(manager)
        
        return {
            'success': len(installed_tools) > 0,
            'tools': installed_tools
        }
    
    def _install_single_package_manager(self, manager: str) -> bool:
        """Install a single package manager"""
        
        install_commands = {
            'pip': None,  # Usually comes with Python
            'poetry': 'curl -sSL https://install.python-poetry.org | python3 -',
            'yarn': 'npm install -g yarn',
            'pnpm': 'npm install -g pnpm',
            'maven': self._install_maven,
            'gradle': self._install_gradle,
            'composer': self._install_composer,
            'bundler': 'gem install bundler'
        }
        
        if manager in ['pip', 'npm', 'cargo', 'go mod', 'nuget', 'gem']:
            # These usually come with their runtimes
            return self._is_command_available(manager.split()[0])
        
        install_cmd = install_commands.get(manager)
        if install_cmd:
            if callable(install_cmd):
                return install_cmd()
            else:
                success, _, _ = self._safe_execute(install_cmd)
                return success == 0
        
        return False
    
    def _install_development_tools(self, language: str) -> Dict[str, Any]:
        """Install development tools for language"""
        
        dev_tools = {
            'python': ['black', 'pylint', 'mypy', 'pytest'],
            'javascript': ['eslint', 'prettier', 'jest'],
            'typescript': ['tslint', 'ts-node'],
            'go': ['golint', 'gofmt', 'go vet'],
            'java': ['checkstyle', 'spotbugs'],
            'csharp': ['dotnet-format'],
            'rust': ['clippy', 'rustfmt'],
            'cpp': ['clang-format', 'cppcheck'],
            'php': ['phpcs', 'phpunit'],
            'ruby': ['rubocop', 'rspec'],
            'swift': ['swiftlint'],
            'kotlin': ['ktlint']
        }
        
        tools = dev_tools.get(language, [])
        installed_tools = []
        
        for tool in tools:
            if self._install_development_tool(language, tool):
                installed_tools.append(tool)
        
        return {'tools': installed_tools}
    
    def _install_development_tool(self, language: str, tool: str) -> bool:
        """Install a specific development tool"""
        
        # Language-specific installation commands
        install_commands = {
            'python': {
                'black': 'pip install black',
                'pylint': 'pip install pylint',
                'mypy': 'pip install mypy',
                'pytest': 'pip install pytest'
            },
            'javascript': {
                'eslint': 'npm install -g eslint',
                'prettier': 'npm install -g prettier',
                'jest': 'npm install -g jest'
            },
            'go': {
                'golint': 'go install golang.org/x/lint/golint@latest',
                'gofmt': None,  # Built into Go
                'go vet': None  # Built into Go
            },
            'rust': {
                'clippy': 'rustup component add clippy',
                'rustfmt': 'rustup component add rustfmt'
            }
        }
        
        lang_commands = install_commands.get(language, {})
        cmd = lang_commands.get(tool)
        
        if cmd is None and tool in ['gofmt', 'go vet']:
            # These are built into Go
            return True
        
        if cmd:
            success, _, _ = self._safe_execute(cmd)
            return success == 0
        
        return False
    
    def _generate_workflow_config(self, language: str, project_path: Optional[str] = None) -> Dict[str, Any]:
        """Generate CI/CD workflow configuration for language"""
        
        workflow_templates = {
            'python': self._generate_python_workflow,
            'javascript': self._generate_javascript_workflow,
            'typescript': self._generate_typescript_workflow,
            'go': self._generate_go_workflow,
            'java': self._generate_java_workflow,
            'csharp': self._generate_csharp_workflow,
            'rust': self._generate_rust_workflow,
            'cpp': self._generate_cpp_workflow,
            'php': self._generate_php_workflow,
            'ruby': self._generate_ruby_workflow
        }
        
        generator = workflow_templates.get(language)
        if generator:
            return generator(project_path)
        else:
            return self._generate_generic_workflow(language)
    
    def _generate_python_workflow(self, project_path: Optional[str] = None) -> Dict[str, Any]:
        """Generate Python-specific workflow"""
        return {
            'name': f'Python CI',
            'on': ['push', 'pull_request'],
            'jobs': {
                'test': {
                    'runs-on': 'ubuntu-latest',
                    'strategy': {
                        'matrix': {
                            'python-version': ['3.8', '3.9', '3.10', '3.11']
                        }
                    },
                    'steps': [
                        {'uses': 'actions/checkout@v4'},
                        {
                            'name': 'Set up Python ${{ matrix.python-version }}',
                            'uses': 'actions/setup-python@v4',
                            'with': {'python-version': '${{ matrix.python-version }}'}
                        },
                        {
                            'name': 'Install dependencies',
                            'run': 'pip install -r requirements.txt || pip install -e .'
                        },
                        {
                            'name': 'Run CodeSnip Analysis',
                            'run': 'codesnip premerge-analyze --pr ${{ github.event.pull_request.number }} --create-status --post-comment'
                        },
                        {
                            'name': 'Lint with pylint',
                            'run': 'pylint $(find . -name "*.py")'
                        },
                        {
                            'name': 'Test with pytest',
                            'run': 'pytest --cov=. --cov-report=xml'
                        },
                        {
                            'name': 'Security check with bandit',
                            'run': 'bandit -r .'
                        }
                    ]
                }
            }
        }
    
    def _generate_go_workflow(self, project_path: Optional[str] = None) -> Dict[str, Any]:
        """Generate Go-specific workflow"""
        return {
            'name': 'Go CI',
            'on': ['push', 'pull_request'],
            'jobs': {
                'test': {
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {'uses': 'actions/checkout@v4'},
                        {
                            'name': 'Set up Go',
                            'uses': 'actions/setup-go@v4',
                            'with': {'go-version': '1.21'}
                        },
                        {
                            'name': 'Run CodeSnip Analysis',
                            'run': 'codesnip premerge-analyze --pr ${{ github.event.pull_request.number }} --create-status --post-comment'
                        },
                        {
                            'name': 'Build',
                            'run': 'go build -v ./...'
                        },
                        {
                            'name': 'Test',
                            'run': 'go test -v ./...'
                        },
                        {
                            'name': 'Vet',
                            'run': 'go vet ./...'
                        },
                        {
                            'name': 'Lint',
                            'run': 'golangci-lint run'
                        },
                        {
                            'name': 'Security check',
                            'run': 'gosec ./...'
                        }
                    ]
                }
            }
        }
    
    # Helper methods
    def _is_command_available(self, command: str) -> bool:
        """Check if a command is available"""
        return shutil.which(command) is not None
    
    def _safe_execute(self, command: str, timeout: int = 300) -> Tuple[int, str, str]:
        """Safely execute a command"""
        try:
            cmd_parts = shlex.split(command)
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)
    
    def _get_command_output(self, command: str) -> str:
        """Get command output safely"""
        try:
            result = subprocess.run(
                shlex.split(command),
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout.strip() if result.returncode == 0 else ""
        except:
            return ""
    
    def _save_workflow_config(self, language: str, workflow: Dict[str, Any], project_path: Optional[str] = None) -> None:
        """Save workflow configuration to file"""
        try:
            if project_path:
                workflows_dir = Path(project_path) / '.github' / 'workflows'
            else:
                workflows_dir = Path('.github') / 'workflows'
            
            workflows_dir.mkdir(parents=True, exist_ok=True)
            
            workflow_file = workflows_dir / f'{language}_ci.yml'
            
            with open(workflow_file, 'w') as f:
                yaml.dump(workflow, f, default_flow_style=False, sort_keys=False)
                
            logger.info(f"Workflow configuration saved to {workflow_file}")
            
        except Exception as e:
            logger.error(f"Failed to save workflow config: {e}")
    
    def _generate_setup_instructions(self, languages: List[str], results: Dict[str, Any]) -> List[str]:
        """Generate setup instructions based on installation results"""
        instructions = []
        
        if results['failed_installations']:
            instructions.append("❌ Some installations failed. Please check the errors and install manually:")
            for failure in results['failed_installations']:
                instructions.append(f"  - {failure.get('language', 'Unknown')}: {failure.get('error', 'Unknown error')}")
        
        if results['installed_runtimes']:
            instructions.append("✅ Successfully installed runtimes for: " + ", ".join(results['installed_runtimes']))
        
        instructions.append("📝 Next steps:")
        instructions.append("  1. Verify installations by running version commands")
        instructions.append("  2. Check generated CI/CD workflows in .github/workflows/")
        instructions.append("  3. Run 'codesnip premerge-analyze' to test the setup")
        instructions.append("  4. Configure additional language-specific tools as needed")
        
        return instructions
    
    # Additional installers
    def _install_maven(self) -> bool:
        """Install Apache Maven"""
        if self.system_os == 'darwin':
            success, _, _ = self._safe_execute('brew install maven')
        elif self.system_os == 'linux':
            success, _, _ = self._safe_execute('sudo apt-get install -y maven')
        else:
            return False
        return success == 0
    
    def _install_gradle(self) -> bool:
        """Install Gradle"""
        if self.system_os == 'darwin':
            success, _, _ = self._safe_execute('brew install gradle')
        elif self.system_os == 'linux':
            success, _, _ = self._safe_execute('sudo apt-get install -y gradle')
        else:
            return False
        return success == 0
    
    def _install_composer(self) -> bool:
        """Install PHP Composer"""
        commands = [
            'curl -sS https://getcomposer.org/installer | php',
            'sudo mv composer.phar /usr/local/bin/composer',
            'sudo chmod +x /usr/local/bin/composer'
        ]
        
        for cmd in commands:
            success, _, _ = self._safe_execute(cmd)
            if success != 0:
                return False
        return True