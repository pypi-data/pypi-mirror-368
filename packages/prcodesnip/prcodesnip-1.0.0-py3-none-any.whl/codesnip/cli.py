import click
import logging
import requests
import psutil
import subprocess
import re
import os
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from codesnip.github_fetcher import fetch_pr_data
from codesnip.quality_checker import run_all_checks
from codesnip.openai_client import generate_release_notes
from codesnip.config import get_config
from codesnip.async_client import analyze_pr_async
from codesnip.premerge.draft_release_notes import DraftReleaseNotesGenerator
from codesnip.premerge.risk_predictor import EarlyRiskPredictor
from codesnip.workflow.github_integration import GitHubWorkflowIntegration, WorkflowStatusManager
from codesnip.setup_wizard import run_setup_wizard
from codesnip.interactive_prompts import get_repository_and_pr_interactive
from codesnip.multi_language_cli import language_commands, MultiLanguageAnalyzer
from codesnip.languages.i18n import i18n
import asyncio

# Set up logger
logger = logging.getLogger(__name__)

def validate_pr_number(pr):
    """Validate PR number is a positive integer"""
    if pr <= 0:
        raise click.BadParameter("PR number must be a positive integer")
    if pr > 999999:  # Reasonable upper limit
        raise click.BadParameter("PR number seems too large")
    return pr

def validate_repo_format(repo):
    """Validate repository format (owner/repo)"""
    if not repo:
        raise click.BadParameter("Repository cannot be empty")
    
    # Check for valid GitHub repo format: owner/repo
    repo_pattern = r'^[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+$'
    if not re.match(repo_pattern, repo):
        raise click.BadParameter(
            "Repository must be in format 'owner/repo' (e.g., 'microsoft/vscode')"
        )
    
    # Check for reasonable length limits
    if len(repo) > 100:
        raise click.BadParameter("Repository name too long")
    
    return repo.strip()

def validate_github_token(token):
    """Validate GitHub token format"""
    if not token:
        raise click.BadParameter("GitHub token cannot be empty")
    
    token = token.strip()
    
    # GitHub tokens are typically 40 characters (classic) or start with ghp_ (new format)
    if len(token) < 20:
        raise click.BadParameter("GitHub token seems too short")
    
    # Check for common patterns
    if token.startswith('ghp_') or token.startswith('github_pat_') or len(token) == 40:
        return token
    else:
        logger.warning("GitHub token format may be invalid")
        return token

def validate_openai_key(api_key):
    """Validate OpenAI API key format"""
    if not api_key:
        raise click.BadParameter("OpenAI API key cannot be empty")
    
    api_key = api_key.strip()
    
    if not api_key.startswith('sk-'):
        raise click.BadParameter("OpenAI API key should start with 'sk-'")
    
    if len(api_key) < 40:
        raise click.BadParameter("OpenAI API key seems too short")
    
    return api_key

def validate_output_path(output_path):
    """Validate output file path"""
    if not output_path:
        raise click.BadParameter("Output path cannot be empty")
    
    # Check if directory exists (create if needed)
    output_dir = os.path.dirname(os.path.abspath(output_path))
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"Created output directory: {output_dir}")
        except OSError as e:
            raise click.BadParameter(f"Cannot create output directory: {e}")
    
    # Check write permissions
    if not os.access(output_dir, os.W_OK):
        raise click.BadParameter(f"No write permission for directory: {output_dir}")
    
    return output_path

def configure_logging(debug):
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
    )

def fetch_pr_data_with_logs(repo, pr_number, token):
    """Fetch PR data with secure logging (no credentials exposed)"""
    base_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    headers = {"Authorization": f"token {token}"}
    
    # Log URL without any sensitive information
    logger.info(f"Fetching PR data for #{pr_number} from repo: {repo}")
    
    try:
        resp = requests.get(base_url, headers=headers, timeout=30)
        logger.info(f"GitHub API responded with status code: {resp.status_code}")
        
        if resp.status_code != 200:
            logger.error(f"GitHub API error: {resp.status_code} - {resp.reason}")
            if resp.status_code == 401:
                raise ValueError("Invalid GitHub token or insufficient permissions")
            elif resp.status_code == 404:
                raise ValueError(f"PR #{pr_number} not found in repository {repo}")
            else:
                raise ValueError(f"GitHub API error: {resp.status_code}")
        
        pr = resp.json()
        diff_url = pr.get("diff_url", "")
        
        if not diff_url:
            logger.warning("No diff URL found in PR data")
            return {
                "number": pr.get("number"),
                "title": pr.get("title"),
                "body": pr.get("body", ""),
                "merged_at": pr.get("merged_at", ""),
                "diff": ""
            }
        
        logger.info("Fetching PR diff content")
        diff_resp = requests.get(diff_url, headers=headers, timeout=60)
        logger.info(f"Diff fetch completed with status: {diff_resp.status_code}")
        
        pr_data = {
            "number": pr.get("number"),
            "title": pr.get("title"),
            "body": pr.get("body", ""),
            "merged_at": pr.get("merged_at", ""),
            "diff": diff_resp.text if diff_resp.status_code == 200 else ""
        }
        
        logger.info(f"Successfully fetched PR data for #{pr_number}")
        return pr_data
        
    except requests.RequestException as e:
        logger.error(f"Network error while fetching PR data: {e}")
        raise ValueError(f"Failed to fetch PR data: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

def analyze_code_diff_by_file(code_diff):
    logger.info("Analyzing code diff line by line...")
    file_diffs = defaultdict(list)
    current_file = None
    for line in code_diff.splitlines():
        if line.startswith("diff --git"):
            parts = line.split(" b/")
            if len(parts) > 1:
                current_file = parts[-1]
        elif current_file and line.startswith('+') and not line.startswith('+++'):
            file_diffs[current_file].append(line[1:])
    
    issues = {}
    for file, lines in file_diffs.items():
        file_issues = []
        for idx, line in enumerate(lines):
            if len(line) > 120:
                file_issues.append(f"Line {idx+1} is too long (>120 chars).")
            if "eval(" in line:
                file_issues.append(f"Line {idx+1} uses `eval()` which can be unsafe.")
            if "print(" in line:
                file_issues.append(f"Line {idx+1} has `print()`. Consider using logging.")
        if file_issues:
            issues[file] = file_issues
    return issues

@click.group()
@click.option('--debug', is_flag=True, default=False, help='Enable debug logging')
@click.option('--language', type=str, help='Interface language (e.g., en, es, fr, de)')
@click.pass_context
def main(ctx, debug, language):
    """🚀 CodeSnip - AI-powered pre-merge analysis for better code reviews
    
    \b
    Quick Start:
      1. First time? Run: prcodesnip setup
      2. Analyze a PR: prcodesnip predict-risk --pr 123 --repo owner/repo
      3. Full analysis: prcodesnip premerge-analyze --pr 123
    
    \b
    Examples:
      prcodesnip setup                                 # Interactive setup wizard
      prcodesnip predict-risk --pr 4 --repo user/repo # Risk analysis only  
      prcodesnip draft-release --pr 4                 # Draft release notes
      prcodesnip premerge-analyze --pr 4 --post-comment # Full analysis + GitHub comment
      prcodesnip language detect-languages --repo user/repo # Multi-language analysis
    
    \b
    Multi-language Support:
      prcodesnip language set-language es             # Set Spanish interface
      prcodesnip language detect-languages            # Detect repo languages
      prcodesnip language setup-environment python    # Setup Python environment
    
    \b
    Need help? Visit: https://github.com/your-repo/prcodesnip
    """
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug
    configure_logging(debug)
    
    # Set language if provided
    if language:
        if i18n.set_language(language):
            lang_info = i18n.get_language_info(language)
            click.echo(f"🌐 Language set to {lang_info['flag']} {lang_info['name']}")
        else:
            click.echo(f"⚠️ Language '{language}' not supported. Using English.")
    
    # Load user's preferred language from config
    try:
        config = get_config()
        user_lang = config.get_user_preference('language')
        if user_lang and not language:  # Don't override command-line language
            i18n.set_language(user_lang)
    except Exception:
        pass  # Continue with default language if config fails
    
    if debug:
        logger.debug("Debug logging enabled")
    
    # Check for first-time usage
    config = get_config()
    if not config.config_file and not any(os.getenv(var) for var in ['GITHUB_TOKEN', 'GH_TOKEN']):
        if ctx.invoked_subcommand not in ['setup', 'config', '--help', 'help']:
            click.echo("👋 Welcome to CodeSnip! It looks like this is your first time.")
            click.echo("💡 Run 'prcodesnip setup' to get started with interactive configuration.")
            click.echo()

@main.command()
@click.option('--pr', required=True, type=int, help='Pull Request number')
@click.option('--repo', type=str, help='GitHub repository (e.g. user/repo)')
@click.option('--token', type=str, help='GitHub token (or set GITHUB_TOKEN env var)')
@click.option('--openai-key', type=str, help='OpenAI API key (or set OPENAI_API_KEY env var)')
@click.option('--output', default='release-notes.md', help='Output file for release notes')
@click.pass_context
def analyze(ctx, pr, repo, token, openai_key, output):
    debug = ctx.obj['DEBUG']
    config = get_config()
    
    try:
        # Validate PR number
        pr = validate_pr_number(pr)
        
        # Get configuration values with priority: CLI > env > config file
        github_token = config.get_github_token(token)
        openai_api_key = config.get_openai_key(openai_key)
        repository = config.get_default_repo(repo)
        
        # Validate required parameters
        if not github_token:
            raise click.ClickException(
                "GitHub token required. Provide via --token, GITHUB_TOKEN env var, or config file."
            )
        if not openai_api_key:
            raise click.ClickException(
                "OpenAI API key required. Provide via --openai-key, OPENAI_API_KEY env var, or config file."
            )
        if not repository:
            raise click.ClickException(
                "Repository required. Provide via --repo or set default_repo in config file."
            )
        
        # Validate inputs
        repository = validate_repo_format(repository)
        github_token = validate_github_token(github_token)
        openai_api_key = validate_openai_key(openai_api_key)
        output = validate_output_path(output)
        
        logger.info(f"Starting analysis for PR #{pr} in repo {repository}")
        pr_data = fetch_pr_data_with_logs(repository, pr, github_token)
        
    except click.BadParameter as e:
        click.echo(f"Error: {e.message}", err=True)
        ctx.exit(1)
    except (click.ClickException, Exception) as e:
        logger.error(f"Analysis failed: {e}")
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)
    code_diff = pr_data.get("diff", "")

    if not code_diff:
        logger.error("No code diff found in PR data. Aborting analysis.")
        click.echo("No code diff found in PR data.")
        return

    logger.info("Running quality checks...")
    checks = run_all_checks()

    logger.info("Checking memory usage before tests")
    mem_before = psutil.virtual_memory()

    try:
        logger.info("Running memory leak detection (valgrind)...")
        mem_leak_output = subprocess.run(
            "valgrind --leak-check=full python -m pytest",
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        checks['memory_leaks'] = mem_leak_output.stdout + mem_leak_output.stderr
        logger.info("Memory leak check completed")
    except subprocess.TimeoutExpired:
        checks['memory_leaks'] = "Memory leak check timed out."
        logger.error("Memory leak check timed out.")
    except Exception as e:
        checks['memory_leaks'] = f"Memory leak check failed: {str(e)}"
        logger.error(f"Memory leak check failed: {str(e)}")

    logger.info("Checking memory usage after tests")
    mem_after = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=1)
    logger.info(f"CPU usage during analysis: {cpu_percent}%")

    logger.info("Analyzing code diff...")
    code_issues = analyze_code_diff_by_file(code_diff)

    system_metrics = {
        "cpu_usage_percent": cpu_percent,
        "memory_before": mem_before.percent,
        "memory_after": mem_after.percent,
    }

    logger.info("Generating release notes with AI model")
    notes = generate_release_notes(
        pr_data,
        checks,
        openai_api_key,
        code_diff,
        code_issues,
        system_metrics,
        debug=debug
    )

    with open(output, 'w') as f:
        f.write(notes)
    logger.info(f"Release notes written to {output}")
    click.echo(f'Release notes written to {output}')

@main.command()
@click.option('--pr', required=True, type=int, help='Pull Request number')
@click.option('--repo', type=str, help='GitHub repository (e.g. user/repo)')
@click.option('--token', type=str, help='GitHub token (or set GITHUB_TOKEN env var)')
@click.pass_context
def fetch(ctx, pr, repo, token):
    debug = ctx.obj['DEBUG']
    config = get_config()
    
    try:
        # Validate PR number
        pr = validate_pr_number(pr)
        
        # Get configuration values
        github_token = config.get_github_token(token)
        repository = config.get_default_repo(repo)
        
        # Validate required parameters
        if not github_token:
            raise click.ClickException(
                "GitHub token required. Provide via --token, GITHUB_TOKEN env var, or config file."
            )
        if not repository:
            raise click.ClickException(
                "Repository required. Provide via --repo or set default_repo in config file."
            )
        
        # Validate inputs
        repository = validate_repo_format(repository)
        github_token = validate_github_token(github_token)
        
        logger.info(f"Fetching data for PR #{pr} in repo {repository}")
        pr_data = fetch_pr_data_with_logs(repository, pr, github_token)
        
        click.echo(pr_data)
        logger.info(f"Successfully fetched PR data for #{pr}")
        click.echo(f"Fetched PR data for #{pr} in {repository}")
        
    except click.BadParameter as e:
        click.echo(f"Error: {e.message}", err=True)
        ctx.exit(1)
    except (click.ClickException, Exception) as e:
        logger.error(f"Fetch failed: {e}")
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)

@main.command()
@click.option('--pr', required=True, type=int, help='Pull Request number')
@click.option('--repo', type=str, help='GitHub repository (e.g. user/repo)')
@click.option('--token', type=str, help='GitHub token (or set GITHUB_TOKEN env var)')
@click.option('--openai-key', type=str, help='OpenAI API key (or set OPENAI_API_KEY env var)')
@click.option('--output', default='release-notes.md', help='Output file for release notes')
@click.pass_context
def analyze_fast(ctx, pr, repo, token, openai_key, output):
    """Fast async analysis with parallel processing"""
    debug = ctx.obj['DEBUG']
    config = get_config()
    
    try:
        # Validate PR number
        pr = validate_pr_number(pr)
        
        # Get configuration values with priority: CLI > env > config file
        github_token = config.get_github_token(token)
        openai_api_key = config.get_openai_key(openai_key)
        repository = config.get_default_repo(repo)
        
        # Validate required parameters
        if not github_token:
            raise click.ClickException(
                "GitHub token required. Provide via --token, GITHUB_TOKEN env var, or config file."
            )
        if not openai_api_key:
            raise click.ClickException(
                "OpenAI API key required. Provide via --openai-key, OPENAI_API_KEY env var, or config file."
            )
        if not repository:
            raise click.ClickException(
                "Repository required. Provide via --repo or set default_repo in config file."
            )
        
        # Validate inputs
        repository = validate_repo_format(repository)
        github_token = validate_github_token(github_token)
        openai_api_key = validate_openai_key(openai_api_key)
        output = validate_output_path(output)
        
        logger.info(f"Starting fast analysis for PR #{pr} in repo {repository}")
        
        # Run async analysis
        async def run_analysis():
            return await analyze_pr_async(repository, pr, github_token)
        
        # Execute async analysis
        analysis_result = asyncio.run(run_analysis())
        pr_data = analysis_result["pr_data"]
        checks = analysis_result["quality_checks"]
        
        if not pr_data.get("diff"):
            logger.error("No code diff found in PR data. Aborting analysis.")
            click.echo("No code diff found in PR data.")
            ctx.exit(1)
        
        # Analyze code diff
        code_diff = pr_data.get("diff", "")
        code_issues = analyze_code_diff_by_file(code_diff)
        
        # System metrics (simplified for fast mode)
        system_metrics = {
            "cpu_usage_percent": psutil.cpu_percent(interval=0.1),
            "memory_usage": psutil.virtual_memory().percent,
            "analysis_mode": "fast_async"
        }
        
        logger.info("Generating release notes with AI model")
        notes = generate_release_notes(
            pr_data,
            checks,
            openai_api_key,
            code_diff,
            code_issues,
            system_metrics,
            debug=debug
        )
        
        with open(output, 'w') as f:
            f.write(notes)
        logger.info(f"Release notes written to {output}")
        click.echo(f'Fast analysis complete! Release notes written to {output}')
        
    except click.BadParameter as e:
        click.echo(f"Error: {e.message}", err=True)
        ctx.exit(1)
    except (click.ClickException, Exception) as e:
        logger.error(f"Fast analysis failed: {e}")
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)

@main.command()
@click.option('--pr', type=int, help='Pull Request number (will prompt if not provided)')
@click.option('--repo', type=str, help='GitHub repository (e.g. user/repo)')
@click.option('--token', type=str, help='GitHub token (or set GITHUB_TOKEN env var)')
@click.option('--commit-sha', type=str, help='Commit SHA for status checks')
@click.option('--post-comment', is_flag=True, help='Post results as PR comment')
@click.option('--create-status', is_flag=True, help='Create GitHub status check')
@click.option('--output', default='premerge-analysis.json', help='Output file for analysis results')
@click.pass_context
def premerge_analyze(ctx, pr, repo, token, commit_sha, post_comment, create_status, output):
    """🚀 Pre-merge analysis with risk prediction and draft release notes"""
    debug = ctx.obj['DEBUG']
    config = get_config()
    
    try:
        # Validate and get configuration
        github_token = config.get_github_token(token)
        
        if not github_token:
            raise click.ClickException("GitHub token required. Run 'prcodesnip setup' to configure.")
        
        github_token = validate_github_token(github_token)
        
        # Interactive prompts for missing parameters
        if not repo or not pr:
            repository, pr_number = get_repository_and_pr_interactive(
                github_token=github_token,
                provided_repo=repo,
                provided_pr=pr,
                default_repo=config.get_default_repo()
            )
        else:
            repository = config.get_default_repo(repo)
            pr_number = pr
        
        if not repository:
            raise click.ClickException("Repository required.")
        
        pr_number = validate_pr_number(pr_number)
        repository = validate_repo_format(repository)
        output = validate_output_path(output)
        
        logger.info(f"🚀 Starting pre-merge analysis for PR #{pr_number} in repo {repository}")
        
        # Fetch PR data
        pr_data = fetch_pr_data_with_logs(repository, pr_number, github_token)
        
        if not pr_data.get("diff"):
            logger.error("No code diff found in PR data. Aborting analysis.")
            click.echo("❌ No code diff found in PR data.")
            ctx.exit(1)
        
        # Initialize analysis engines
        draft_generator = DraftReleaseNotesGenerator()
        risk_predictor = EarlyRiskPredictor()
        
        # Generate draft release notes
        logger.info("📝 Generating draft release notes...")
        code_analysis = {"diff": pr_data.get("diff", "")}  # Basic analysis
        draft_notes = draft_generator.generate_draft_notes(pr_data, code_analysis)
        
        # Predict risks
        logger.info("🎯 Predicting risks...")
        risk_score = risk_predictor.predict_risks(pr_data, code_analysis)
        risk_report = risk_predictor.generate_risk_report(risk_score, pr_data)
        
        # Create workflow status
        status_manager = WorkflowStatusManager()
        workflow_status = status_manager.create_workflow_status(
            risk_score.risk_level, 
            risk_score.overall_risk, 
            pr
        )
        
        # Combine results
        analysis_result = {
            "timestamp": datetime.now().isoformat(),
            "pr_data": {
                "number": pr_data.get("number"),
                "title": pr_data.get("title"),
                "repository": repository
            },
            "risk_analysis": risk_report,
            "draft_release_notes": draft_notes,
            "workflow_status": workflow_status
        }
        
        # Save results to file
        with open(output, 'w') as f:
            json.dump(analysis_result, f, indent=2)
        logger.info(f"📄 Analysis results saved to {output}")
        
        # Display results
        click.echo(f"\n{workflow_status['symbol']} Pre-Merge Analysis Results")
        click.echo(f"{'=' * 50}")
        click.echo(f"PR #{pr}: {pr_data.get('title', '')}")
        click.echo(f"Repository: {repository}")
        click.echo(f"Risk Level: {risk_score.risk_symbol} {risk_score.risk_level.title()}")
        click.echo(f"Overall Risk Score: {risk_score.overall_risk:.2f}/1.0")
        click.echo(f"Confidence: {risk_score.confidence:.2f}")
        
        if draft_notes.get('version'):
            click.echo(f"Suggested Version Bump: {draft_notes['version']}")
        
        # Post to GitHub if requested
        if post_comment or create_status:
            github_integration = GitHubWorkflowIntegration(github_token)
            
            if post_comment:
                success = github_integration.post_risk_comment(repository, pr, risk_report, draft_notes)
                if success:
                    click.echo("💬 Posted analysis comment to PR")
                else:
                    click.echo("❌ Failed to post comment", err=True)
            
            if create_status and commit_sha:
                success = github_integration.create_status_check(repository, commit_sha, risk_report)
                if success:
                    click.echo("✅ Created GitHub status check")
                else:
                    click.echo("❌ Failed to create status check", err=True)
            elif create_status and not commit_sha:
                click.echo("⚠️ Commit SHA required for status checks", err=True)
        
        # Exit with appropriate code based on risk level
        if risk_score.risk_level == "high":
            click.echo(f"\n🚨 HIGH RISK DETECTED - Review required before merge")
            ctx.exit(1)
        elif risk_score.risk_level == "moderate":
            click.echo(f"\n⚠️ MODERATE RISK - Proceed with caution")
            ctx.exit(0)
        else:
            click.echo(f"\n✅ LOW RISK - Safe to merge")
            ctx.exit(0)
        
    except click.BadParameter as e:
        click.echo(f"Error: {e.message}", err=True)
        ctx.exit(1)
    except (click.ClickException, Exception) as e:
        logger.error(f"Pre-merge analysis failed: {e}")
        click.echo(f"❌ Error: {e}", err=True)
        ctx.exit(1)

@main.command()
@click.option('--pr', type=int, help='Pull Request number (will prompt if not provided)')
@click.option('--repo', type=str, help='GitHub repository (e.g. user/repo)')
@click.option('--token', type=str, help='GitHub token (or set GITHUB_TOKEN env var)')
@click.option('--format', default='markdown', type=click.Choice(['markdown', 'json', 'text']), help='Output format')
@click.option('--output', help='Output file (default: stdout)')
@click.pass_context
def draft_release(ctx, pr, repo, token, format, output):
    """📝 Generate draft release notes for PR before merge"""
    debug = ctx.obj['DEBUG']
    config = get_config()
    
    try:
        # Validate and get configuration
        github_token = config.get_github_token(token)
        
        if not github_token:
            raise click.ClickException("GitHub token required. Run 'prcodesnip setup' to configure.")
        
        github_token = validate_github_token(github_token)
        
        # Interactive prompts for missing parameters
        if not repo or not pr:
            repository, pr_number = get_repository_and_pr_interactive(
                github_token=github_token,
                provided_repo=repo,
                provided_pr=pr,
                default_repo=config.get_default_repo()
            )
        else:
            repository = config.get_default_repo(repo)
            pr_number = pr
        
        if not repository:
            raise click.ClickException("Repository required.")
        
        pr_number = validate_pr_number(pr_number)
        repository = validate_repo_format(repository)
        
        logger.info(f"📝 Generating draft release notes for PR #{pr_number}")
        
        # Fetch PR data
        pr_data = fetch_pr_data_with_logs(repository, pr_number, github_token)
        
        # Generate draft notes
        draft_generator = DraftReleaseNotesGenerator()
        code_analysis = {"diff": pr_data.get("diff", "")}
        draft_notes = draft_generator.generate_draft_notes(pr_data, code_analysis)
        
        # Format output
        if format == 'json':
            content = json.dumps(draft_notes, indent=2)
        elif format == 'text':
            content = f"Version: {draft_notes.get('version', 'patch')}\n"
            content += f"Confidence: {draft_notes.get('confidence_score', 0):.2f}\n\n"
            content += draft_notes.get('release_notes', '')
        else:  # markdown (default)
            content = draft_notes.get('release_notes', '')
        
        # Output results
        if output:
            output = validate_output_path(output)
            with open(output, 'w') as f:
                f.write(content)
            click.echo(f"📄 Draft release notes written to {output}")
        else:
            click.echo(content)
        
    except click.BadParameter as e:
        click.echo(f"Error: {e.message}", err=True)
        ctx.exit(1)
    except (click.ClickException, Exception) as e:
        logger.error(f"Draft release generation failed: {e}")
        click.echo(f"❌ Error: {e}", err=True)
        ctx.exit(1)

@main.command()
@click.option('--pr', type=int, help='Pull Request number (will prompt if not provided)')
@click.option('--repo', type=str, help='GitHub repository (e.g. user/repo)')
@click.option('--token', type=str, help='GitHub token (or set GITHUB_TOKEN env var)')
@click.option('--detailed', is_flag=True, help='Show detailed risk breakdown')
@click.pass_context
def predict_risk(ctx, pr, repo, token, detailed):
    """🎯 Predict risks for PR before merge"""
    debug = ctx.obj['DEBUG']
    config = get_config()
    
    try:
        # Validate and get configuration  
        github_token = config.get_github_token(token)
        
        if not github_token:
            raise click.ClickException("GitHub token required. Run 'prcodesnip setup' to configure.")
        
        github_token = validate_github_token(github_token)
        
        # Interactive prompts for missing parameters
        if not repo or not pr:
            repository, pr_number = get_repository_and_pr_interactive(
                github_token=github_token,
                provided_repo=repo,
                provided_pr=pr,
                default_repo=config.get_default_repo()
            )
        else:
            repository = config.get_default_repo(repo)
            pr_number = pr
        
        if not repository:
            raise click.ClickException("Repository required.")
        
        pr_number = validate_pr_number(pr_number)
        repository = validate_repo_format(repository)
        
        logger.info(f"🎯 Predicting risks for PR #{pr_number}")
        
        # Fetch PR data
        pr_data = fetch_pr_data_with_logs(repository, pr_number, github_token)
        
        # Predict risks
        risk_predictor = EarlyRiskPredictor()
        code_analysis = {"diff": pr_data.get("diff", "")}
        risk_score = risk_predictor.predict_risks(pr_data, code_analysis)
        
        # Display results
        click.echo(f"\n{risk_score.risk_symbol} Risk Prediction Results")
        click.echo(f"{'=' * 40}")
        click.echo(f"Overall Risk: {risk_score.risk_symbol} {risk_score.risk_level.title()} ({risk_score.overall_risk:.2f}/1.0)")
        click.echo(f"Confidence: {risk_score.confidence:.2f}")
        
        if detailed:
            click.echo(f"\n📊 Detailed Risk Breakdown:")
            click.echo(f"  🐛 Bug Probability: {risk_score.bug_probability:.2f}")
            click.echo(f"  🔒 Security Risk: {risk_score.security_risk:.2f}")
            click.echo(f"  ⚡ Performance Risk: {risk_score.performance_risk:.2f}")
            click.echo(f"  🧩 Complexity Risk: {risk_score.complexity_risk:.2f}")
        
        # Generate and show recommendations
        risk_report = risk_predictor.generate_risk_report(risk_score, pr_data)
        recommendations = risk_report.get("recommendations", [])
        
        if recommendations:
            click.echo(f"\n💡 Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                click.echo(f"  {i}. {rec}")
        
    except click.BadParameter as e:
        click.echo(f"Error: {e.message}", err=True)
        ctx.exit(1)  
    except (click.ClickException, Exception) as e:
        logger.error(f"Risk prediction failed: {e}")
        click.echo(f"❌ Error: {e}", err=True)
        ctx.exit(1)

@main.command()
@click.pass_context
def quickstart(ctx):
    """🏃 Quick start guide for new users"""
    click.echo("🚀 CodeSnip Quick Start Guide")
    click.echo("=" * 30)
    
    click.echo("\n1️⃣ First-Time Setup:")
    click.echo("   prcodesnip setup                    # Interactive configuration")
    
    click.echo("\n2️⃣ Basic Usage:")
    click.echo("   prcodesnip predict-risk --pr 123   # Analyze PR risks")
    click.echo("   prcodesnip draft-release --pr 123  # Generate release notes")
    
    click.echo("\n3️⃣ Full Analysis:")
    click.echo("   prcodesnip premerge-analyze --pr 123 # Complete analysis")
    
    click.echo("\n4️⃣ GitHub Integration:")
    click.echo("   prcodesnip setup-workflow           # Add to GitHub Actions")
    
    click.echo("\n5️⃣ Configuration:")
    click.echo("   prcodesnip config --show            # View current settings")
    click.echo("   prcodesnip config --test            # Test credentials")
    
    click.echo("\n💡 Tips:")
    click.echo("   • Set GITHUB_TOKEN environment variable for convenience")
    click.echo("   • Add OPENAI_API_KEY for AI-powered release notes")
    click.echo("   • Use --debug flag to see detailed logs")
    
    click.echo("\n🆘 Need help? Try:")
    click.echo("   prcodesnip <command> --help")

@main.command()
@click.pass_context 
def setup(ctx):
    """🚀 Interactive setup wizard for first-time users"""
    try:
        success = run_setup_wizard()
        if success:
            click.echo("\n🎉 You're all set! Try running:")
            click.echo("  codesnip predict-risk --pr <number> --repo <owner/repo>")
            click.echo("\nOr run the full analysis:")
            click.echo("  codesnip premerge-analyze --pr <number>")
        else:
            click.echo("\n💡 You can run 'codesnip setup' again anytime.")
            ctx.exit(1)
    except Exception as e:
        logger.error(f"Setup wizard failed: {e}")
        click.echo(f"❌ Setup failed: {e}", err=True)
        ctx.exit(1)

@main.command()
@click.option('--create', is_flag=True, help='Create a sample configuration file')
@click.option('--show', is_flag=True, help='Show current configuration') 
@click.option('--test', is_flag=True, help='Test current configuration')
@click.option('--reset', is_flag=True, help='Reset configuration (run setup again)')
@click.pass_context
def config(ctx, create, show, test, reset):
    """Manage configuration settings"""
    config = get_config()
    
    if reset:
        if click.confirm("This will reset your configuration. Continue?"):
            success = run_setup_wizard()
            if not success:
                ctx.exit(1)
        return
    
    if create:
        config_path = config.create_sample_config()
        if config_path:
            click.echo(f"✅ Created sample configuration file: {config_path}")
            click.echo("\n💡 Next steps:")
            click.echo("1. Run 'prcodesnip setup' for interactive configuration")
            click.echo("2. Or manually edit the config file")
            click.echo("3. Set environment variables:")
            click.echo("   export GITHUB_TOKEN='your_token_here'")
            click.echo("   export OPENAI_API_KEY='your_key_here'")
        else:
            click.echo("❌ Failed to create configuration file", err=True)
            ctx.exit(1)
    
    elif show:
        click.echo("📋 Current Configuration")
        click.echo("=" * 25)
        click.echo(f"Config file: {config.config_file or '❌ Not found'}")
        
        # Show masked tokens for security
        github_token = config.get_github_token()
        if github_token:
            masked_token = github_token[:8] + '*' * max(0, len(github_token) - 8)
            click.echo(f"GitHub token: ✅ {masked_token}")
        else:
            click.echo("GitHub token: ❌ Not configured")
        
        openai_key = config.get_openai_key()
        if openai_key:
            masked_key = openai_key[:8] + '*' * max(0, len(openai_key) - 8)
            click.echo(f"OpenAI key: ✅ {masked_key}")
        else:
            click.echo("OpenAI key: ⚠️ Not configured (optional)")
        
        default_repo = config.get_default_repo()
        if default_repo:
            click.echo(f"Default repo: ✅ {default_repo}")
        else:
            click.echo("Default repo: ⚠️ Not configured")
        
        # Show status
        if not github_token:
            click.echo("\n💡 Run 'prcodesnip setup' to configure credentials interactively")
    
    elif test:
        click.echo("🧪 Testing Configuration")
        click.echo("-" * 22)
        
        # Test GitHub token
        github_token = config.get_github_token()
        if github_token:
            try:
                import requests
                headers = {'Authorization': f'token {github_token}', 'User-Agent': 'CodeSnip-CLI'}
                response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
                if response.status_code == 200:
                    user_data = response.json()
                    click.echo(f"✅ GitHub token: Connected as {user_data.get('login', 'unknown')}")
                else:
                    click.echo("❌ GitHub token: Invalid or expired")
            except Exception as e:
                click.echo(f"❌ GitHub token: Test failed - {e}")
        else:
            click.echo("❌ GitHub token: Not configured")
        
        # Test OpenAI key (without making actual API call to avoid charges)
        openai_key = config.get_openai_key()
        if openai_key:
            if openai_key.startswith('sk-') and len(openai_key) > 40:
                click.echo("✅ OpenAI key: Format looks correct")
            else:
                click.echo("⚠️ OpenAI key: Format may be incorrect")
        else:
            click.echo("⚠️ OpenAI key: Not configured (optional)")
        
        # Test default repo
        default_repo = config.get_default_repo()
        if default_repo:
            if config.get_github_token():
                try:
                    headers = {'Authorization': f'token {github_token}', 'User-Agent': 'CodeSnip-CLI'}
                    response = requests.get(f'https://api.github.com/repos/{default_repo}', headers=headers, timeout=10)
                    if response.status_code == 200:
                        click.echo(f"✅ Default repo: {default_repo} is accessible")
                    else:
                        click.echo(f"❌ Default repo: {default_repo} not accessible")
                except Exception as e:
                    click.echo(f"❌ Default repo: Test failed - {e}")
            else:
                click.echo(f"⚠️ Default repo: {default_repo} (cannot test without GitHub token)")
        else:
            click.echo("ℹ️ Default repo: Not configured (will prompt per command)")
    
    else:
        click.echo("💡 Configuration Help")
        click.echo("=" * 20)
        click.echo("Available options:")
        click.echo("  --create   Create a sample configuration file")
        click.echo("  --show     Show current configuration") 
        click.echo("  --test     Test current configuration")
        click.echo("  --reset    Reset configuration (interactive setup)")
        click.echo("\n🚀 For first-time setup, run: prcodesnip setup")

@main.command()
@click.option('--provider', default='github-actions', type=click.Choice(['github-actions', 'gitlab-ci', 'jenkins']), help='CI/CD provider')
@click.option('--output-dir', default='.github/workflows', help='Output directory for workflow files')
@click.pass_context
def setup_workflow(ctx, provider, output_dir):
    """🔄 Setup CI/CD workflow integration"""
    try:
        if provider == 'github-actions':
            # Create .github/workflows directory
            workflow_dir = Path(output_dir)
            workflow_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy workflow template
            template_path = Path(__file__).parent / 'templates' / 'github-workflow.yml'
            workflow_path = workflow_dir / 'prcodesnip-premerge.yml'
            
            if template_path.exists():
                import shutil
                shutil.copy2(template_path, workflow_path)
                click.echo(f"✅ Created GitHub Actions workflow: {workflow_path}")
            else:
                # Create workflow content directly
                workflow_content = """name: CodeSnip Pre-Merge Analysis
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  premerge-analysis:
    runs-on: ubuntu-latest
    name: 🚀 Pre-Merge Analysis
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install CodeSnip
        run: |
          pip install -e .
          
      - name: Run Pre-Merge Analysis
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          prcodesnip premerge-analyze \\
            --pr ${{ github.event.number }} \\
            --repo ${{ github.repository }} \\
            --commit-sha ${{ github.event.pull_request.head.sha }} \\
            --post-comment \\
            --create-status"""
                
                with open(workflow_path, 'w') as f:
                    f.write(workflow_content)
                click.echo(f"✅ Created GitHub Actions workflow: {workflow_path}")
            
            click.echo("\n📋 Setup Instructions:")
            click.echo("1. Add OPENAI_API_KEY to your GitHub repository secrets")
            click.echo("2. Ensure GITHUB_TOKEN has write permissions for status checks")
            click.echo("3. Commit and push the workflow file")
            click.echo("4. Create a test PR to see the analysis in action!")
            
        elif provider == 'gitlab-ci':
            click.echo("🚧 GitLab CI integration coming soon!")
        elif provider == 'jenkins':
            click.echo("🚧 Jenkins integration coming soon!")
            
    except Exception as e:
        logger.error(f"Workflow setup failed: {e}")
        click.echo(f"❌ Error: {e}", err=True)
        ctx.exit(1)

# Add language commands to main CLI
main.add_command(language_commands, name='language')

if __name__ == '__main__':
    main()
