import json
import logging
from typing import Dict, Any, Optional
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

class GitHubWorkflowIntegration:
    """Integration with GitHub workflows and status checks"""
    
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "codesnip-workflow-integration"
        }
        self.base_url = "https://api.github.com"
    
    def create_status_check(self, repo: str, commit_sha: str, risk_report: Dict[str, Any]) -> bool:
        """Create GitHub status check with risk-based visual indicators"""
        try:
            status_data = risk_report.get("status_check", {})
            risk_level = risk_report["risk_assessment"]["risk_level"]
            risk_symbol = risk_report["risk_assessment"]["risk_symbol"]
            overall_score = risk_report["risk_assessment"]["overall_score"]
            
            # Create status check
            status_payload = {
                "state": status_data.get("state", "pending"),
                "target_url": self._generate_report_url(repo, risk_report["pr_number"]),
                "description": f"{risk_symbol} Risk: {risk_level.title()} ({overall_score:.2f}/1.0)",
                "context": "codesnip/risk-analysis"
            }
            
            url = f"{self.base_url}/repos/{repo}/statuses/{commit_sha}"
            response = requests.post(url, headers=self.headers, json=status_payload)
            
            if response.status_code == 201:
                logger.info(f"Created status check: {risk_symbol} {risk_level} risk")
                return True
            else:
                logger.error(f"Failed to create status check: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating status check: {e}")
            return False
    
    def post_risk_comment(self, repo: str, pr_number: int, risk_report: Dict[str, Any], 
                         draft_notes: Dict[str, Any]) -> bool:
        """Post comprehensive risk analysis and draft release notes as PR comment"""
        try:
            comment_body = self._format_risk_comment(risk_report, draft_notes)
            
            url = f"{self.base_url}/repos/{repo}/issues/{pr_number}/comments"
            payload = {"body": comment_body}
            
            response = requests.post(url, headers=self.headers, json=payload)
            
            if response.status_code == 201:
                logger.info(f"Posted risk analysis comment to PR #{pr_number}")
                return True
            else:
                logger.error(f"Failed to post comment: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error posting risk comment: {e}")
            return False
    
    def update_pr_labels(self, repo: str, pr_number: int, risk_level: str) -> bool:
        """Update PR labels based on risk level"""
        try:
            # Risk-based label mapping
            risk_labels = {
                "low": ["✅ low-risk", "ready-for-review"],
                "moderate": ["⚠️ moderate-risk", "needs-attention"],
                "high": ["🚨 high-risk", "requires-careful-review"]
            }
            
            labels = risk_labels.get(risk_level, [])
            
            url = f"{self.base_url}/repos/{repo}/issues/{pr_number}/labels"
            payload = {"labels": labels}
            
            response = requests.post(url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                logger.info(f"Updated PR labels: {labels}")
                return True
            else:
                logger.error(f"Failed to update labels: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating PR labels: {e}")
            return False
    
    def create_check_run(self, repo: str, commit_sha: str, risk_report: Dict[str, Any], 
                        draft_notes: Dict[str, Any]) -> bool:
        """Create detailed check run with risk analysis and draft notes"""
        try:
            risk_level = risk_report["risk_assessment"]["risk_level"]
            risk_symbol = risk_report["risk_assessment"]["risk_symbol"]
            
            # Determine conclusion based on risk level
            conclusion_map = {
                "low": "success",
                "moderate": "neutral", 
                "high": "failure"
            }
            
            check_payload = {
                "name": "CodeSnip Pre-Merge Analysis",
                "head_sha": commit_sha,
                "status": "completed",
                "conclusion": conclusion_map[risk_level],
                "started_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat(),
                "output": {
                    "title": f"{risk_symbol} Risk Assessment: {risk_level.title()}",
                    "summary": self._format_check_summary(risk_report, draft_notes),
                    "text": self._format_detailed_analysis(risk_report, draft_notes)
                }
            }
            
            url = f"{self.base_url}/repos/{repo}/check-runs"
            response = requests.post(url, headers=self.headers, json=check_payload)
            
            if response.status_code == 201:
                logger.info(f"Created check run with {risk_symbol} {risk_level} status")
                return True
            else:
                logger.error(f"Failed to create check run: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating check run: {e}")
            return False
    
    def _format_risk_comment(self, risk_report: Dict[str, Any], draft_notes: Dict[str, Any]) -> str:
        """Format comprehensive risk analysis comment"""
        risk_assessment = risk_report["risk_assessment"]
        detailed_risks = risk_report["detailed_risks"]
        recommendations = risk_report["recommendations"]
        
        comment_parts = []
        
        # Header with risk indicator
        comment_parts.append(f"## {risk_assessment['risk_symbol']} CodeSnip Pre-Merge Analysis")
        comment_parts.append(f"**Risk Level: {risk_assessment['risk_level'].title()}** (Score: {risk_assessment['overall_score']}/1.0)")
        comment_parts.append(f"*Confidence: {risk_assessment['confidence']:.2f}*")
        comment_parts.append("")
        
        # Risk breakdown
        comment_parts.append("### 📊 Risk Breakdown")
        comment_parts.append(f"- 🐛 **Bug Probability:** {detailed_risks['bug_probability']:.2f}")
        comment_parts.append(f"- 🔒 **Security Risk:** {detailed_risks['security_risk']:.2f}")
        comment_parts.append(f"- ⚡ **Performance Risk:** {detailed_risks['performance_risk']:.2f}")
        comment_parts.append(f"- 🧩 **Complexity Risk:** {detailed_risks['complexity_risk']:.2f}")
        comment_parts.append("")
        
        # Recommendations
        if recommendations:
            comment_parts.append("### 💡 Recommendations")
            for rec in recommendations:
                comment_parts.append(f"- {rec}")
            comment_parts.append("")
        
        # Draft Release Notes
        if draft_notes and draft_notes.get("release_notes"):
            comment_parts.append("### 📝 Draft Release Notes")
            comment_parts.append(f"*Suggested version bump: **{draft_notes.get('version', 'patch')}***")
            comment_parts.append("")
            comment_parts.append(draft_notes["release_notes"])
            comment_parts.append("")
        
        # Merge recommendation
        merge_recommendation = self._get_merge_recommendation(risk_assessment["risk_level"])
        comment_parts.append(f"### 🎯 Merge Recommendation")
        comment_parts.append(merge_recommendation)
        comment_parts.append("")
        
        comment_parts.append("---")
        comment_parts.append("*🤖 Generated by CodeSnip Pre-Merge Analysis*")
        
        return "\n".join(comment_parts)
    
    def _format_check_summary(self, risk_report: Dict[str, Any], draft_notes: Dict[str, Any]) -> str:
        """Format check run summary"""
        risk_assessment = risk_report["risk_assessment"]
        
        summary_parts = []
        summary_parts.append(f"Risk Level: **{risk_assessment['risk_level'].title()}**")
        summary_parts.append(f"Overall Risk Score: **{risk_assessment['overall_score']:.2f}/1.0**")
        summary_parts.append(f"Confidence: {risk_assessment['confidence']:.2f}")
        
        if draft_notes:
            summary_parts.append(f"Suggested Version: **{draft_notes.get('version', 'patch')}**")
        
        return " | ".join(summary_parts)
    
    def _format_detailed_analysis(self, risk_report: Dict[str, Any], draft_notes: Dict[str, Any]) -> str:
        """Format detailed analysis for check run"""
        detailed_risks = risk_report["detailed_risks"]
        recommendations = risk_report["recommendations"]
        
        analysis_parts = []
        
        # Detailed risk metrics
        analysis_parts.append("## Detailed Risk Analysis")
        analysis_parts.append("")
        analysis_parts.append("| Risk Category | Score | Level |")
        analysis_parts.append("|---------------|-------|-------|")
        analysis_parts.append(f"| Bug Probability | {detailed_risks['bug_probability']:.2f} | {self._score_to_level(detailed_risks['bug_probability'])} |")
        analysis_parts.append(f"| Security Risk | {detailed_risks['security_risk']:.2f} | {self._score_to_level(detailed_risks['security_risk'])} |")
        analysis_parts.append(f"| Performance Risk | {detailed_risks['performance_risk']:.2f} | {self._score_to_level(detailed_risks['performance_risk'])} |")
        analysis_parts.append(f"| Complexity Risk | {detailed_risks['complexity_risk']:.2f} | {self._score_to_level(detailed_risks['complexity_risk'])} |")
        analysis_parts.append("")
        
        # Recommendations
        if recommendations:
            analysis_parts.append("## Recommendations")
            for i, rec in enumerate(recommendations, 1):
                analysis_parts.append(f"{i}. {rec}")
            analysis_parts.append("")
        
        # Draft release notes
        if draft_notes and draft_notes.get("release_notes"):
            analysis_parts.append("## Draft Release Notes Preview")
            analysis_parts.append(draft_notes["release_notes"][:500] + "..." if len(draft_notes["release_notes"]) > 500 else draft_notes["release_notes"])
        
        return "\n".join(analysis_parts)
    
    def _score_to_level(self, score: float) -> str:
        """Convert numeric score to risk level"""
        if score >= 0.7:
            return "🚨 High"
        elif score >= 0.4:
            return "⚠️ Moderate" 
        else:
            return "✅ Low"
    
    def _get_merge_recommendation(self, risk_level: str) -> str:
        """Get merge recommendation based on risk level"""
        recommendations = {
            "low": "✅ **Safe to merge** - Low risk detected. Standard review process is sufficient.",
            "moderate": "⚠️ **Proceed with caution** - Moderate risk detected. Consider additional testing and review.",
            "high": "🚨 **Hold for review** - High risk detected. Requires thorough review, additional testing, and possible risk mitigation."
        }
        return recommendations.get(risk_level, "Review required before merge.")
    
    def _generate_report_url(self, repo: str, pr_number: int) -> str:
        """Generate URL for detailed risk report"""
        # This would link to a detailed dashboard in a real implementation
        return f"https://github.com/{repo}/pull/{pr_number}#codesnip-analysis"

class WorkflowStatusManager:
    """Manage workflow status across different CI/CD platforms"""
    
    def __init__(self):
        self.status_symbols = {
            "low": "✅",
            "moderate": "⚠️", 
            "high": "🚨"
        }
        self.status_colors = {
            "low": "28a745",    # Green
            "moderate": "ffc107", # Yellow
            "high": "dc3545"     # Red
        }
    
    def create_workflow_status(self, risk_level: str, overall_score: float, 
                             pr_number: int) -> Dict[str, Any]:
        """Create standardized workflow status"""
        symbol = self.status_symbols.get(risk_level, "❓")
        color = self.status_colors.get(risk_level, "6c757d")
        
        return {
            "symbol": symbol,
            "color": color,
            "status": risk_level,
            "score": overall_score,
            "badge_url": self._generate_badge_url(symbol, risk_level, color),
            "dashboard_url": f"#pr-{pr_number}-analysis",
            "workflow_result": {
                "conclusion": "success" if risk_level == "low" else "failure" if risk_level == "high" else "neutral",
                "title": f"{symbol} Risk Assessment: {risk_level.title()}",
                "summary": f"Overall risk score: {overall_score:.2f}/1.0"
            }
        }
    
    def _generate_badge_url(self, symbol: str, risk_level: str, color: str) -> str:
        """Generate shields.io badge URL for status"""
        import urllib.parse
        label = urllib.parse.quote(f"Risk {symbol}")
        message = urllib.parse.quote(risk_level.title())
        return f"https://img.shields.io/badge/{label}-{message}-{color}"