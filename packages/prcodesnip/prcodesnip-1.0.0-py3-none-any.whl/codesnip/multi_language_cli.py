"""
Multi-language enhanced CLI commands with dynamic language detection and tool installation
"""
import click
import logging
import json
import asyncio
from typing import Dict, List, Optional, Any
from pathlib import Path

from codesnip.languages.language_detector import LanguageDetector
from codesnip.languages.quality_checkers import QualityCheckerManager
from codesnip.languages.package_manager import LanguagePackageManager
from codesnip.languages.i18n import i18n
from codesnip.config import get_config
from codesnip.github_fetcher import fetch_pr_data
from codesnip.analysis.memory_analyzer import analyze_memory_leaks
from codesnip.analysis.architecture_analyzer import analyze_architecture
from codesnip.analysis.performance_profiler import analyze_performance

logger = logging.getLogger(__name__)

class MultiLanguageAnalyzer:
    """Enhanced analyzer with multi-language support"""
    
    def __init__(self, github_token: str):
        self.github_token = github_token
        self.language_detector = LanguageDetector(github_token)
        self.quality_checker = QualityCheckerManager()
        self.package_manager = LanguagePackageManager()
    
    async def analyze_repository(self, repository: str, pr_number: Optional[int] = None) -> Dict[str, Any]:
        """
        Comprehensive multi-language repository analysis
        
        Args:
            repository: GitHub repository (owner/repo)
            pr_number: Optional PR number for PR-specific analysis
            
        Returns:
            Complete analysis results
        """
        logger.info(i18n.t("language_detection"))
        click.echo(f"🔍 {i18n.t('detecting_languages')} {repository}...")
        
        try:
            # Detect languages
            language_info = self.language_detector.detect_languages(repository, pr_number)
            primary_language = language_info.get('primary_language', 'unknown')
            detected_languages = list(language_info.get('languages', {}).keys())
            
            click.echo(f"🎯 {i18n.t('primary_language')}: {primary_language}")
            click.echo(f"📊 {i18n.t('detected_languages')}: {', '.join(detected_languages)}")
            
            # Install required tools
            click.echo(f"⚙️ {i18n.t('installing_tools')} {', '.join(detected_languages)}...")
            installation_result = self.package_manager.install_language_environment(
                detected_languages, 
                None  # Could pass repo path if cloned locally
            )
            
            if installation_result['success']:
                click.echo(f"✅ {i18n.t('tools_installed')}")
            else:
                click.echo(f"⚠️ {i18n.t('tools_failed')}")
            
            # Get PR data if analyzing a specific PR
            pr_data = None
            if pr_number:
                pr_data = fetch_pr_data(repository, pr_number, self.github_token)
            
            # Run comprehensive analysis for each detected language
            quality_results = {}
            memory_results = {}
            architecture_results = {}
            performance_results = {}
            
            for language in detected_languages:
                if language in ['python', 'javascript', 'typescript', 'go', 'java', 'rust', 'cpp', 'c', 'csharp']:
                    click.echo(f"🔍 Analyzing {language}...")
                    
                    # Extract code for this language from PR or repo
                    code_content = self._extract_language_code(pr_data, language) if pr_data else ""
                    
                    if code_content:
                        # Quality analysis
                        quality_result = self.quality_checker.analyze_language_quality(
                            language, code_content
                        )
                        quality_results[language] = quality_result
                        
                        # Memory leak analysis
                        memory_result = analyze_memory_leaks(language, code_content, f"temp_{language}_file")
                        memory_results[language] = memory_result
                        
                        # Architecture analysis
                        arch_result = analyze_architecture(f"temp_{language}_file", language, code_content)
                        architecture_results[language] = arch_result
                        
                        # Performance analysis
                        perf_result = analyze_performance(language, code_content, f"temp_{language}_file")
                        performance_results[language] = perf_result
            
            # Generate comprehensive report
            analysis_result = {
                'repository': repository,
                'pr_number': pr_number,
                'timestamp': click.get_current_context().obj.get('timestamp', ''),
                'language_detection': language_info,
                'installation_results': installation_result,
                'quality_analysis': quality_results,
                'memory_analysis': memory_results,
                'architecture_analysis': architecture_results,
                'performance_analysis': performance_results,
                'recommendations': self._generate_recommendations(language_info, quality_results, memory_results, architecture_results, performance_results),
                'next_steps': self._generate_next_steps(detected_languages, installation_result)
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Multi-language analysis failed: {e}")
            raise click.ClickException(f"{i18n.t('error')}: {e}")
    
    def _extract_language_code(self, pr_data: Dict, language: str) -> str:
        """Extract code for specific language from PR data"""
        if not pr_data or not pr_data.get('diff'):
            return ""
        
        diff_content = pr_data['diff']
        code_lines = []
        
        # Simple extraction - in reality would be more sophisticated
        for line in diff_content.split('\n'):
            if line.startswith('+') and not line.startswith('+++'):
                code_lines.append(line[1:])  # Remove the + prefix
        
        return '\n'.join(code_lines)
    
    def _generate_recommendations(self, language_info: Dict, quality_results: Dict, memory_results: Dict, architecture_results: Dict, performance_results: Dict) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        detected_languages = list(language_info.get('languages', {}).keys())
        primary_language = language_info.get('primary_language', 'unknown')
        
        # Language-specific recommendations
        if 'python' in detected_languages:
            recommendations.append("🐍 Consider using type hints for better code quality")
            recommendations.append("📦 Use virtual environments for dependency management")
        
        if 'javascript' in detected_languages:
            recommendations.append("⚡ Consider migrating to TypeScript for better type safety")
            recommendations.append("📦 Use npm audit for security vulnerability scanning")
        
        if 'go' in detected_languages:
            recommendations.append("🚀 Run go fmt and go vet regularly")
            recommendations.append("📊 Use go mod for dependency management")
        
        if 'java' in detected_languages:
            recommendations.append("☕ Configure CheckStyle for consistent code formatting")
            recommendations.append("🔒 Use SpotBugs for security analysis")
        
        # Quality-based recommendations
        for language, results in quality_results.items():
            quality_score = results.get('quality_score', 0)
            if quality_score < 70:
                recommendations.append(f"⚠️ {language.title()} code quality needs improvement (score: {quality_score}/100)")
            
            issues = results.get('issues', [])
            if len(issues) > 10:
                recommendations.append(f"🔧 Address {len(issues)} issues in {language} code")
        
        # Memory-based recommendations
        for language, results in memory_results.items():
            memory_score = results.get('memory_score', 100)
            if memory_score < 70:
                recommendations.append(f"🧠 {language.title()} has memory issues (score: {memory_score}/100)")
            
            leak_risks = results.get('leak_risks', [])
            if len(leak_risks) > 0:
                recommendations.append(f"⚠️ Found {len(leak_risks)} potential memory leaks in {language}")
        
        # Architecture-based recommendations
        for language, results in architecture_results.items():
            arch_score = results.get('architecture_score', 100)
            if arch_score < 70:
                recommendations.append(f"🏗️ {language.title()} architecture needs improvement (score: {arch_score}/100)")
            
            issues = results.get('issues', [])
            critical_issues = [i for i in issues if i.severity == 'high']
            if critical_issues:
                recommendations.append(f"🚨 {len(critical_issues)} critical architecture issues in {language}")
        
        # Performance-based recommendations
        for language, results in performance_results.items():
            perf_score = results.get('performance_score', 100)
            if perf_score < 70:
                recommendations.append(f"⚡ {language.title()} performance needs optimization (score: {perf_score}/100)")
            
            bottlenecks = results.get('bottlenecks', [])
            critical_bottlenecks = [b for b in bottlenecks if b.get('severity') == 'high']
            if critical_bottlenecks:
                recommendations.append(f"🔥 {len(critical_bottlenecks)} critical performance bottlenecks in {language}")
        
        # Multi-language project recommendations
        if len(detected_languages) > 3:
            recommendations.append("🏗️ Consider using monorepo tools for multi-language projects")
            recommendations.append("🔄 Set up language-specific CI/CD pipelines")
        
        return recommendations
    
    def _generate_next_steps(self, languages: List[str], installation_result: Dict) -> List[str]:
        """Generate next steps for the user"""
        next_steps = []
        
        if installation_result.get('failed_installations'):
            next_steps.append("🔧 Resolve failed tool installations manually")
            for failure in installation_result['failed_installations']:
                next_steps.append(f"  - Install {failure.get('language', 'unknown')} tools")
        
        next_steps.append("📊 Review generated CI/CD workflows in .github/workflows/")
        next_steps.append("⚙️ Customize quality rules for your project needs")
        next_steps.append("🚀 Run regular quality checks in your development workflow")
        
        if len(languages) > 1:
            next_steps.append("🏗️ Consider setting up pre-commit hooks for all languages")
        
        return next_steps

# CLI Commands
@click.group()
def language_commands():
    """Multi-language support commands"""
    pass

@language_commands.command()
@click.option('--repo', type=str, help='GitHub repository (owner/repo)')
@click.option('--pr', type=int, help='Pull request number')
@click.option('--token', type=str, help='GitHub token')
@click.option('--output', type=str, help='Output file for results')
@click.option('--format', default='json', type=click.Choice(['json', 'yaml', 'markdown']), help='Output format')
@click.option('--install-tools', is_flag=True, help='Install required language tools')
@click.pass_context
def detect_languages(ctx, repo, pr, token, output, format, install_tools):
    """🔍 Detect programming languages and setup development environment"""
    
    config = get_config()
    github_token = config.get_github_token(token)
    
    if not github_token:
        raise click.ClickException(f"{i18n.t('token_required')}")
    
    if not repo:
        # Use interactive prompts
        from codesnip.interactive_prompts import get_repository_and_pr_interactive
        repo, pr = get_repository_and_pr_interactive(
            github_token=github_token,
            provided_repo=repo,
            provided_pr=pr,
            default_repo=config.get_default_repo()
        )
    
    try:
        analyzer = MultiLanguageAnalyzer(github_token)
        
        # Run analysis
        result = asyncio.run(analyzer.analyze_repository(repo, pr))
        
        # Display results
        click.echo(f"\n🎯 {i18n.t('analysis_completed')}")
        click.echo("=" * 50)
        
        # Show language detection results
        language_info = result['language_detection']
        primary_lang = language_info.get('primary_language', 'unknown')
        detected_langs = list(language_info.get('languages', {}).keys())
        
        click.echo(f"📊 {i18n.t('primary_language')}: {primary_lang}")
        click.echo(f"🔍 {i18n.t('detected_languages')}: {', '.join(detected_langs)}")
        
        # Show quality scores
        quality_results = result.get('quality_analysis', {})
        if quality_results:
            click.echo(f"\n📈 {i18n.t('quality_analysis')}:")
            for language, analysis in quality_results.items():
                score = analysis.get('quality_score', 0)
                issues = len(analysis.get('issues', []))
                click.echo(f"  {language}: {score}/100 ({issues} issues)")
        
        # Show recommendations
        recommendations = result.get('recommendations', [])
        if recommendations:
            click.echo(f"\n💡 {i18n.t('recommendations')}:")
            for rec in recommendations[:5]:  # Show top 5
                click.echo(f"  {rec}")
        
        # Show next steps
        next_steps = result.get('next_steps', [])
        if next_steps:
            click.echo(f"\n📋 {i18n.t('next_steps')}:")
            for step in next_steps:
                click.echo(f"  {step}")
        
        # Save results if output specified
        if output:
            output_path = Path(output)
            if format == 'json':
                with open(output_path, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
            elif format == 'yaml':
                import yaml
                with open(output_path, 'w') as f:
                    yaml.dump(result, f, default_flow_style=False)
            elif format == 'markdown':
                markdown_content = _generate_markdown_report(result)
                with open(output_path, 'w') as f:
                    f.write(markdown_content)
            
            click.echo(f"📄 Results saved to {output_path}")
        
    except Exception as e:
        logger.error(f"Language detection failed: {e}")
        raise click.ClickException(f"{i18n.t('error')}: {e}")

@language_commands.command()
@click.option('--language', required=True, type=str, help='Programming language')
@click.option('--project-path', type=str, help='Project path')
@click.pass_context
def setup_environment(ctx, language, project_path):
    """⚙️ Setup development environment for specific language"""
    
    try:
        click.echo(f"🚀 {i18n.t('installing_tools')} {language}...")
        
        package_manager = LanguagePackageManager()
        result = package_manager.install_language_environment([language], project_path)
        
        if result['success']:
            click.echo(f"✅ {i18n.t('success')} - Environment setup completed for {language}")
            
            # Show installed tools
            if result['installed_tools']:
                click.echo(f"🔧 Installed tools: {', '.join(result['installed_tools'])}")
            
            # Show next steps
            for step in result['next_steps']:
                click.echo(f"📋 {step}")
                
        else:
            click.echo(f"❌ {i18n.t('error')} - Environment setup failed")
            for failure in result.get('failed_installations', []):
                click.echo(f"  - {failure.get('error', 'Unknown error')}")
        
    except Exception as e:
        logger.error(f"Environment setup failed: {e}")
        raise click.ClickException(f"{i18n.t('error')}: {e}")

@language_commands.command()
@click.argument('language_code', required=False)
@click.pass_context
def set_language(ctx, language_code):
    """🌐 Set interface language"""
    
    if not language_code:
        # Show available languages
        click.echo("🌐 Available languages:")
        click.echo(i18n.list_languages())
        return
    
    if i18n.set_language(language_code):
        lang_info = i18n.get_language_info(language_code)
        click.echo(f"✅ {i18n.t('language_changed')} {lang_info['flag']} {lang_info['name']}")
        
        # Save language preference
        config = get_config()
        config.set_user_preference('language', language_code)
    else:
        click.echo(f"❌ {i18n.t('language_not_supported')}: {language_code}")

@language_commands.command()
@click.pass_context
def show_locale_info(ctx):
    """📍 Show current locale information"""
    
    locale_info = i18n.get_locale_info()
    
    click.echo("🌍 Locale Information")
    click.echo("=" * 30)
    click.echo(f"Language: {locale_info['flag']} {locale_info['language_name']} ({locale_info['language']})")
    click.echo(f"Locale: {locale_info['locale']}")
    click.echo(f"Currency: {locale_info['currency_symbol']}")
    click.echo(f"Number format: {i18n.format_number(1234.56)}")
    click.echo(f"Currency format: {i18n.format_currency(1234.56, 'USD')}")
    click.echo(f"Date format: {locale_info['date_format']}")
    click.echo(f"Time format: {locale_info['time_format']}")

def _generate_markdown_report(result: Dict[str, Any]) -> str:
    """Generate markdown report from analysis results"""
    
    md_content = [
        "# 🔍 Multi-Language Analysis Report",
        "",
        f"**Repository:** {result['repository']}",
        f"**Analysis Date:** {result.get('timestamp', 'N/A')}",
        ""
    ]
    
    # Language Detection Section
    language_info = result.get('language_detection', {})
    primary_lang = language_info.get('primary_language', 'unknown')
    detected_langs = list(language_info.get('languages', {}).keys())
    
    md_content.extend([
        "## 📊 Language Detection",
        "",
        f"- **Primary Language:** {primary_lang}",
        f"- **Detected Languages:** {', '.join(detected_langs)}",
        ""
    ])
    
    # Quality Analysis Section
    quality_results = result.get('quality_analysis', {})
    if quality_results:
        md_content.extend([
            "## 📈 Quality Analysis",
            ""
        ])
        
        for language, analysis in quality_results.items():
            score = analysis.get('quality_score', 0)
            issues = len(analysis.get('issues', []))
            tools_used = ', '.join(analysis.get('tools_used', []))
            
            md_content.extend([
                f"### {language.title()}",
                f"- **Quality Score:** {score}/100",
                f"- **Issues Found:** {issues}",
                f"- **Tools Used:** {tools_used}",
                ""
            ])
    
    # Recommendations Section
    recommendations = result.get('recommendations', [])
    if recommendations:
        md_content.extend([
            "## 💡 Recommendations",
            ""
        ])
        for rec in recommendations:
            md_content.append(f"- {rec}")
        md_content.append("")
    
    # Next Steps Section
    next_steps = result.get('next_steps', [])
    if next_steps:
        md_content.extend([
            "## 📋 Next Steps",
            ""
        ])
        for step in next_steps:
            md_content.append(f"1. {step}")
        md_content.append("")
    
    return '\n'.join(md_content)