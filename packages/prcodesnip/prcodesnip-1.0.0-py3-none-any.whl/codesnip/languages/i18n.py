"""
Internationalization (i18n) support for CodeSnip CLI
Supports multiple languages and locales for worldwide usage
"""
import os
import json
import logging
from typing import Dict, Optional, Any
from pathlib import Path
import locale
import gettext

logger = logging.getLogger(__name__)

class InternationalizationManager:
    """Manages internationalization and localization"""
    
    # Supported languages with their locale codes
    SUPPORTED_LANGUAGES = {
        'en': {'name': 'English', 'locale': 'en_US', 'flag': '🇺🇸'},
        'es': {'name': 'Español', 'locale': 'es_ES', 'flag': '🇪🇸'},
        'fr': {'name': 'Français', 'locale': 'fr_FR', 'flag': '🇫🇷'},
        'de': {'name': 'Deutsch', 'locale': 'de_DE', 'flag': '🇩🇪'},
        'it': {'name': 'Italiano', 'locale': 'it_IT', 'flag': '🇮🇹'},
        'pt': {'name': 'Português', 'locale': 'pt_BR', 'flag': '🇧🇷'},
        'ru': {'name': 'Русский', 'locale': 'ru_RU', 'flag': '🇷🇺'},
        'zh': {'name': '中文', 'locale': 'zh_CN', 'flag': '🇨🇳'},
        'ja': {'name': '日本語', 'locale': 'ja_JP', 'flag': '🇯🇵'},
        'ko': {'name': '한국어', 'locale': 'ko_KR', 'flag': '🇰🇷'},
        'hi': {'name': 'हिंदी', 'locale': 'hi_IN', 'flag': '🇮🇳'},
        'ar': {'name': 'العربية', 'locale': 'ar_SA', 'flag': '🇸🇦'},
        'nl': {'name': 'Nederlands', 'locale': 'nl_NL', 'flag': '🇳🇱'},
        'sv': {'name': 'Svenska', 'locale': 'sv_SE', 'flag': '🇸🇪'},
        'no': {'name': 'Norsk', 'locale': 'no_NO', 'flag': '🇳🇴'},
        'da': {'name': 'Dansk', 'locale': 'da_DK', 'flag': '🇩🇰'},
        'fi': {'name': 'Suomi', 'locale': 'fi_FI', 'flag': '🇫🇮'},
        'pl': {'name': 'Polski', 'locale': 'pl_PL', 'flag': '🇵🇱'},
        'tr': {'name': 'Türkçe', 'locale': 'tr_TR', 'flag': '🇹🇷'},
        'cs': {'name': 'Čeština', 'locale': 'cs_CZ', 'flag': '🇨🇿'},
        'hu': {'name': 'Magyar', 'locale': 'hu_HU', 'flag': '🇭🇺'},
        'ro': {'name': 'Română', 'locale': 'ro_RO', 'flag': '🇷🇴'},
        'el': {'name': 'Ελληνικά', 'locale': 'el_GR', 'flag': '🇬🇷'},
        'he': {'name': 'עברית', 'locale': 'he_IL', 'flag': '🇮🇱'},
        'th': {'name': 'ไทย', 'locale': 'th_TH', 'flag': '🇹🇭'},
        'vi': {'name': 'Tiếng Việt', 'locale': 'vi_VN', 'flag': '🇻🇳'},
        'id': {'name': 'Bahasa Indonesia', 'locale': 'id_ID', 'flag': '🇮🇩'},
        'ms': {'name': 'Bahasa Malaysia', 'locale': 'ms_MY', 'flag': '🇲🇾'},
        'tl': {'name': 'Filipino', 'locale': 'tl_PH', 'flag': '🇵🇭'}
    }
    
    def __init__(self):
        self.current_language = 'en'  # Default to English
        self.translations = {}
        self.locale_dir = Path(__file__).parent / 'locales'
        self.locale_dir.mkdir(exist_ok=True)
        
        # Detect system language
        self._detect_system_language()
        
        # Load translations
        self._load_translations()
    
    def _detect_system_language(self) -> None:
        """Detect system language automatically"""
        try:
            # Try to get language from environment
            lang_env = os.getenv('LANG', '').split('.')[0].split('_')[0]
            if lang_env in self.SUPPORTED_LANGUAGES:
                self.current_language = lang_env
                return
            
            # Try system locale
            system_locale = locale.getdefaultlocale()[0]
            if system_locale:
                lang_code = system_locale.split('_')[0]
                if lang_code in self.SUPPORTED_LANGUAGES:
                    self.current_language = lang_code
                    return
        except Exception as e:
            logger.debug(f"Could not detect system language: {e}")
        
        # Default to English if detection fails
        self.current_language = 'en'
    
    def _load_translations(self) -> None:
        """Load translation files for all supported languages"""
        for lang_code in self.SUPPORTED_LANGUAGES:
            translation_file = self.locale_dir / f'{lang_code}.json'
            if translation_file.exists():
                try:
                    with open(translation_file, 'r', encoding='utf-8') as f:
                        self.translations[lang_code] = json.load(f)
                except Exception as e:
                    logger.error(f"Failed to load translations for {lang_code}: {e}")
                    self.translations[lang_code] = {}
            else:
                self.translations[lang_code] = {}
                if lang_code != 'en':  # Create empty translation files
                    self._create_translation_template(lang_code)
    
    def _create_translation_template(self, lang_code: str) -> None:
        """Create translation template for a language"""
        template = self._get_translation_template()
        translation_file = self.locale_dir / f'{lang_code}.json'
        
        try:
            with open(translation_file, 'w', encoding='utf-8') as f:
                json.dump(template, f, ensure_ascii=False, indent=2)
            logger.info(f"Created translation template for {lang_code}")
        except Exception as e:
            logger.error(f"Failed to create translation template for {lang_code}: {e}")
    
    def _get_translation_template(self) -> Dict[str, str]:
        """Get the base translation template in English"""
        return {
            # CLI Interface
            "welcome": "🚀 Welcome to CodeSnip!",
            "setup_wizard_title": "🚀 CodeSnip Setup Wizard",
            "repository_selection": "🏗️ Repository Selection",
            "pr_selection": "📋 Pull Request Selection",
            "language_detection": "🔍 Detecting Programming Languages",
            "quality_analysis": "🔍 Running Quality Analysis",
            "risk_prediction": "🎯 Predicting Risks",
            "draft_release": "📝 Generating Draft Release Notes",
            
            # Status Messages
            "success": "✅ Success",
            "warning": "⚠️ Warning",
            "error": "❌ Error",
            "info": "ℹ️ Info",
            "loading": "⏳ Loading",
            "completed": "✅ Completed",
            "failed": "❌ Failed",
            
            # Configuration
            "config_title": "⚙️ Configuration",
            "github_token": "GitHub Token",
            "openai_key": "OpenAI API Key",
            "default_repo": "Default Repository",
            "language_settings": "Language Settings",
            "quality_tools": "Quality Tools",
            
            # Analysis Results
            "quality_score": "Quality Score",
            "risk_level": "Risk Level",
            "confidence": "Confidence",
            "issues_found": "Issues Found",
            "security_issues": "Security Issues",
            "performance_issues": "Performance Issues",
            "maintainability": "Maintainability",
            
            # Risk Levels
            "risk_low": "Low Risk",
            "risk_moderate": "Moderate Risk",
            "risk_high": "High Risk",
            "risk_critical": "Critical Risk",
            
            # Actions
            "install": "Install",
            "configure": "Configure",
            "analyze": "Analyze",
            "setup": "Setup",
            "test": "Test",
            "build": "Build",
            "deploy": "Deploy",
            "cancel": "Cancel",
            "continue": "Continue",
            "skip": "Skip",
            "retry": "Retry",
            
            # Language Detection
            "detecting_languages": "Detecting programming languages in repository",
            "primary_language": "Primary Language",
            "detected_languages": "Detected Languages",
            "installing_tools": "Installing required tools for",
            "tools_installed": "Tools successfully installed",
            "tools_failed": "Failed to install some tools",
            
            # Workflow Integration
            "workflow_setup": "Setting up CI/CD workflows",
            "workflow_created": "Workflow configuration created",
            "github_integration": "GitHub integration configured",
            "status_checks": "Status checks enabled",
            
            # Error Messages
            "token_required": "GitHub token is required",
            "repo_not_found": "Repository not found",
            "pr_not_found": "Pull request not found",
            "api_error": "API request failed",
            "network_error": "Network connection failed",
            "permission_denied": "Permission denied",
            "invalid_format": "Invalid format",
            "file_not_found": "File not found",
            
            # Help Messages
            "help_title": "📖 Help & Documentation",
            "getting_started": "Getting Started",
            "command_examples": "Command Examples",
            "troubleshooting": "Troubleshooting",
            "support": "Support & Community",
            "documentation": "Documentation",
            
            # Prompts
            "enter_repository": "Enter repository (owner/repo)",
            "enter_pr_number": "Enter PR number",
            "select_option": "Select option",
            "confirm_action": "Confirm action",
            "choose_language": "Choose language",
            
            # Multi-language specific
            "language_changed": "Language changed to",
            "language_not_supported": "Language not supported",
            "translation_missing": "Translation missing",
            "locale_error": "Locale configuration error",
            
            # Enterprise features
            "enterprise_mode": "Enterprise Mode",
            "team_settings": "Team Settings",
            "organization_config": "Organization Configuration",
            "audit_log": "Audit Log",
            "compliance_check": "Compliance Check",
            "security_scan": "Security Scan"
        }
    
    def set_language(self, language_code: str) -> bool:
        """Set the current language"""
        if language_code in self.SUPPORTED_LANGUAGES:
            self.current_language = language_code
            logger.info(f"Language set to {self.SUPPORTED_LANGUAGES[language_code]['name']}")
            return True
        else:
            logger.warning(f"Language {language_code} not supported")
            return False
    
    def get_current_language(self) -> str:
        """Get current language code"""
        return self.current_language
    
    def get_language_info(self, language_code: Optional[str] = None) -> Dict[str, Any]:
        """Get information about a language"""
        lang = language_code or self.current_language
        return self.SUPPORTED_LANGUAGES.get(lang, self.SUPPORTED_LANGUAGES['en'])
    
    def translate(self, key: str, **kwargs) -> str:
        """Translate a key to the current language"""
        # Get translation from current language
        translation = self.translations.get(self.current_language, {}).get(key)
        
        # Fall back to English if translation not found
        if not translation:
            translation = self.translations.get('en', {}).get(key, key)
        
        # Replace placeholders if kwargs provided
        if kwargs:
            try:
                translation = translation.format(**kwargs)
            except (KeyError, ValueError) as e:
                logger.warning(f"Translation formatting failed for key '{key}': {e}")
        
        return translation
    
    def t(self, key: str, **kwargs) -> str:
        """Shorthand for translate method"""
        return self.translate(key, **kwargs)
    
    def get_supported_languages(self) -> Dict[str, Dict[str, str]]:
        """Get list of supported languages"""
        return self.SUPPORTED_LANGUAGES
    
    def list_languages(self) -> str:
        """Get formatted list of supported languages"""
        languages = []
        for code, info in self.SUPPORTED_LANGUAGES.items():
            current = " (current)" if code == self.current_language else ""
            languages.append(f"{info['flag']} {code}: {info['name']}{current}")
        
        return "\n".join(languages)
    
    def get_locale_info(self) -> Dict[str, Any]:
        """Get current locale information"""
        lang_info = self.get_language_info()
        
        try:
            # Try to set locale to get formatting info
            test_locale = locale.setlocale(locale.LC_ALL, lang_info['locale'])
            currency = locale.localeconv()
            
            return {
                'language': self.current_language,
                'language_name': lang_info['name'],
                'locale': lang_info['locale'],
                'flag': lang_info['flag'],
                'currency_symbol': currency.get('currency_symbol', '$'),
                'decimal_point': currency.get('decimal_point', '.'),
                'thousands_sep': currency.get('thousands_sep', ','),
                'date_format': self._get_date_format(),
                'time_format': self._get_time_format()
            }
        except locale.Error:
            # Fall back to default if locale setting fails
            return {
                'language': self.current_language,
                'language_name': lang_info['name'],
                'locale': lang_info['locale'],
                'flag': lang_info['flag'],
                'currency_symbol': '$',
                'decimal_point': '.',
                'thousands_sep': ',',
                'date_format': '%Y-%m-%d',
                'time_format': '%H:%M:%S'
            }
    
    def _get_date_format(self) -> str:
        """Get locale-specific date format"""
        formats = {
            'en': '%Y-%m-%d',
            'es': '%d/%m/%Y',
            'fr': '%d/%m/%Y',
            'de': '%d.%m.%Y',
            'it': '%d/%m/%Y',
            'pt': '%d/%m/%Y',
            'ru': '%d.%m.%Y',
            'zh': '%Y年%m月%d日',
            'ja': '%Y年%m月%d日',
            'ko': '%Y년 %m월 %d일',
            'hi': '%d/%m/%Y',
            'ar': '%d/%m/%Y'
        }
        return formats.get(self.current_language, '%Y-%m-%d')
    
    def _get_time_format(self) -> str:
        """Get locale-specific time format"""
        formats = {
            'en': '%H:%M:%S',
            'es': '%H:%M:%S',
            'fr': '%H:%M:%S',
            'de': '%H:%M:%S',
            'it': '%H:%M:%S',
            'pt': '%H:%M:%S',
            'ru': '%H:%M:%S',
            'zh': '%H:%M:%S',
            'ja': '%H:%M:%S',
            'ko': '%H:%M:%S',
            'hi': '%H:%M:%S',
            'ar': '%H:%M:%S'
        }
        return formats.get(self.current_language, '%H:%M:%S')
    
    def format_number(self, number: float, decimal_places: int = 2) -> str:
        """Format number according to current locale"""
        try:
            locale_info = self.get_locale_info()
            decimal_point = locale_info['decimal_point']
            thousands_sep = locale_info['thousands_sep']
            
            # Format the number
            formatted = f"{number:,.{decimal_places}f}"
            
            # Replace separators if different from default
            if decimal_point != '.':
                formatted = formatted.replace('.', '|DECIMAL|')
            if thousands_sep != ',':
                formatted = formatted.replace(',', thousands_sep)
            formatted = formatted.replace('|DECIMAL|', decimal_point)
            
            return formatted
        except Exception:
            return f"{number:.{decimal_places}f}"
    
    def format_currency(self, amount: float, currency_code: str = 'USD') -> str:
        """Format currency according to current locale"""
        try:
            locale_info = self.get_locale_info()
            symbol = locale_info['currency_symbol']
            
            # Currency symbols by code
            currency_symbols = {
                'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥',
                'CNY': '¥', 'INR': '₹', 'KRW': '₩', 'BRL': 'R$',
                'RUB': '₽', 'CAD': 'C$', 'AUD': 'A$', 'CHF': 'CHF',
                'SEK': 'kr', 'NOK': 'kr', 'DKK': 'kr', 'PLN': 'zł'
            }
            
            symbol = currency_symbols.get(currency_code, currency_code)
            formatted_amount = self.format_number(amount, 2)
            
            # Currency position by language
            prefix_languages = ['en', 'es', 'pt', 'fr']
            if self.current_language in prefix_languages:
                return f"{symbol}{formatted_amount}"
            else:
                return f"{formatted_amount} {symbol}"
                
        except Exception:
            return f"{amount:.2f} {currency_code}"
    
    def export_translations(self, language_code: str) -> Optional[Dict[str, str]]:
        """Export translations for a specific language"""
        return self.translations.get(language_code)
    
    def import_translations(self, language_code: str, translations: Dict[str, str]) -> bool:
        """Import translations for a specific language"""
        try:
            if language_code not in self.SUPPORTED_LANGUAGES:
                return False
            
            self.translations[language_code] = translations
            
            # Save to file
            translation_file = self.locale_dir / f'{language_code}.json'
            with open(translation_file, 'w', encoding='utf-8') as f:
                json.dump(translations, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Imported translations for {language_code}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import translations for {language_code}: {e}")
            return False

# Global instance
i18n = InternationalizationManager()