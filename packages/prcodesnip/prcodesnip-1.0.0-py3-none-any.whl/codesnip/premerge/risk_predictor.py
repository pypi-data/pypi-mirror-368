import re
import logging
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class RiskScore:
    """Risk score with detailed breakdown"""
    overall_risk: float  # 0.0-1.0
    bug_probability: float
    security_risk: float
    performance_risk: float
    complexity_risk: float
    confidence: float
    risk_level: str  # "low", "moderate", "high"
    risk_symbol: str  # ✅, ⚠️, 🚨

class EarlyRiskPredictor:
    """Predict risks before PR is merged using ML-inspired heuristics"""
    
    def __init__(self):
        self.high_risk_patterns = [
            r'auth|authentication|security|login|password',
            r'database|sql|query|migration',
            r'payment|billing|transaction|money',
            r'admin|root|sudo|privilege'
        ]
        
        self.performance_risk_patterns = [
            r'loop|iteration|recursive',
            r'database.*query|select.*from',
            r'async|await|promise|thread',
            r'cache|memory|storage'
        ]
        
        self.complexity_indicators = [
            r'if.*else.*if',  # Nested conditionals
            r'for.*in.*for',  # Nested loops
            r'try.*except.*try',  # Nested error handling
            r'class.*class.*class'  # Deep inheritance
        ]
    
    def predict_risks(self, pr_data: Dict[str, Any], code_analysis: Dict[str, Any] = None) -> RiskScore:
        """Comprehensive risk prediction for PR"""
        logger.info(f"Starting risk prediction for PR #{pr_data.get('number')}")
        
        # Individual risk components
        bug_risk = self._predict_bug_probability(pr_data, code_analysis)
        security_risk = self._assess_security_risk(pr_data, code_analysis)
        performance_risk = self._assess_performance_risk(pr_data, code_analysis)
        complexity_risk = self._assess_complexity_risk(pr_data, code_analysis)
        
        # Calculate overall risk (weighted average)
        overall_risk = self._calculate_overall_risk(
            bug_risk, security_risk, performance_risk, complexity_risk
        )
        
        # Determine risk level and symbol
        risk_level, risk_symbol = self._determine_risk_level(overall_risk)
        
        # Calculate confidence in prediction
        confidence = self._calculate_prediction_confidence(pr_data, code_analysis)
        
        risk_score = RiskScore(
            overall_risk=overall_risk,
            bug_probability=bug_risk,
            security_risk=security_risk,
            performance_risk=performance_risk,
            complexity_risk=complexity_risk,
            confidence=confidence,
            risk_level=risk_level,
            risk_symbol=risk_symbol
        )
        
        logger.info(f"Risk prediction complete: {risk_level} risk ({risk_symbol}) with {confidence:.2f} confidence")
        return risk_score
    
    def _predict_bug_probability(self, pr_data: Dict[str, Any], code_analysis: Dict[str, Any]) -> float:
        """Predict likelihood of bugs using various indicators"""
        risk = 0.0
        
        title = (pr_data.get('title') or '').lower()
        body = (pr_data.get('body') or '').lower()
        diff = pr_data.get('diff', '')
        
        # Size-based risk (larger changes = higher risk)
        additions = pr_data.get('additions', 0)
        deletions = pr_data.get('deletions', 0)
        total_changes = additions + deletions
        
        if total_changes > 500:
            risk += 0.3
        elif total_changes > 200:
            risk += 0.2
        elif total_changes > 50:
            risk += 0.1
        
        # Files changed risk
        files_changed = pr_data.get('files_changed', 0)
        if files_changed > 10:
            risk += 0.2
        elif files_changed > 5:
            risk += 0.1
        
        # Pattern-based risk assessment
        risky_content = title + ' ' + body + ' ' + diff
        
        # Check for hasty fixes (often introduce bugs)
        if any(keyword in risky_content for keyword in ['quick fix', 'hotfix', 'urgent', 'asap']):
            risk += 0.2
        
        # Check for complex logic changes
        if any(pattern in diff for pattern in ['if ', 'else ', 'for ', 'while ', 'try ', 'catch ']):
            complexity_count = sum(diff.count(pattern) for pattern in ['if ', 'else ', 'for ', 'while '])
            if complexity_count > 10:
                risk += 0.3
            elif complexity_count > 5:
                risk += 0.2
        
        # Check for error handling changes (can be risky)
        if any(keyword in diff for keyword in ['exception', 'error', 'catch', 'finally']):
            risk += 0.1
        
        return min(1.0, risk)
    
    def _assess_security_risk(self, pr_data: Dict[str, Any], code_analysis: Dict[str, Any]) -> float:
        """Assess security-related risks"""
        risk = 0.0
        
        title = (pr_data.get('title') or '').lower()
        body = (pr_data.get('body') or '').lower()
        diff = pr_data.get('diff', '')
        
        content = title + ' ' + body + ' ' + diff
        
        # Check for high-risk security patterns
        for pattern in self.high_risk_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                risk += 0.3
        
        # Check for specific security vulnerabilities
        security_issues = [
            ('sql injection', r'execute.*\+.*|query.*\+.*|".*"\s*\+'),
            ('xss', r'innerHTML|document\.write|eval\('),
            ('hardcoded secrets', r'password.*=.*|api_key.*=.*|secret.*=.*'),
            ('unsafe deserialization', r'pickle\.loads|eval|exec'),
            ('file system access', r'open\(.*input|os\.system|subprocess\.call')
        ]
        
        for issue_name, pattern in security_issues:
            if re.search(pattern, diff, re.IGNORECASE):
                risk += 0.4
                logger.warning(f"Potential {issue_name} vulnerability detected")
        
        # Check for authentication/authorization changes
        if any(auth_term in content for auth_term in ['login', 'auth', 'permission', 'role', 'access']):
            risk += 0.2
        
        return min(1.0, risk)
    
    def _assess_performance_risk(self, pr_data: Dict[str, Any], code_analysis: Dict[str, Any]) -> float:
        """Assess performance impact risks"""
        risk = 0.0
        
        diff = pr_data.get('diff', '')
        
        # Check for performance-related patterns
        for pattern in self.performance_risk_patterns:
            if re.search(pattern, diff, re.IGNORECASE):
                risk += 0.2
        
        # Check for database-related changes
        if any(db_pattern in diff for db_pattern in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'JOIN']):
            risk += 0.3
        
        # Check for loop modifications
        loop_additions = diff.count('+ ') and any(loop in diff for loop in ['for', 'while', 'map', 'forEach'])
        if loop_additions:
            risk += 0.2
        
        # Check for synchronous to asynchronous changes
        if '+async' in diff or '+await' in diff:
            risk += 0.1  # Usually good, but can introduce complexity
        
        # Check for caching changes
        if any(cache_term in diff for cache_term in ['cache', 'redis', 'memcache', 'storage']):
            risk += 0.1
        
        return min(1.0, risk)
    
    def _assess_complexity_risk(self, pr_data: Dict[str, Any], code_analysis: Dict[str, Any]) -> float:
        """Assess code complexity risks"""
        risk = 0.0
        
        diff = pr_data.get('diff', '')
        
        # Check for complexity indicators
        for pattern in self.complexity_indicators:
            matches = len(re.findall(pattern, diff, re.IGNORECASE))
            if matches > 0:
                risk += min(0.3, matches * 0.1)
        
        # Check for deep nesting (indentation)
        lines = diff.split('\n')
        max_indentation = 0
        for line in lines:
            if line.startswith('+'):
                indentation = len(line) - len(line.lstrip())
                max_indentation = max(max_indentation, indentation)
        
        if max_indentation > 16:  # Very deep nesting
            risk += 0.3
        elif max_indentation > 12:
            risk += 0.2
        elif max_indentation > 8:
            risk += 0.1
        
        # Check for long functions/methods
        function_lengths = []
        current_function_length = 0
        in_function = False
        
        for line in lines:
            if line.startswith('+'):
                if 'def ' in line or 'function ' in line:
                    if in_function:
                        function_lengths.append(current_function_length)
                    in_function = True
                    current_function_length = 1
                elif in_function:
                    current_function_length += 1
                elif any(end_marker in line for end_marker in ['}', 'return']):
                    if in_function:
                        function_lengths.append(current_function_length)
                        in_function = False
        
        if function_lengths:
            avg_length = sum(function_lengths) / len(function_lengths)
            if avg_length > 50:
                risk += 0.3
            elif avg_length > 30:
                risk += 0.2
        
        return min(1.0, risk)
    
    def _calculate_overall_risk(self, bug_risk: float, security_risk: float, 
                              performance_risk: float, complexity_risk: float) -> float:
        """Calculate weighted overall risk score"""
        # Security gets highest weight, then bugs, then complexity, then performance
        weights = {
            'security': 0.4,
            'bug': 0.3,
            'complexity': 0.2,
            'performance': 0.1
        }
        
        overall = (
            security_risk * weights['security'] +
            bug_risk * weights['bug'] +
            complexity_risk * weights['complexity'] +
            performance_risk * weights['performance']
        )
        
        return min(1.0, overall)
    
    def _determine_risk_level(self, overall_risk: float) -> Tuple[str, str]:
        """Determine risk level and corresponding symbol"""
        if overall_risk >= 0.7:
            return "high", "🚨"
        elif overall_risk >= 0.4:
            return "moderate", "⚠️"
        else:
            return "low", "✅"
    
    def _calculate_prediction_confidence(self, pr_data: Dict[str, Any], 
                                       code_analysis: Dict[str, Any]) -> float:
        """Calculate confidence in the risk prediction"""
        confidence = 0.5  # Base confidence
        
        # More data = higher confidence
        if pr_data.get('body'):
            confidence += 0.1
        
        if pr_data.get('diff'):
            confidence += 0.2
        
        if code_analysis:
            confidence += 0.2
        
        # Size matters for confidence
        total_changes = pr_data.get('additions', 0) + pr_data.get('deletions', 0)
        if total_changes > 100:
            confidence += 0.1
        elif total_changes < 10:
            confidence -= 0.1  # Hard to predict for very small changes
        
        return min(1.0, max(0.1, confidence))
    
    def generate_risk_report(self, risk_score: RiskScore, pr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive risk report"""
        return {
            "pr_number": pr_data.get('number'),
            "risk_assessment": {
                "overall_score": round(risk_score.overall_risk, 2),
                "risk_level": risk_score.risk_level,
                "risk_symbol": risk_score.risk_symbol,
                "confidence": round(risk_score.confidence, 2)
            },
            "detailed_risks": {
                "bug_probability": round(risk_score.bug_probability, 2),
                "security_risk": round(risk_score.security_risk, 2),
                "performance_risk": round(risk_score.performance_risk, 2),
                "complexity_risk": round(risk_score.complexity_risk, 2)
            },
            "recommendations": self._generate_risk_recommendations(risk_score),
            "status_check": {
                "state": "failure" if risk_score.risk_level == "high" else "success" if risk_score.risk_level == "low" else "pending",
                "description": f"{risk_score.risk_symbol} Risk Level: {risk_score.risk_level.title()}",
                "context": "codesnip/risk-analysis"
            }
        }
    
    def _generate_risk_recommendations(self, risk_score: RiskScore) -> List[str]:
        """Generate recommendations based on risk assessment"""
        recommendations = []
        
        if risk_score.bug_probability > 0.6:
            recommendations.append("🧪 Add comprehensive unit tests for modified functions")
            recommendations.append("👥 Request additional code review from senior developer")
        
        if risk_score.security_risk > 0.5:
            recommendations.append("🔒 Conduct security review before merge")
            recommendations.append("🛡️ Run security scanning tools (SAST/DAST)")
        
        if risk_score.performance_risk > 0.5:
            recommendations.append("⚡ Run performance tests on staging environment")
            recommendations.append("📊 Monitor key performance metrics after deployment")
        
        if risk_score.complexity_risk > 0.6:
            recommendations.append("🧹 Consider refactoring to reduce complexity")
            recommendations.append("📚 Add comprehensive documentation for complex logic")
        
        if risk_score.overall_risk > 0.7:
            recommendations.append("🚨 Consider breaking this PR into smaller, focused changes")
            recommendations.append("⏳ Allow extra time for testing and review")
        
        return recommendations