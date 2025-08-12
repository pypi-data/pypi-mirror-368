"""
Language-specific quality checkers with dynamic tool installation
"""
import os
import subprocess
import logging
import json
import shlex
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import tempfile
import shutil
import platform

logger = logging.getLogger(__name__)

class QualityCheckerManager:
    """Manages quality checks for different programming languages"""
    
    def __init__(self):
        self.system_os = platform.system().lower()
        self.temp_dir = None
        self.installed_tools = set()
    
    def analyze_language_quality(self, language: str, code_content: str, 
                               repo_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Run quality analysis for specific language
        
        Args:
            language: Programming language
            code_content: Code content to analyze
            repo_path: Optional path to repository
            
        Returns:
            Quality analysis results
        """
        logger.info(f"🔍 Running quality analysis for {language}")
        
        # Create temporary directory for analysis
        self.temp_dir = tempfile.mkdtemp(prefix=f"codesnip_{language}_")
        
        try:
            # Install required tools for the language
            self._install_language_tools(language)
            
            # Run language-specific quality checks
            results = self._run_language_checks(language, code_content, repo_path)
            
            return {
                'language': language,
                'quality_score': results.get('quality_score', 0),
                'issues': results.get('issues', []),
                'metrics': results.get('metrics', {}),
                'tools_used': results.get('tools_used', []),
                'suggestions': results.get('suggestions', [])
            }
            
        finally:
            # Cleanup temporary directory
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _install_language_tools(self, language: str) -> None:
        """Install required tools for the language"""
        tool_installers = {
            'python': self._install_python_tools,
            'javascript': self._install_javascript_tools,
            'typescript': self._install_typescript_tools,
            'go': self._install_go_tools,
            'java': self._install_java_tools,
            'csharp': self._install_csharp_tools,
            'rust': self._install_rust_tools,
            'cpp': self._install_cpp_tools,
            'php': self._install_php_tools,
            'ruby': self._install_ruby_tools,
            'swift': self._install_swift_tools,
            'kotlin': self._install_kotlin_tools
        }
        
        installer = tool_installers.get(language)
        if installer:
            installer()
        else:
            logger.warning(f"No tool installer available for {language}")
    
    def _install_python_tools(self) -> None:
        """Install Python quality tools"""
        tools = [
            ('pylint', 'pip install pylint'),
            ('black', 'pip install black'),
            ('flake8', 'pip install flake8'),
            ('mypy', 'pip install mypy'),
            ('bandit', 'pip install bandit'),
            ('safety', 'pip install safety'),
            ('pytest', 'pip install pytest'),
            ('coverage', 'pip install coverage')
        ]
        
        for tool_name, install_cmd in tools:
            if not self._is_tool_available(tool_name):
                logger.info(f"Installing {tool_name}...")
                self._safe_execute(install_cmd)
                self.installed_tools.add(tool_name)
    
    def _install_javascript_tools(self) -> None:
        """Install JavaScript quality tools"""
        # Check if npm is available
        if not self._is_tool_available('npm'):
            logger.warning("npm not found. Please install Node.js first.")
            return
        
        tools = [
            ('eslint', 'npm install -g eslint'),
            ('prettier', 'npm install -g prettier'),
            ('jshint', 'npm install -g jshint'),
            ('jest', 'npm install -g jest'),
            ('audit', None)  # Built into npm
        ]
        
        for tool_name, install_cmd in tools:
            if install_cmd and not self._is_tool_available(tool_name):
                logger.info(f"Installing {tool_name}...")
                self._safe_execute(install_cmd)
                self.installed_tools.add(tool_name)
    
    def _install_typescript_tools(self) -> None:
        """Install TypeScript quality tools"""
        if not self._is_tool_available('npm'):
            logger.warning("npm not found. Please install Node.js first.")
            return
        
        tools = [
            ('typescript', 'npm install -g typescript'),
            ('tslint', 'npm install -g tslint'),
            ('ts-node', 'npm install -g ts-node'),
            ('@typescript-eslint/eslint-plugin', 'npm install -g @typescript-eslint/eslint-plugin')
        ]
        
        for tool_name, install_cmd in tools:
            if not self._is_tool_available(tool_name.split('/')[-1]):
                logger.info(f"Installing {tool_name}...")
                self._safe_execute(install_cmd)
                self.installed_tools.add(tool_name)
    
    def _install_go_tools(self) -> None:
        """Install Go quality tools"""
        if not self._is_tool_available('go'):
            logger.warning("Go not found. Please install Go first.")
            return
        
        tools = [
            ('golint', 'go install golang.org/x/lint/golint@latest'),
            ('staticcheck', 'go install honnef.co/go/tools/cmd/staticcheck@latest'),
            ('gosec', 'go install github.com/securecodewarrior/gosec/v2/cmd/gosec@latest'),
            ('goimports', 'go install golang.org/x/tools/cmd/goimports@latest'),
            ('golangci-lint', self._install_golangci_lint)
        ]
        
        for tool_name, install_cmd in tools:
            if not self._is_tool_available(tool_name):
                logger.info(f"Installing {tool_name}...")
                if callable(install_cmd):
                    install_cmd()
                else:
                    self._safe_execute(install_cmd)
                self.installed_tools.add(tool_name)
    
    def _install_java_tools(self) -> None:
        """Install Java quality tools"""
        if not self._is_tool_available('java'):
            logger.warning("Java not found. Please install Java first.")
            return
        
        # Most Java tools are Maven/Gradle plugins, check if build tools are available
        has_maven = self._is_tool_available('mvn')
        has_gradle = self._is_tool_available('gradle')
        
        if not (has_maven or has_gradle):
            logger.warning("Neither Maven nor Gradle found. Java quality tools require a build system.")
            return
        
        logger.info("Java quality tools will be configured via build system plugins")
        # Note: Tools like Checkstyle, SpotBugs, PMD are typically configured as plugins
    
    def _install_csharp_tools(self) -> None:
        """Install C# quality tools"""
        if not self._is_tool_available('dotnet'):
            logger.warning("dotnet CLI not found. Please install .NET SDK first.")
            return
        
        tools = [
            ('dotnet-format', 'dotnet tool install -g dotnet-format'),
            ('security-scan', 'dotnet tool install -g security-scan'),
            ('dotnet-outdated', 'dotnet tool install -g dotnet-outdated')
        ]
        
        for tool_name, install_cmd in tools:
            logger.info(f"Installing {tool_name}...")
            self._safe_execute(install_cmd)
            self.installed_tools.add(tool_name)
    
    def _install_rust_tools(self) -> None:
        """Install Rust quality tools"""
        if not self._is_tool_available('cargo'):
            logger.warning("Cargo not found. Please install Rust first.")
            return
        
        tools = [
            ('clippy', 'rustup component add clippy'),
            ('rustfmt', 'rustup component add rustfmt'),
            ('cargo-audit', 'cargo install cargo-audit'),
            ('cargo-outdated', 'cargo install cargo-outdated')
        ]
        
        for tool_name, install_cmd in tools:
            if not self._is_tool_available(tool_name):
                logger.info(f"Installing {tool_name}...")
                self._safe_execute(install_cmd)
                self.installed_tools.add(tool_name)
    
    def _install_cpp_tools(self) -> None:
        """Install C++ quality tools"""
        tools_info = [
            ('cppcheck', 'Static analysis tool for C/C++'),
            ('clang-tidy', 'Clang-based linter for C++'),
            ('valgrind', 'Memory error detector'),
            ('cmake', 'Build system generator')
        ]
        
        available_tools = []
        for tool, description in tools_info:
            if self._is_tool_available(tool):
                available_tools.append(tool)
                self.installed_tools.add(tool)
            else:
                logger.warning(f"{tool} ({description}) not found. Please install manually.")
        
        logger.info(f"Available C++ tools: {available_tools}")
    
    def _install_php_tools(self) -> None:
        """Install PHP quality tools"""
        if not self._is_tool_available('php'):
            logger.warning("PHP not found. Please install PHP first.")
            return
        
        if not self._is_tool_available('composer'):
            logger.warning("Composer not found. Please install Composer first.")
            return
        
        # Create a temporary composer.json for global tools
        composer_config = {
            "require-dev": {
                "phpunit/phpunit": "^9.0",
                "squizlabs/php_codesniffer": "^3.6",
                "phpstan/phpstan": "^1.0",
                "psalm/psalm": "^4.0"
            }
        }
        
        logger.info("Installing PHP quality tools via Composer...")
        # Note: In practice, these would be installed globally or per-project
    
    def _install_ruby_tools(self) -> None:
        """Install Ruby quality tools"""
        if not self._is_tool_available('ruby'):
            logger.warning("Ruby not found. Please install Ruby first.")
            return
        
        tools = [
            ('rubocop', 'gem install rubocop'),
            ('bundler-audit', 'gem install bundler-audit'),
            ('reek', 'gem install reek'),
            ('rspec', 'gem install rspec')
        ]
        
        for tool_name, install_cmd in tools:
            if not self._is_tool_available(tool_name):
                logger.info(f"Installing {tool_name}...")
                self._safe_execute(install_cmd)
                self.installed_tools.add(tool_name)
    
    def _install_swift_tools(self) -> None:
        """Install Swift quality tools"""
        if not self._is_tool_available('swift'):
            logger.warning("Swift not found. Please install Swift first.")
            return
        
        tools = [
            ('swiftlint', self._install_swiftlint),
            ('swiftformat', 'mint install nicklockwood/SwiftFormat')
        ]
        
        for tool_name, install_cmd in tools:
            if not self._is_tool_available(tool_name):
                logger.info(f"Installing {tool_name}...")
                if callable(install_cmd):
                    install_cmd()
                else:
                    self._safe_execute(install_cmd)
                self.installed_tools.add(tool_name)
    
    def _install_kotlin_tools(self) -> None:
        """Install Kotlin quality tools"""
        if not self._is_tool_available('java'):
            logger.warning("Java not found. Please install Java first.")
            return
        
        # Kotlin tools are typically Gradle plugins
        logger.info("Kotlin quality tools will be configured via Gradle plugins")
        tools = ['ktlint', 'detekt']
        for tool in tools:
            self.installed_tools.add(tool)
    
    def _run_language_checks(self, language: str, code_content: str, 
                           repo_path: Optional[str] = None) -> Dict[str, Any]:
        """Run quality checks for specific language"""
        
        checkers = {
            'python': self._check_python_quality,
            'javascript': self._check_javascript_quality,
            'typescript': self._check_typescript_quality,
            'go': self._check_go_quality,
            'java': self._check_java_quality,
            'csharp': self._check_csharp_quality,
            'rust': self._check_rust_quality,
            'cpp': self._check_cpp_quality,
            'php': self._check_php_quality,
            'ruby': self._check_ruby_quality,
            'swift': self._check_swift_quality,
            'kotlin': self._check_kotlin_quality
        }
        
        checker = checkers.get(language)
        if checker:
            return checker(code_content, repo_path)
        else:
            return {
                'quality_score': 50,
                'issues': [f"No quality checker available for {language}"],
                'metrics': {},
                'tools_used': [],
                'suggestions': [f"Consider adding quality tools for {language}"]
            }
    
    def _check_python_quality(self, code_content: str, repo_path: Optional[str] = None) -> Dict[str, Any]:
        """Run Python quality checks"""
        issues = []
        metrics = {}
        tools_used = []
        
        # Create temporary Python file
        temp_file = os.path.join(self.temp_dir, 'temp_code.py')
        with open(temp_file, 'w') as f:
            f.write(code_content)
        
        # Run Pylint
        if 'pylint' in self.installed_tools:
            pylint_result = self._run_pylint(temp_file)
            issues.extend(pylint_result.get('issues', []))
            metrics.update(pylint_result.get('metrics', {}))
            tools_used.append('pylint')
        
        # Run Black (formatting check)
        if 'black' in self.installed_tools:
            black_result = self._run_black_check(temp_file)
            issues.extend(black_result.get('issues', []))
            tools_used.append('black')
        
        # Run Bandit (security)
        if 'bandit' in self.installed_tools:
            bandit_result = self._run_bandit(temp_file)
            issues.extend(bandit_result.get('issues', []))
            tools_used.append('bandit')
        
        # Calculate quality score
        quality_score = max(0, 100 - len(issues) * 5)
        
        return {
            'quality_score': quality_score,
            'issues': issues,
            'metrics': metrics,
            'tools_used': tools_used,
            'suggestions': self._get_python_suggestions(issues)
        }
    
    def _check_go_quality(self, code_content: str, repo_path: Optional[str] = None) -> Dict[str, Any]:
        """Run Go quality checks"""
        issues = []
        metrics = {}
        tools_used = []
        
        # Create temporary Go file
        temp_file = os.path.join(self.temp_dir, 'temp_code.go')
        with open(temp_file, 'w') as f:
            f.write(code_content)
        
        # Run go fmt check
        if self._is_tool_available('go'):
            fmt_result = self._run_go_fmt_check(temp_file)
            issues.extend(fmt_result.get('issues', []))
            tools_used.append('gofmt')
        
        # Run go vet
        if self._is_tool_available('go'):
            vet_result = self._run_go_vet(temp_file)
            issues.extend(vet_result.get('issues', []))
            tools_used.append('go vet')
        
        # Run staticcheck
        if 'staticcheck' in self.installed_tools:
            staticcheck_result = self._run_staticcheck(temp_file)
            issues.extend(staticcheck_result.get('issues', []))
            tools_used.append('staticcheck')
        
        quality_score = max(0, 100 - len(issues) * 3)
        
        return {
            'quality_score': quality_score,
            'issues': issues,
            'metrics': metrics,
            'tools_used': tools_used,
            'suggestions': self._get_go_suggestions(issues)
        }
    
    def _check_javascript_quality(self, code_content: str, repo_path: Optional[str] = None) -> Dict[str, Any]:
        """Run JavaScript quality checks"""
        issues = []
        metrics = {}
        tools_used = []
        
        # Create temporary JS file
        temp_file = os.path.join(self.temp_dir, 'temp_code.js')
        with open(temp_file, 'w') as f:
            f.write(code_content)
        
        # Run ESLint
        if 'eslint' in self.installed_tools:
            eslint_result = self._run_eslint(temp_file)
            issues.extend(eslint_result.get('issues', []))
            tools_used.append('eslint')
        
        # Run JSHint
        if 'jshint' in self.installed_tools:
            jshint_result = self._run_jshint(temp_file)
            issues.extend(jshint_result.get('issues', []))
            tools_used.append('jshint')
        
        quality_score = max(0, 100 - len(issues) * 4)
        
        return {
            'quality_score': quality_score,
            'issues': issues,
            'metrics': metrics,
            'tools_used': tools_used,
            'suggestions': self._get_javascript_suggestions(issues)
        }
    
    # Tool execution helpers
    def _run_pylint(self, file_path: str) -> Dict[str, Any]:
        """Run Pylint analysis"""
        try:
            cmd = ['pylint', '--output-format=json', file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            issues = []
            metrics = {}
            
            if result.stdout:
                try:
                    pylint_output = json.loads(result.stdout)
                    for issue in pylint_output:
                        issues.append({
                            'type': issue.get('type', 'unknown'),
                            'message': issue.get('message', ''),
                            'line': issue.get('line', 0),
                            'severity': issue.get('message-id', 'unknown')
                        })
                except json.JSONDecodeError:
                    issues.append({'message': 'Failed to parse pylint output', 'severity': 'error'})
            
            return {'issues': issues, 'metrics': metrics}
            
        except Exception as e:
            logger.error(f"Pylint execution failed: {e}")
            return {'issues': [{'message': f'Pylint failed: {e}', 'severity': 'error'}], 'metrics': {}}
    
    def _run_black_check(self, file_path: str) -> Dict[str, Any]:
        """Check Black formatting"""
        try:
            cmd = ['black', '--check', '--diff', file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            issues = []
            if result.returncode != 0 and result.stdout:
                issues.append({
                    'message': 'Code formatting issues found',
                    'type': 'formatting',
                    'severity': 'warning'
                })
            
            return {'issues': issues}
            
        except Exception as e:
            logger.error(f"Black check failed: {e}")
            return {'issues': []}
    
    def _run_bandit(self, file_path: str) -> Dict[str, Any]:
        """Run Bandit security analysis"""
        try:
            cmd = ['bandit', '-f', 'json', file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            issues = []
            if result.stdout:
                try:
                    bandit_output = json.loads(result.stdout)
                    for issue in bandit_output.get('results', []):
                        issues.append({
                            'type': 'security',
                            'message': issue.get('issue_text', ''),
                            'line': issue.get('line_number', 0),
                            'severity': issue.get('issue_severity', 'unknown'),
                            'confidence': issue.get('issue_confidence', 'unknown')
                        })
                except json.JSONDecodeError:
                    pass
            
            return {'issues': issues}
            
        except Exception as e:
            logger.error(f"Bandit execution failed: {e}")
            return {'issues': []}
    
    # Helper methods
    def _is_tool_available(self, tool_name: str) -> bool:
        """Check if a tool is available in PATH"""
        return shutil.which(tool_name) is not None
    
    def _safe_execute(self, command: str, timeout: int = 60) -> Tuple[int, str, str]:
        """Safely execute a shell command"""
        try:
            # Split command safely
            cmd_parts = shlex.split(command)
            result = subprocess.run(
                cmd_parts, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                cwd=self.temp_dir
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {command}")
            return 1, "", "Command timed out"
        except Exception as e:
            logger.error(f"Command execution failed: {command}, Error: {e}")
            return 1, "", str(e)
    
    # Suggestion generators
    def _get_python_suggestions(self, issues: List[Dict]) -> List[str]:
        """Generate Python-specific suggestions"""
        suggestions = []
        
        issue_types = [issue.get('type', '') for issue in issues]
        
        if 'formatting' in issue_types:
            suggestions.append("Run 'black .' to fix formatting issues")
        
        if any('security' in issue.get('type', '') for issue in issues):
            suggestions.append("Review security issues flagged by Bandit")
        
        if len(issues) > 10:
            suggestions.append("Consider refactoring to reduce complexity")
        
        return suggestions
    
    def _get_go_suggestions(self, issues: List[Dict]) -> List[str]:
        """Generate Go-specific suggestions"""
        suggestions = []
        
        if any('fmt' in str(issue) for issue in issues):
            suggestions.append("Run 'go fmt' to fix formatting")
        
        if len(issues) > 5:
            suggestions.append("Review Go best practices and style guide")
        
        return suggestions
    
    def _get_javascript_suggestions(self, issues: List[Dict]) -> List[str]:
        """Generate JavaScript-specific suggestions"""
        suggestions = []
        
        if len(issues) > 8:
            suggestions.append("Consider using a linter like ESLint consistently")
        
        suggestions.append("Ensure consistent code style with Prettier")
        
        return suggestions
    
    # Additional tool installers
    def _install_golangci_lint(self) -> None:
        """Install golangci-lint"""
        if self.system_os == 'darwin':
            self._safe_execute('brew install golangci-lint')
        elif self.system_os == 'linux':
            self._safe_execute('curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | sh -s -- -b $(go env GOPATH)/bin')
        else:
            logger.warning("golangci-lint installation not supported on this OS")
    
    def _install_swiftlint(self) -> None:
        """Install SwiftLint"""
        if self.system_os == 'darwin':
            self._safe_execute('brew install swiftlint')
        else:
            logger.warning("SwiftLint is only supported on macOS")