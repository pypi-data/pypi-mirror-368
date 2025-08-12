import subprocess
import shlex
import logging

logger = logging.getLogger(__name__)

def run_command_safe(command_list):
    """Safely run command without shell injection vulnerability"""
    try:
        if isinstance(command_list, str):
            command_list = shlex.split(command_list)
        
        logger.debug(f"Running command: {' '.join(command_list)}")
        result = subprocess.run(
            command_list, 
            capture_output=True, 
            text=True, 
            timeout=300,
            check=False
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out: {' '.join(command_list)}")
        return "Command timed out after 300 seconds"
    except FileNotFoundError:
        logger.error(f"Command not found: {command_list[0]}")
        return f"Error: {command_list[0]} command not found"
    except Exception as e:
        logger.error(f"Command failed: {e}")
        return f"Error: {str(e)}"

def run_all_checks():
    """Run all quality checks with safe command execution"""
    checks = {}
    
    # Define safe command lists
    commands = {
        "pytest": ["pytest", "--tb=short"],
        "coverage": ["coverage", "run", "-m", "pytest"],
        "coverage_report": ["coverage", "report", "--show-missing"],
        "pylint": ["pylint", "codesnip", "--output-format=text"],
        "bandit": ["bandit", "-r", "codesnip", "-f", "txt"]
    }
    
    # Run pytest
    checks["pytest"] = run_command_safe(commands["pytest"])
    
    # Run coverage (two-step process)
    run_command_safe(commands["coverage"])  # Generate coverage data
    checks["coverage"] = run_command_safe(commands["coverage_report"])
    
    # Run pylint
    checks["pylint"] = run_command_safe(commands["pylint"])
    
    # Run bandit security check
    checks["bandit"] = run_command_safe(commands["bandit"])
    
    return checks
