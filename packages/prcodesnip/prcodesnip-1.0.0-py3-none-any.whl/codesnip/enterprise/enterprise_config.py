"""
Enterprise-grade configuration system for CodeSnip
Supports team configurations, compliance settings, and organizational policies
"""
import os
import json
import yaml
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import datetime
from dataclasses import dataclass, asdict
import hashlib
import secrets
import base64

logger = logging.getLogger(__name__)

@dataclass
class OrganizationConfig:
    """Organization-level configuration"""
    org_id: str
    org_name: str
    domain: str
    compliance_level: str  # 'basic', 'standard', 'strict', 'enterprise'
    allowed_languages: List[str]
    required_quality_score: int
    security_policies: Dict[str, Any]
    audit_enabled: bool
    sso_enabled: bool
    custom_rules: Dict[str, Any]
    created_at: str
    updated_at: str

@dataclass
class TeamConfig:
    """Team-level configuration"""
    team_id: str
    team_name: str
    org_id: str
    repositories: List[str]
    members: List[str]
    quality_thresholds: Dict[str, int]
    workflow_templates: Dict[str, str]
    notification_settings: Dict[str, Any]
    custom_integrations: Dict[str, Any]

@dataclass
class ComplianceConfig:
    """Compliance and regulatory configuration"""
    standards: List[str]  # ['SOX', 'GDPR', 'HIPAA', 'PCI-DSS', 'ISO27001']
    data_retention_days: int
    encryption_required: bool
    audit_trail_required: bool
    code_review_mandatory: bool
    security_scan_required: bool
    vulnerability_threshold: str  # 'low', 'medium', 'high', 'critical'
    license_compliance: bool
    third_party_approval_required: bool

class EnterpriseConfigManager:
    """Manages enterprise-grade configurations"""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else Path.home() / '.codesnip' / 'enterprise'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.org_config_file = self.config_dir / 'organization.yaml'
        self.team_configs_dir = self.config_dir / 'teams'
        self.compliance_config_file = self.config_dir / 'compliance.yaml'
        self.audit_log_file = self.config_dir / 'audit.log'
        
        self.team_configs_dir.mkdir(exist_ok=True)
        
        # Load configurations
        self.org_config = self._load_org_config()
        self.compliance_config = self._load_compliance_config()
    
    def create_organization_config(self, org_name: str, domain: str, 
                                 compliance_level: str = 'standard') -> OrganizationConfig:
        """Create a new organization configuration"""
        
        org_id = self._generate_org_id(org_name, domain)
        
        # Default security policies
        default_security_policies = {
            'require_2fa': True,
            'session_timeout_minutes': 60,
            'password_policy': {
                'min_length': 12,
                'require_uppercase': True,
                'require_lowercase': True,
                'require_numbers': True,
                'require_symbols': True
            },
            'api_rate_limits': {
                'requests_per_minute': 1000,
                'burst_limit': 100
            },
            'ip_whitelist': [],
            'allowed_integrations': ['github', 'gitlab', 'bitbucket'],
            'data_encryption': {
                'in_transit': True,
                'at_rest': True,
                'key_rotation_days': 90
            }
        }
        
        # Compliance-specific settings
        if compliance_level == 'enterprise':
            default_security_policies.update({
                'require_vpn': True,
                'device_management_required': True,
                'code_signing_required': True,
                'security_training_required': True
            })
        
        org_config = OrganizationConfig(
            org_id=org_id,
            org_name=org_name,
            domain=domain,
            compliance_level=compliance_level,
            allowed_languages=['python', 'javascript', 'typescript', 'go', 'java', 'csharp', 'rust'],
            required_quality_score=80,
            security_policies=default_security_policies,
            audit_enabled=True,
            sso_enabled=compliance_level in ['strict', 'enterprise'],
            custom_rules={},
            created_at=datetime.datetime.utcnow().isoformat(),
            updated_at=datetime.datetime.utcnow().isoformat()
        )
        
        self._save_org_config(org_config)
        self._audit_log('organization_created', {'org_id': org_id, 'org_name': org_name})
        
        return org_config
    
    def create_team_config(self, team_name: str, repositories: List[str], 
                          members: List[str]) -> TeamConfig:
        """Create a new team configuration"""
        
        if not self.org_config:
            raise ValueError("Organization configuration must be created first")
        
        team_id = self._generate_team_id(team_name)
        
        # Default quality thresholds
        quality_thresholds = {
            'minimum_quality_score': self.org_config.required_quality_score,
            'max_critical_issues': 0,
            'max_high_issues': 2,
            'max_medium_issues': 10,
            'code_coverage_minimum': 80,
            'complexity_threshold': 10
        }
        
        # Default workflow templates
        workflow_templates = {
            'pull_request': 'standard_pr_review',
            'deployment': 'secure_deployment',
            'hotfix': 'emergency_hotfix'
        }
        
        # Default notification settings
        notification_settings = {
            'email_notifications': True,
            'slack_integration': False,
            'teams_integration': False,
            'webhook_urls': [],
            'escalation_rules': {
                'critical_issues': 'immediate',
                'high_issues': '1_hour',
                'failed_builds': '30_minutes'
            }
        }
        
        team_config = TeamConfig(
            team_id=team_id,
            team_name=team_name,
            org_id=self.org_config.org_id,
            repositories=repositories,
            members=members,
            quality_thresholds=quality_thresholds,
            workflow_templates=workflow_templates,
            notification_settings=notification_settings,
            custom_integrations={}
        )
        
        self._save_team_config(team_config)
        self._audit_log('team_created', {'team_id': team_id, 'team_name': team_name})
        
        return team_config
    
    def create_compliance_config(self, standards: List[str]) -> ComplianceConfig:
        """Create compliance configuration"""
        
        # Default settings based on standards
        data_retention_days = 2555  # 7 years default
        encryption_required = True
        audit_trail_required = True
        vulnerability_threshold = 'medium'
        
        # Adjust settings based on compliance standards
        if 'SOX' in standards:
            data_retention_days = max(data_retention_days, 2555)  # 7 years
            audit_trail_required = True
        
        if 'GDPR' in standards:
            data_retention_days = min(data_retention_days, 1095)  # 3 years max
            encryption_required = True
        
        if 'HIPAA' in standards:
            encryption_required = True
            vulnerability_threshold = 'low'
        
        if 'PCI-DSS' in standards:
            vulnerability_threshold = 'low'
            encryption_required = True
        
        compliance_config = ComplianceConfig(
            standards=standards,
            data_retention_days=data_retention_days,
            encryption_required=encryption_required,
            audit_trail_required=audit_trail_required,
            code_review_mandatory=True,
            security_scan_required=True,
            vulnerability_threshold=vulnerability_threshold,
            license_compliance=True,
            third_party_approval_required='SOX' in standards or 'PCI-DSS' in standards
        )
        
        self._save_compliance_config(compliance_config)
        self._audit_log('compliance_config_created', {'standards': standards})
        
        return compliance_config
    
    def get_team_config(self, team_id: str) -> Optional[TeamConfig]:
        """Get team configuration"""
        team_config_file = self.team_configs_dir / f'{team_id}.yaml'
        
        if not team_config_file.exists():
            return None
        
        try:
            with open(team_config_file, 'r') as f:
                data = yaml.safe_load(f)
            return TeamConfig(**data)
        except Exception as e:
            logger.error(f"Failed to load team config {team_id}: {e}")
            return None
    
    def get_repository_config(self, repository: str) -> Dict[str, Any]:
        """Get configuration for a specific repository"""
        
        # Find team that owns this repository
        team_config = None
        for team_file in self.team_configs_dir.glob('*.yaml'):
            try:
                with open(team_file, 'r') as f:
                    data = yaml.safe_load(f)
                    if repository in data.get('repositories', []):
                        team_config = TeamConfig(**data)
                        break
            except Exception:
                continue
        
        # Combine org, team, and compliance configs
        config = {
            'organization': asdict(self.org_config) if self.org_config else {},
            'team': asdict(team_config) if team_config else {},
            'compliance': asdict(self.compliance_config) if self.compliance_config else {}
        }
        
        return config
    
    def validate_pr_compliance(self, repository: str, pr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate PR against compliance requirements"""
        
        repo_config = self.get_repository_config(repository)
        compliance = repo_config.get('compliance', {})
        
        violations = []
        warnings = []
        
        # Check if code review is mandatory
        if compliance.get('code_review_mandatory', False):
            reviews = pr_data.get('reviews', [])
            approved_reviews = [r for r in reviews if r.get('state') == 'APPROVED']
            if not approved_reviews:
                violations.append("Code review is mandatory but no approvals found")
        
        # Check security scan requirement
        if compliance.get('security_scan_required', False):
            # This would integrate with security scanning tools
            # For now, we'll assume it's checked elsewhere
            pass
        
        # Check vulnerability threshold
        vuln_threshold = compliance.get('vulnerability_threshold', 'medium')
        # This would integrate with vulnerability scanning
        
        return {
            'compliant': len(violations) == 0,
            'violations': violations,
            'warnings': warnings,
            'compliance_level': compliance.get('standards', [])
        }
    
    def generate_audit_report(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Generate audit report for specified date range"""
        
        if not self.audit_log_file.exists():
            return {'error': 'No audit log found'}
        
        try:
            start_dt = datetime.datetime.fromisoformat(start_date)
            end_dt = datetime.datetime.fromisoformat(end_date)
        except ValueError:
            return {'error': 'Invalid date format. Use ISO format (YYYY-MM-DD)'}
        
        audit_entries = []
        
        try:
            with open(self.audit_log_file, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        entry_date = datetime.datetime.fromisoformat(entry['timestamp'])
                        
                        if start_dt <= entry_date <= end_dt:
                            audit_entries.append(entry)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            return {'error': f'Failed to read audit log: {e}'}
        
        # Generate summary statistics
        action_counts = {}
        user_actions = {}
        
        for entry in audit_entries:
            action = entry.get('action', 'unknown')
            user = entry.get('user', 'unknown')
            
            action_counts[action] = action_counts.get(action, 0) + 1
            if user not in user_actions:
                user_actions[user] = {}
            user_actions[user][action] = user_actions[user].get(action, 0) + 1
        
        return {
            'period': {'start': start_date, 'end': end_date},
            'total_entries': len(audit_entries),
            'action_summary': action_counts,
            'user_activity': user_actions,
            'entries': audit_entries
        }
    
    def export_configuration(self) -> Dict[str, Any]:
        """Export all configurations for backup/migration"""
        
        config_export = {
            'export_version': '1.0',
            'export_timestamp': datetime.datetime.utcnow().isoformat(),
            'organization': asdict(self.org_config) if self.org_config else None,
            'compliance': asdict(self.compliance_config) if self.compliance_config else None,
            'teams': []
        }
        
        # Export team configurations
        for team_file in self.team_configs_dir.glob('*.yaml'):
            try:
                with open(team_file, 'r') as f:
                    team_data = yaml.safe_load(f)
                    config_export['teams'].append(team_data)
            except Exception as e:
                logger.error(f"Failed to export team config {team_file}: {e}")
        
        return config_export
    
    def import_configuration(self, config_data: Dict[str, Any]) -> bool:
        """Import configuration from backup/migration"""
        
        try:
            # Import organization config
            if config_data.get('organization'):
                org_config = OrganizationConfig(**config_data['organization'])
                self._save_org_config(org_config)
                self.org_config = org_config
            
            # Import compliance config
            if config_data.get('compliance'):
                compliance_config = ComplianceConfig(**config_data['compliance'])
                self._save_compliance_config(compliance_config)
                self.compliance_config = compliance_config
            
            # Import team configs
            for team_data in config_data.get('teams', []):
                team_config = TeamConfig(**team_data)
                self._save_team_config(team_config)
            
            self._audit_log('configuration_imported', {
                'teams_count': len(config_data.get('teams', [])),
                'has_org_config': bool(config_data.get('organization')),
                'has_compliance_config': bool(config_data.get('compliance'))
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Configuration import failed: {e}")
            return False
    
    # Private helper methods
    def _generate_org_id(self, org_name: str, domain: str) -> str:
        """Generate unique organization ID"""
        data = f"{org_name}:{domain}:{datetime.datetime.utcnow().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _generate_team_id(self, team_name: str) -> str:
        """Generate unique team ID"""
        data = f"{team_name}:{datetime.datetime.utcnow().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:12]
    
    def _load_org_config(self) -> Optional[OrganizationConfig]:
        """Load organization configuration"""
        if not self.org_config_file.exists():
            return None
        
        try:
            with open(self.org_config_file, 'r') as f:
                data = yaml.safe_load(f)
            return OrganizationConfig(**data)
        except Exception as e:
            logger.error(f"Failed to load organization config: {e}")
            return None
    
    def _load_compliance_config(self) -> Optional[ComplianceConfig]:
        """Load compliance configuration"""
        if not self.compliance_config_file.exists():
            return None
        
        try:
            with open(self.compliance_config_file, 'r') as f:
                data = yaml.safe_load(f)
            return ComplianceConfig(**data)
        except Exception as e:
            logger.error(f"Failed to load compliance config: {e}")
            return None
    
    def _save_org_config(self, config: OrganizationConfig) -> None:
        """Save organization configuration"""
        try:
            with open(self.org_config_file, 'w') as f:
                yaml.dump(asdict(config), f, default_flow_style=False)
        except Exception as e:
            logger.error(f"Failed to save organization config: {e}")
    
    def _save_team_config(self, config: TeamConfig) -> None:
        """Save team configuration"""
        try:
            team_config_file = self.team_configs_dir / f'{config.team_id}.yaml'
            with open(team_config_file, 'w') as f:
                yaml.dump(asdict(config), f, default_flow_style=False)
        except Exception as e:
            logger.error(f"Failed to save team config: {e}")
    
    def _save_compliance_config(self, config: ComplianceConfig) -> None:
        """Save compliance configuration"""
        try:
            with open(self.compliance_config_file, 'w') as f:
                yaml.dump(asdict(config), f, default_flow_style=False)
        except Exception as e:
            logger.error(f"Failed to save compliance config: {e}")
    
    def _audit_log(self, action: str, details: Dict[str, Any]) -> None:
        """Log audit trail entry"""
        
        entry = {
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'action': action,
            'user': os.getenv('USER', 'unknown'),
            'details': details,
            'session_id': self._get_session_id()
        }
        
        try:
            with open(self.audit_log_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def _get_session_id(self) -> str:
        """Get or generate session ID"""
        session_id = getattr(self, '_session_id', None)
        if not session_id:
            self._session_id = secrets.token_hex(16)
        return self._session_id