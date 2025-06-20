#!/usr/bin/env python3
"""
Configuration Manager
====================

Manages configuration loading, validation, and environment variable handling.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml
from dataclasses import dataclass, field


@dataclass
class ResearchConfig:
    """Research-specific configuration"""
    interests: List[str] = field(default_factory=list)
    arxiv_categories: List[str] = field(default_factory=list)
    boost_keywords: List[str] = field(default_factory=list)
    exclude_keywords: List[str] = field(default_factory=list)
    max_papers_per_day: int = 50
    days_back: int = 1
    min_relevance_score: float = 0.3
    min_significance_score: float = 0.4


@dataclass
class ScheduleConfig:
    """Scheduling configuration"""
    daily_digest_enabled: bool = True
    daily_digest_time: str = "09:00"
    weekly_summary_enabled: bool = True
    weekly_summary_day: str = "Monday"
    weekly_summary_time: str = "08:00"
    monitoring_enabled: bool = False
    monitoring_interval_hours: int = 4
    timezone: str = "UTC"


@dataclass
class OutputConfig:
    """Output configuration"""
    directory: str = "output"
    html: bool = True
    markdown: bool = True
    json: bool = True
    email: bool = True
    filename_pattern: str = "digest_{date}_{time}"


@dataclass
class EmailConfig:
    """Email notification configuration"""
    enabled: bool = False
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    username: str = ""
    password: str = ""
    from_email: str = ""
    recipients: List[str] = field(default_factory=list)
    subject_template: str = "🔬 AI Research Digest - {date}"


@dataclass
class DiscordConfig:
    """Discord notification configuration"""
    enabled: bool = False
    webhook_url: str = ""
    mention_role: str = ""


@dataclass
class ClaudeConfig:
    """Claude Code SDK configuration"""
    working_directory: str = ""
    max_turns: int = 3
    max_thinking_tokens: int = 8000
    permission_mode: str = "acceptEdits"
    batch_size: int = 5
    timeout_seconds: int = 300
    retry_attempts: int = 2


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    main_log_file: str = "logs/agent.log"
    error_log_file: str = "logs/errors.log"
    max_size_mb: int = 10
    backup_count: int = 5
    console_enabled: bool = True
    console_level: str = "INFO"


class ConfigManager:
    """Manages application configuration with environment variable support"""
    
    def __init__(self, config_path: str = None):
        self.config_path = Path(config_path or "config/config.yaml")
        self.logger = logging.getLogger(__name__)
        self._config: Dict[str, Any] = {}
        
        # Load configuration
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file with environment variable substitution"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Substitute environment variables
                content = self._substitute_env_vars(content)
                
                # Parse YAML
                self._config = yaml.safe_load(content) or {}
                self.logger.info(f"Loaded configuration from {self.config_path}")
            else:
                self.logger.warning(f"Config file not found: {self.config_path}, using defaults")
                self._config = self._get_default_config()
            
            # Validate configuration
            self._validate_config()
            
            return self._config
            
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            self._config = self._get_default_config()
            return self._config
    
    def _substitute_env_vars(self, content: str) -> str:
        """Substitute environment variables in configuration content"""
        import re
        
        # Pattern to match ${VAR_NAME} or ${VAR_NAME:default_value}
        pattern = r'\$\{([^}:]+)(?::([^}]*))?\}'
        
        def replace_var(match):
            var_name = match.group(1)
            default_value = match.group(2) if match.group(2) is not None else ""
            return os.getenv(var_name, default_value)
        
        return re.sub(pattern, replace_var, content)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'research': {
                'interests': ["Large Language Models", "AI Agents", "Machine Learning"],
                'arxiv_categories': ["cs.AI", "cs.LG", "cs.CL"],
                'boost_keywords': ["breakthrough", "novel", "state-of-the-art"],
                'exclude_keywords': ["survey", "review"],
                'filters': {
                    'max_papers_per_day': 50,
                    'days_back': 1,
                    'min_relevance_score': 0.3,
                    'min_significance_score': 0.4
                }
            },
            'schedule': {
                'daily_digest': {
                    'enabled': True,
                    'time': '09:00',
                    'timezone': 'UTC'
                }
            },
            'output': {
                'directory': 'output',
                'formats': {
                    'html': True,
                    'markdown': True,
                    'json': True,
                    'email': True
                }
            },
            'claude': {
                'options': {
                    'max_turns': 3,
                    'max_thinking_tokens': 8000,
                    'permission_mode': 'acceptEdits'
                }
            },
            'logging': {
                'level': 'INFO',
                'console': {'enabled': True}
            }
        }
    
    def _validate_config(self):
        """Validate configuration values"""
        # Validate research interests
        interests = self.get('research.interests', [])
        if not interests:
            self.logger.warning("No research interests defined")
        
        # Validate schedule times
        daily_time = self.get('schedule.daily_digest.time', '09:00')
        if not self._is_valid_time(daily_time):
            self.logger.error(f"Invalid daily digest time: {daily_time}")
            self.set('schedule.daily_digest.time', '09:00')
        
        # Validate output directory
        output_dir = Path(self.get('output.directory', 'output'))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Validate log directory
        log_dir = Path(self.get('logging.files.main', 'logs/agent.log')).parent
        log_dir.mkdir(parents=True, exist_ok=True)
    
    def _is_valid_time(self, time_str: str) -> bool:
        """Validate time format HH:MM"""
        try:
            from datetime import datetime
            datetime.strptime(time_str, '%H:%M')
            return True
        except ValueError:
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'research.interests')"""
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self._config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    def get_research_config(self) -> ResearchConfig:
        """Get research configuration as dataclass"""
        research_data = self.get('research', {})
        filters = research_data.get('filters', {})
        
        return ResearchConfig(
            interests=research_data.get('interests', []),
            arxiv_categories=research_data.get('arxiv_categories', []),
            boost_keywords=research_data.get('boost_keywords', []),
            exclude_keywords=research_data.get('exclude_keywords', []),
            max_papers_per_day=filters.get('max_papers_per_day', 50),
            days_back=filters.get('days_back', 1),
            min_relevance_score=filters.get('min_relevance_score', 0.3),
            min_significance_score=filters.get('min_significance_score', 0.4)
        )
    
    def get_schedule_config(self) -> ScheduleConfig:
        """Get schedule configuration as dataclass"""
        daily = self.get('schedule.daily_digest', {})
        weekly = self.get('schedule.weekly_summary', {})
        monitoring = self.get('schedule.monitoring', {})
        
        return ScheduleConfig(
            daily_digest_enabled=daily.get('enabled', True),
            daily_digest_time=daily.get('time', '09:00'),
            weekly_summary_enabled=weekly.get('enabled', True),
            weekly_summary_day=weekly.get('day', 'Monday'),
            weekly_summary_time=weekly.get('time', '08:00'),
            monitoring_enabled=monitoring.get('enabled', False),
            monitoring_interval_hours=monitoring.get('interval_hours', 4),
            timezone=daily.get('timezone', 'UTC')
        )
    
    def get_output_config(self) -> OutputConfig:
        """Get output configuration as dataclass"""
        output_data = self.get('output', {})
        formats = output_data.get('formats', {})
        
        return OutputConfig(
            directory=output_data.get('directory', 'output'),
            html=formats.get('html', True),
            markdown=formats.get('markdown', True),
            json=formats.get('json', True),
            email=formats.get('email', True),
            filename_pattern=output_data.get('filename_pattern', 'digest_{date}_{time}')
        )
    
    def get_email_config(self) -> EmailConfig:
        """Get email configuration as dataclass"""
        email_data = self.get('notifications.email', {})
        smtp_data = email_data.get('smtp', {})
        
        return EmailConfig(
            enabled=email_data.get('enabled', False),
            smtp_server=smtp_data.get('server', 'smtp.gmail.com'),
            smtp_port=smtp_data.get('port', 587),
            username=smtp_data.get('username', ''),
            password=smtp_data.get('password', ''),
            from_email=smtp_data.get('from_email', ''),
            recipients=email_data.get('recipients', []),
            subject_template=email_data.get('subject_template', '🔬 AI Research Digest - {date}')
        )
    
    def get_discord_config(self) -> DiscordConfig:
        """Get Discord configuration as dataclass"""
        discord_data = self.get('notifications.discord', {})
        
        return DiscordConfig(
            enabled=discord_data.get('enabled', False),
            webhook_url=discord_data.get('webhook_url', ''),
            mention_role=discord_data.get('mention_role', '')
        )
    
    def get_claude_config(self) -> ClaudeConfig:
        """Get Claude configuration as dataclass"""
        claude_data = self.get('claude', {})
        options = claude_data.get('options', {})
        analysis = claude_data.get('analysis', {})
        
        return ClaudeConfig(
            working_directory=claude_data.get('working_directory', ''),
            max_turns=options.get('max_turns', 3),
            max_thinking_tokens=options.get('max_thinking_tokens', 8000),
            permission_mode=options.get('permission_mode', 'acceptEdits'),
            batch_size=analysis.get('batch_size', 5),
            timeout_seconds=analysis.get('timeout_seconds', 300),
            retry_attempts=analysis.get('retry_attempts', 2)
        )
    
    def get_logging_config(self) -> LoggingConfig:
        """Get logging configuration as dataclass"""
        logging_data = self.get('logging', {})
        files = logging_data.get('files', {})
        rotation = logging_data.get('rotation', {})
        console = logging_data.get('console', {})
        
        return LoggingConfig(
            level=logging_data.get('level', 'INFO'),
            main_log_file=files.get('main', 'logs/agent.log'),
            error_log_file=files.get('errors', 'logs/errors.log'),
            max_size_mb=rotation.get('max_size_mb', 10),
            backup_count=rotation.get('backup_count', 5),
            console_enabled=console.get('enabled', True),
            console_level=console.get('level', 'INFO')
        )
    
    def save_config(self, output_path: str = None):
        """Save current configuration to file"""
        output_file = Path(output_path or self.config_path)
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                yaml.dump(self._config, f, default_flow_style=False, indent=2)
            
            self.logger.info(f"Configuration saved to {output_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
    
    def update_from_env(self):
        """Update configuration from environment variables"""
        env_mappings = {
            'ARXIV_AGENT_EMAIL_USERNAME': 'notifications.email.smtp.username',
            'ARXIV_AGENT_EMAIL_PASSWORD': 'notifications.email.smtp.password',
            'ARXIV_AGENT_EMAIL_FROM': 'notifications.email.smtp.from_email',
            'ARXIV_AGENT_DISCORD_WEBHOOK': 'notifications.discord.webhook_url',
            'ANTHROPIC_API_KEY': 'claude.api_key',
            'ARXIV_AGENT_LOG_LEVEL': 'logging.level'
        }
        
        for env_var, config_key in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                self.set(config_key, value)
                self.logger.debug(f"Updated {config_key} from environment variable {env_var}")


# Example usage and configuration validation
def main():
    """Example usage of ConfigManager"""
    import sys
    
    # Setup basic logging
    logging.basicConfig(level=logging.INFO)
    
    # Load configuration
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/config.yaml"
    config = ConfigManager(config_path)
    
    # Print configuration summary
    research_config = config.get_research_config()
    schedule_config = config.get_schedule_config()
    
    print("Configuration Summary:")
    print(f"  Research interests: {len(research_config.interests)}")
    print(f"  Daily digest: {schedule_config.daily_digest_time}")
    print(f"  Output formats: HTML={config.get('output.formats.html')}, MD={config.get('output.formats.markdown')}")
    
    # Test environment variable substitution
    print(f"  API Key set: {'Yes' if os.getenv('ANTHROPIC_API_KEY') else 'No'}")


if __name__ == "__main__":
    main()