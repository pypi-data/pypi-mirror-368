import re
import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class DraftReleaseNotesGenerator:
    """Generate draft release notes from PR changes before merge"""
    
    def __init__(self):
        self.feature_patterns = [
            r'add|new|create|implement|introduce',
            r'feature|functionality|capability',
            r'endpoint|api|route',
            r'component|module|service'
        ]
        
        self.bugfix_patterns = [
            r'fix|bug|issue|problem|error',
            r'resolve|correct|repair',
            r'crash|failure|exception',
            r'memory leak|performance'
        ]
        
        self.breaking_patterns = [
            r'breaking|remove|delete|deprecate',
            r'rename|move|change.*signature',
            r'major|incompatible',
            r'migration|upgrade'
        ]
    
    def generate_draft_notes(self, pr_data: Dict[str, Any], code_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive draft release notes"""
        logger.info(f"Generating draft release notes for PR #{pr_data.get('number')}")
        
        # Analyze PR for categorization
        changes = self._categorize_changes(pr_data, code_analysis)
        
        # Suggest version bump
        version_suggestion = self._suggest_version_bump(changes)
        
        # Generate structured draft
        draft = {
            "version": version_suggestion,
            "pr_number": pr_data.get('number'),
            "title": pr_data.get('title', ''),
            "generated_at": datetime.now().isoformat(),
            "changes": changes,
            "release_notes": self._format_release_notes(changes, pr_data),
            "migration_notes": self._generate_migration_notes(changes),
            "confidence_score": self._calculate_confidence(changes, code_analysis)
        }
        
        logger.info(f"Draft release notes generated with confidence: {draft['confidence_score']}")
        return draft
    
    def _categorize_changes(self, pr_data: Dict[str, Any], code_analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """Categorize changes based on PR content and code analysis"""
        changes = {
            "features": [],
            "bug_fixes": [],
            "improvements": [],
            "breaking_changes": [],
            "documentation": [],
            "dependencies": []
        }
        
        title = (pr_data.get('title') or '').lower()
        body = (pr_data.get('body') or '').lower()
        diff = pr_data.get('diff', '')
        
        # Analyze title and description
        if self._matches_patterns(title + ' ' + body, self.feature_patterns):
            changes["features"].append(self._extract_feature_description(pr_data))
        
        if self._matches_patterns(title + ' ' + body, self.bugfix_patterns):
            changes["bug_fixes"].append(self._extract_bugfix_description(pr_data))
        
        if self._matches_patterns(title + ' ' + body, self.breaking_patterns):
            changes["breaking_changes"].append(self._extract_breaking_change_description(pr_data))
        
        # Analyze code changes
        if code_analysis:
            changes.update(self._analyze_code_changes(code_analysis, diff))
        
        # Clean up empty categories
        return {k: v for k, v in changes.items() if v}
    
    def _matches_patterns(self, text: str, patterns: List[str]) -> bool:
        """Check if text matches any of the given patterns"""
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)
    
    def _extract_feature_description(self, pr_data: Dict[str, Any]) -> str:
        """Extract user-friendly feature description"""
        title = pr_data.get('title', '')
        
        # Clean up technical jargon
        cleaned_title = re.sub(r'^(feat|feature|add|new):\s*', '', title, flags=re.IGNORECASE)
        cleaned_title = cleaned_title.strip()
        
        if not cleaned_title.endswith('.'):
            cleaned_title += '.'
        
        return cleaned_title.capitalize()
    
    def _extract_bugfix_description(self, pr_data: Dict[str, Any]) -> str:
        """Extract user-friendly bug fix description"""
        title = pr_data.get('title', '')
        
        # Clean up technical jargon
        cleaned_title = re.sub(r'^(fix|bug|issue):\s*', '', title, flags=re.IGNORECASE)
        cleaned_title = cleaned_title.strip()
        
        if not cleaned_title.startswith(('Fixed', 'Resolved')):
            cleaned_title = f"Fixed {cleaned_title.lower()}"
        
        if not cleaned_title.endswith('.'):
            cleaned_title += '.'
        
        return cleaned_title.capitalize()
    
    def _extract_breaking_change_description(self, pr_data: Dict[str, Any]) -> str:
        """Extract breaking change description with migration hints"""
        title = pr_data.get('title', '')
        body = pr_data.get('body', '')
        
        cleaned_title = re.sub(r'^(breaking|remove|deprecate):\s*', '', title, flags=re.IGNORECASE)
        
        # Look for migration information in PR body
        migration_info = ""
        if "migration" in body.lower() or "upgrade" in body.lower():
            migration_info = " (See migration guide below)"
        
        return f"{cleaned_title.strip()}{migration_info}."
    
    def _analyze_code_changes(self, code_analysis: Dict[str, Any], diff: str) -> Dict[str, List[str]]:
        """Analyze actual code changes for additional categorization"""
        changes = {
            "dependencies": [],
            "documentation": [],
            "improvements": []
        }
        
        # Check for dependency changes
        if 'package.json' in diff or 'requirements.txt' in diff or 'pyproject.toml' in diff:
            changes["dependencies"].append("Updated project dependencies")
        
        # Check for documentation changes
        if any(doc_file in diff for doc_file in ['.md', '.rst', '.txt', 'README']):
            changes["documentation"].append("Updated documentation")
        
        # Check for test additions
        if 'test' in diff and '+' in diff:
            changes["improvements"].append("Added test coverage")
        
        # Check for performance improvements
        if any(perf_keyword in diff for perf_keyword in ['optimize', 'performance', 'cache', 'async']):
            changes["improvements"].append("Performance improvements")
        
        return changes
    
    def _suggest_version_bump(self, changes: Dict[str, List[str]]) -> str:
        """Suggest semantic version bump based on changes"""
        if changes.get("breaking_changes"):
            return "major"
        elif changes.get("features"):
            return "minor"
        elif changes.get("bug_fixes") or changes.get("improvements"):
            return "patch"
        else:
            return "patch"  # Default to patch for any changes
    
    def _format_release_notes(self, changes: Dict[str, List[str]], pr_data: Dict[str, Any]) -> str:
        """Format changes into markdown release notes"""
        notes = []
        pr_number = pr_data.get('number', '')
        
        notes.append(f"## Draft Release Notes")
        notes.append(f"*Generated from PR #{pr_number}: {pr_data.get('title', '')}*\n")
        
        if changes.get("features"):
            notes.append("### ✨ New Features")
            for feature in changes["features"]:
                notes.append(f"- {feature}")
            notes.append("")
        
        if changes.get("improvements"):
            notes.append("### 📈 Improvements")
            for improvement in changes["improvements"]:
                notes.append(f"- {improvement}")
            notes.append("")
        
        if changes.get("bug_fixes"):
            notes.append("### 🐛 Bug Fixes")
            for fix in changes["bug_fixes"]:
                notes.append(f"- {fix}")
            notes.append("")
        
        if changes.get("breaking_changes"):
            notes.append("### ⚠️ Breaking Changes")
            for breaking in changes["breaking_changes"]:
                notes.append(f"- {breaking}")
            notes.append("")
        
        if changes.get("dependencies"):
            notes.append("### 📦 Dependencies")
            for dep in changes["dependencies"]:
                notes.append(f"- {dep}")
            notes.append("")
        
        if changes.get("documentation"):
            notes.append("### 📝 Documentation")
            for doc in changes["documentation"]:
                notes.append(f"- {doc}")
            notes.append("")
        
        return "\n".join(notes)
    
    def _generate_migration_notes(self, changes: Dict[str, List[str]]) -> str:
        """Generate migration notes for breaking changes"""
        if not changes.get("breaking_changes"):
            return ""
        
        notes = []
        notes.append("## Migration Guide")
        notes.append("This release contains breaking changes. Please review the following:")
        notes.append("")
        
        for breaking_change in changes["breaking_changes"]:
            notes.append(f"### {breaking_change}")
            notes.append("- Review your code for compatibility")
            notes.append("- Update API calls if necessary")
            notes.append("- Test thoroughly before upgrading")
            notes.append("")
        
        return "\n".join(notes)
    
    def _calculate_confidence(self, changes: Dict[str, List[str]], code_analysis: Dict[str, Any]) -> float:
        """Calculate confidence score for the generated notes"""
        confidence = 0.5  # Base confidence
        
        # Higher confidence if we have more information
        if changes:
            confidence += 0.2
        
        if code_analysis:
            confidence += 0.2
        
        # Lower confidence for breaking changes (need human review)
        if changes.get("breaking_changes"):
            confidence -= 0.1
        
        # Higher confidence for simple bug fixes
        if changes.get("bug_fixes") and not changes.get("breaking_changes"):
            confidence += 0.1
        
        return min(1.0, max(0.0, confidence))