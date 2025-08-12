import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class AsyncGitHubClient:
    """Async GitHub API client for better performance"""
    
    def __init__(self, token: str, timeout: int = 30):
        self.token = token
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "codesnip-cli"
        }
    
    async def fetch_pr_data_async(self, repo: str, pr_number: int) -> Dict[str, Any]:
        """Fetch PR data asynchronously"""
        base_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
        
        async with aiohttp.ClientSession(
            timeout=self.timeout,
            headers=self.headers
        ) as session:
            try:
                logger.info(f"Fetching PR data for #{pr_number} from repo: {repo}")
                
                # Fetch PR metadata and diff content concurrently
                pr_task = self._fetch_pr_metadata(session, base_url)
                
                pr_data = await pr_task
                
                if not pr_data:
                    return {}
                
                diff_url = pr_data.get("diff_url", "")
                if diff_url:
                    diff_task = self._fetch_diff_content(session, diff_url)
                    diff_content = await diff_task
                    pr_data["diff"] = diff_content
                else:
                    pr_data["diff"] = ""
                
                logger.info(f"Successfully fetched PR data for #{pr_number}")
                return {
                    "number": pr_data.get("number"),
                    "title": pr_data.get("title"),
                    "body": pr_data.get("body", ""),
                    "merged_at": pr_data.get("merged_at", ""),
                    "diff": pr_data.get("diff", ""),
                    "files_changed": pr_data.get("changed_files", 0),
                    "additions": pr_data.get("additions", 0),
                    "deletions": pr_data.get("deletions", 0)
                }
                
            except Exception as e:
                logger.error(f"Failed to fetch PR data: {e}")
                raise
    
    async def _fetch_pr_metadata(self, session: aiohttp.ClientSession, url: str) -> Optional[Dict]:
        """Fetch PR metadata"""
        try:
            async with session.get(url) as response:
                logger.info(f"GitHub API responded with status: {response.status}")
                
                if response.status == 401:
                    raise ValueError("Invalid GitHub token or insufficient permissions")
                elif response.status == 404:
                    raise ValueError("PR not found or repository not accessible")
                elif response.status != 200:
                    raise ValueError(f"GitHub API error: {response.status}")
                
                return await response.json()
                
        except aiohttp.ClientError as e:
            logger.error(f"Network error fetching PR metadata: {e}")
            raise ValueError(f"Network error: {e}")
    
    async def _fetch_diff_content(self, session: aiohttp.ClientSession, diff_url: str) -> str:
        """Fetch diff content"""
        try:
            logger.info("Fetching PR diff content")
            async with session.get(diff_url) as response:
                logger.info(f"Diff fetch completed with status: {response.status}")
                
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"Failed to fetch diff: {response.status}")
                    return ""
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error fetching diff: {e}")
            return ""

class AsyncQualityChecker:
    """Async quality checker for parallel execution"""
    
    def __init__(self, timeout: int = 300):
        self.timeout = timeout
    
    async def run_checks_async(self) -> Dict[str, str]:
        """Run quality checks in parallel"""
        logger.info("Starting parallel quality checks")
        
        # Define check tasks
        tasks = [
            self._run_pytest(),
            self._run_coverage(),
            self._run_pylint(), 
            self._run_bandit()
        ]
        
        # Run all checks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        checks = {}
        check_names = ["pytest", "coverage", "pylint", "bandit"]
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"{check_names[i]} check failed: {result}")
                checks[check_names[i]] = f"Error: {str(result)}"
            else:
                checks[check_names[i]] = result
        
        logger.info("Completed parallel quality checks")
        return checks
    
    async def _run_pytest(self) -> str:
        """Run pytest asynchronously"""
        return await self._run_command(["pytest", "--tb=short"])
    
    async def _run_coverage(self) -> str:
        """Run coverage analysis asynchronously"""
        # First generate coverage data
        await self._run_command(["coverage", "run", "-m", "pytest"])
        # Then get coverage report
        return await self._run_command(["coverage", "report", "--show-missing"])
    
    async def _run_pylint(self) -> str:
        """Run pylint asynchronously"""
        return await self._run_command(["pylint", "codesnip", "--output-format=text"])
    
    async def _run_bandit(self) -> str:
        """Run bandit security check asynchronously"""
        return await self._run_command(["bandit", "-r", "codesnip", "-f", "txt"])
    
    async def _run_command(self, command_list) -> str:
        """Run command asynchronously"""
        try:
            logger.debug(f"Running async command: {' '.join(command_list)}")
            
            process = await asyncio.create_subprocess_exec(
                *command_list,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=self.timeout
            )
            
            return stdout.decode() + stderr.decode()
            
        except asyncio.TimeoutError:
            logger.error(f"Command timed out: {' '.join(command_list)}")
            return f"Command timed out after {self.timeout} seconds"
        except FileNotFoundError:
            logger.error(f"Command not found: {command_list[0]}")
            return f"Error: {command_list[0]} command not found"
        except Exception as e:
            logger.error(f"Command failed: {e}")
            return f"Error: {str(e)}"

async def analyze_pr_async(repo: str, pr_number: int, github_token: str) -> Dict[str, Any]:
    """Main async analysis function"""
    github_client = AsyncGitHubClient(github_token)
    quality_checker = AsyncQualityChecker()
    
    # Run GitHub API fetch and quality checks in parallel
    pr_task = github_client.fetch_pr_data_async(repo, pr_number)
    checks_task = quality_checker.run_checks_async()
    
    pr_data, checks = await asyncio.gather(pr_task, checks_task)
    
    return {
        "pr_data": pr_data,
        "quality_checks": checks
    }