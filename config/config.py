#!/usr/bin/env python3
"""
Configuration management for Automated RC Release Workflow.
Uses Pydantic for validation and YAML for configuration files.
"""

import os
import re
from typing import List, Optional, Dict, Any, Union
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, validator, model_validator
from pydantic_settings import BaseSettings


class SlackConfig(BaseModel):
    """Slack integration configuration."""
    bot_token: str = Field(..., description="Slack bot token (xoxb-...)")
    signing_secret: str = Field(..., description="Slack app signing secret")
    app_token: Optional[str] = Field(None, description="Slack app token for Socket Mode (xapp-...)")
    default_channels: List[str] = Field(default=["#releases"], description="Default notification channels")

    @validator('bot_token')
    def validate_bot_token(cls, v):
        if not v.startswith('xoxb-'):
            raise ValueError('Bot token must start with xoxb-')
        return v

    @validator('app_token')
    def validate_app_token(cls, v):
        if v and not v.startswith('xapp-'):
            raise ValueError('App token must start with xapp-')
        return v


class GitHubConfig(BaseModel):
    """GitHub integration configuration."""
    token: str = Field(..., description="GitHub personal access token or app token")
    repo: str = Field(..., description="Repository in format owner/repo")
    api_url: str = Field(default="https://api.github.com", description="GitHub API base URL")

    @validator('repo')
    def validate_repo_format(cls, v):
        if not re.match(r'^[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+$', v):
            raise ValueError('Repository must be in format owner/repo')
        return v

    @validator('token')
    def validate_token(cls, v):
        if not v or len(v) < 10:
            raise ValueError('GitHub token must be provided and valid')
        return v


class OpenAIConfig(BaseModel):
    """OpenAI configuration."""
    api_key: str = Field(..., description="OpenAI API key")
    model: str = Field(default="gpt-4-1106-preview", description="OpenAI model to use")
    api_base: str = Field(default="https://api.openai.com/v1", description="OpenAI API base URL")
    max_tokens: int = Field(default=1000, description="Maximum tokens for responses")


class AzureOpenAIConfig(BaseModel):
    """Azure OpenAI configuration."""
    endpoint: str = Field(..., description="Azure OpenAI endpoint")
    api_key: str = Field(..., description="Azure OpenAI API key")
    api_version: str = Field(default="2023-12-01-preview", description="Azure OpenAI API version")
    deployment: str = Field(..., description="Azure OpenAI deployment name")


class AnthropicConfig(BaseModel):
    """Anthropic Claude configuration."""
    api_key: str = Field(..., description="Anthropic API key")
    model: str = Field(default="claude-3-sonnet-20240229", description="Anthropic model to use")


class AIConfig(BaseModel):
    """AI provider configuration."""
    provider: str = Field(default="openai", description="AI provider: openai, azure, anthropic")
    openai: Optional[OpenAIConfig] = None
    azure: Optional[AzureOpenAIConfig] = None
    anthropic: Optional[AnthropicConfig] = None

    @validator('provider')
    def validate_provider(cls, v):
        if v not in ['openai', 'azure', 'anthropic']:
            raise ValueError('Provider must be one of: openai, azure, anthropic')
        return v

    @model_validator(mode='after')
    def validate_provider_config(self):
        if self.provider == 'openai' and not self.openai:
            raise ValueError('OpenAI configuration required when provider is openai')
        elif self.provider == 'azure' and not self.azure:
            raise ValueError('Azure configuration required when provider is azure')
        elif self.provider == 'anthropic' and not self.anthropic:
            raise ValueError('Anthropic configuration required when provider is anthropic')
        return self


class OrganizationConfig(BaseModel):
    """Organization-specific configuration."""
    name: str = Field(default="Your Company", description="Organization name")
    default_service: str = Field(default="your-service", description="Default service name")
    timezone: str = Field(default="UTC", description="Default timezone")
    regions: List[str] = Field(default=["EUS", "SCUS", "WUS"], description="Deployment regions")


class AppConfig(BaseModel):
    """Application configuration."""
    environment: str = Field(default="development", description="Environment: development, staging, production")
    log_level: str = Field(default="INFO", description="Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL")
    deployment_mode: str = Field(default="socket", description="Deployment mode: socket, http")
    port: int = Field(default=3000, description="Server port for HTTP mode")
    output_dir: str = Field(default="output", description="Output directory for generated files")

    @validator('environment')
    def validate_environment(cls, v):
        if v not in ['development', 'staging', 'production']:
            raise ValueError('Environment must be one of: development, staging, production')
        return v

    @validator('log_level')
    def validate_log_level(cls, v):
        if v not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            raise ValueError('Log level must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL')
        return v

    @validator('deployment_mode')
    def validate_deployment_mode(cls, v):
        if v not in ['socket', 'http']:
            raise ValueError('Deployment mode must be one of: socket, http')
        return v


class ModalFieldConfig(BaseModel):
    """Configuration for individual modal fields."""
    required: bool = Field(default=True, description="Whether field is required")
    validation: Optional[str] = Field(None, description="Regex validation pattern")
    placeholder: Optional[str] = Field(None, description="Placeholder text")
    options: Optional[List[str]] = Field(None, description="Options for dropdown fields")
    default: Optional[str] = Field(None, description="Default value")
    type: str = Field(default="text", description="Field type: text, date, dropdown")
    description: Optional[str] = Field(None, description="Field description")


class ModalConfig(BaseModel):
    """Modal field configuration."""
    fields: Dict[str, ModalFieldConfig] = Field(
        default_factory=lambda: {
            "production_version": ModalFieldConfig(
                required=True,
                validation=r"^v?\d+\.\d+\.\d+$",
                placeholder="e.g., v1.2.3"
            ),
            "new_version": ModalFieldConfig(
                required=True,
                validation=r"^v?\d+\.\d+\.\d+$",
                placeholder="e.g., v1.3.0"
            ),
            "service_name": ModalFieldConfig(
                required=True,
                validation=r"^[a-z][a-z0-9-]*[a-z0-9]$",
                placeholder="e.g., cer-cart"
            ),
            "release_type": ModalFieldConfig(
                required=True,
                type="dropdown",
                options=["standard", "hotfix", "ebf"],
                default="standard"
            ),
            "rc_name": ModalFieldConfig(
                required=True,
                placeholder="Who's running the release"
            ),
            "rc_manager": ModalFieldConfig(
                required=True,
                placeholder="Who to escalate to"
            ),
            "day1_date": ModalFieldConfig(
                required=True,
                type="date",
                description="CRQ Day 1 (prep/setup)"
            ),
            "day2_date": ModalFieldConfig(
                required=True,
                type="date",
                description="CRQ Day 2 (actual release)"
            )
        }
    )


class CRQTemplateConfig(BaseModel):
    """CRQ template configuration matching the provided template."""
    summary_format: str = Field(
        default="{service_name} Application Code deployment for {platform} ({regions}) - {day_type}",
        description="Format string for CRQ summary"
    )
    description_questions: List[str] = Field(
        default=[
            "What is the criticality of change or why is this change required?",
            "How have we validated this change in the lower environment?",
            "What is the blast radius of this change?",
            "Describe how testing has reduced risk for the deployment?",
            "What happens if we encounter an issue during release?",
            "What controls do we have to minimize the impact to our customers?",
            "What monitoring is in place to determine the errors?"
        ],
        description="Standard questions for CRQ description section"
    )
    implementation_fields: List[str] = Field(
        default=[
            "Application Name", "Namespace", "Assembly", "Service name", "Platform",
            "Artifact Version", "Forward Artifact Version", "Rollback Artifact Version",
            "Confluence link"
        ],
        description="Required fields for implementation plan"
    )
    validation_dashboards: List[str] = Field(
        default=[
            "P0 Dashboard – Grafana Link", "L1 Dashboard – Grafana Link",
            "Services dashboard – Grafana Link", "WCNP - CPU - Memory – Link",
            "Istio/ SM: Link"
        ],
        description="Dashboard links for validation plan"
    )
    backout_fields: List[str] = Field(
        default=[
            "Application Name", "Namespace", "Assembly", "Service name", "Platform",
            "Artifact Version (Previous Version for rollback)", "Confluence link"
        ],
        description="Required fields for backout plan"
    )


class CRQConfig(BaseModel):
    """CRQ generation configuration."""
    template_fields: CRQTemplateConfig = Field(default_factory=CRQTemplateConfig)


class TemplateFormats(BaseModel):
    """Template output format configuration."""
    confluence: bool = Field(default=True, description="Generate Confluence markup")
    markdown: bool = Field(default=True, description="Generate Markdown")
    html: bool = Field(default=False, description="Generate HTML")
    plain_text: bool = Field(default=False, description="Generate plain text")


class TemplatesConfig(BaseModel):
    """Template configuration."""
    base_path: str = Field(default="templates", description="Base template directory")
    release_notes: str = Field(default="release_notes.j2", description="Release notes template")
    crq_template: str = Field(default="crq_template.j2", description="CRQ template")
    slack_message: str = Field(default="slack_message.j2", description="Slack message template")
    custom_path: Optional[str] = Field(None, description="Custom template directory override")
    formats: TemplateFormats = Field(default_factory=TemplateFormats)


class SecurityConfig(BaseModel):
    """Security and access control configuration."""
    allowed_users: List[str] = Field(default=[], description="Allowed Slack user IDs (empty = all)")
    allowed_channels: List[str] = Field(default=[], description="Allowed channel IDs (empty = all)")
    require_manager_approval: bool = Field(default=False, description="Require manager approval")


class MonitoringConfig(BaseModel):
    """Monitoring and alerting configuration."""
    webhook_url: Optional[str] = Field(None, description="Webhook URL for external monitoring")
    sentry_dsn: Optional[str] = Field(None, description="Sentry DSN for error tracking")
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")


class JiraIntegration(BaseModel):
    """JIRA integration configuration."""
    enabled: bool = Field(default=False)
    url: Optional[str] = None
    username: Optional[str] = None
    api_token: Optional[str] = None


class ServiceNowIntegration(BaseModel):
    """ServiceNow integration configuration."""
    enabled: bool = Field(default=False)
    instance: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class IntegrationsConfig(BaseModel):
    """External integrations configuration."""
    jira: JiraIntegration = Field(default_factory=JiraIntegration)
    servicenow: ServiceNowIntegration = Field(default_factory=ServiceNowIntegration)


class DashboardConfig(BaseModel):
    """Dashboard configuration for monitoring links."""
    # Direct dashboard URLs - users specify exactly what they want
    confluence_dashboard_url: str = Field(
        default="https://confluence.company.com/display/SERVICE/Dashboards",
        description="Direct URL to Confluence dashboard page"
    )
    p0_dashboard_url: str = Field(
        default="https://grafana.company.com/d/service-p0",
        description="Direct URL to P0 dashboard"
    )
    l1_dashboard_url: str = Field(
        default="https://grafana.company.com/d/service-l1", 
        description="Direct URL to L1 dashboard"
    )
    services_dashboard_url: str = Field(
        default="https://grafana.company.com/d/service-overview",
        description="Direct URL to services dashboard"
    )
    wcnp_dashboard_url: str = Field(
        default="https://grafana.company.com/d/service-wcnp",
        description="Direct URL to WCNP dashboard"
    )
    istio_dashboard_url: str = Field(
        default="https://grafana.company.com/d/service-istio",
        description="Direct URL to Istio dashboard"
    )

    def get_dashboard_urls(self) -> Dict[str, str]:
        """Get all dashboard URLs as a dictionary."""
        return {
            "confluence_dashboard_url": self.confluence_dashboard_url,
            "p0_dashboard_url": self.p0_dashboard_url,
            "l1_dashboard_url": self.l1_dashboard_url,
            "services_dashboard_url": self.services_dashboard_url,
            "wcnp_dashboard_url": self.wcnp_dashboard_url,
            "istio_dashboard_url": self.istio_dashboard_url
        }


class ExternalTemplateConfig(BaseModel):
    """External CRQ template configuration."""
    enabled: bool = Field(default=False, description="Enable external template download")
    template_url: Optional[str] = Field(None, description="URL to external CRQ template (Word doc, text file, etc.)")
    template_type: str = Field(default="auto", description="Template type: auto, word, text, markdown")
    cache_duration: int = Field(default=3600, description="Cache duration in seconds (1 hour default)")
    fallback_to_builtin: bool = Field(default=True, description="Fall back to built-in template if download fails")
    
    @validator('template_type')
    def validate_template_type(cls, v):
        if v not in ['auto', 'word', 'text', 'markdown', 'html']:
            raise ValueError('Template type must be one of: auto, word, text, markdown, html')
        return v


class Settings(BaseModel):
    """Main application settings."""
    slack: SlackConfig
    github: GitHubConfig
    ai: AIConfig
    organization: OrganizationConfig = Field(default_factory=OrganizationConfig)
    app: AppConfig = Field(default_factory=AppConfig)
    modal: ModalConfig = Field(default_factory=ModalConfig)
    crq: CRQConfig = Field(default_factory=CRQConfig)
    templates: TemplatesConfig = Field(default_factory=TemplatesConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    integrations: IntegrationsConfig = Field(default_factory=IntegrationsConfig)
    dashboard: DashboardConfig = Field(default_factory=DashboardConfig)
    external_template: ExternalTemplateConfig = Field(default_factory=ExternalTemplateConfig)


def substitute_env_vars(data: Any) -> Any:
    """Recursively substitute environment variables in configuration data."""
    if isinstance(data, dict):
        return {key: substitute_env_vars(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [substitute_env_vars(item) for item in data]
    elif isinstance(data, str):
        # Handle ${VAR} and ${VAR:default} patterns
        import re
        pattern = r'\$\{([^}:]+)(?::([^}]*))?\}'
        
        def replace_var(match):
            var_name = match.group(1)
            default_value = match.group(2) if match.group(2) is not None else ""
            return os.getenv(var_name, default_value)
        
        return re.sub(pattern, replace_var, data)
    else:
        return data


def load_config(config_path: Optional[Union[str, Path]] = None) -> Settings:
    """
    Load configuration from YAML file with environment variable substitution.
    
    Args:
        config_path: Path to configuration file. If None, looks for:
                    - config/settings.local.yaml (for local overrides)
                    - config/settings.yaml
                    - config/settings.example.yaml (fallback)
    
    Returns:
        Settings instance with validated configuration.
        
    Raises:
        FileNotFoundError: If no configuration file is found.
        ValidationError: If configuration is invalid.
    """
    if config_path is None:
        # Look for configuration files in order of preference
        possible_paths = [
            Path("config/settings.local.yaml"),
            Path("config/settings.yaml"),
            Path("config/settings.example.yaml")
        ]
        
        config_path = None
        for path in possible_paths:
            if path.exists():
                config_path = path
                break
        
        if config_path is None:
            raise FileNotFoundError(
                "No configuration file found. Please create config/settings.yaml "
                "or copy config/settings.example.yaml to config/settings.yaml"
            )
    
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    # Load and parse YAML
    with open(config_path, 'r') as f:
        raw_config = yaml.safe_load(f)
    
    # Substitute environment variables
    processed_config = substitute_env_vars(raw_config)
    
    # Validate with Pydantic
    try:
        return Settings(**processed_config)
    except Exception as e:
        raise ValueError(f"Configuration validation failed: {e}")


def validate_modal_input(field_name: str, value: str, field_config: ModalFieldConfig) -> tuple[bool, Optional[str]]:
    """
    Validate modal input against field configuration.
    
    Args:
        field_name: Name of the field being validated
        value: Input value to validate
        field_config: Field configuration
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check required fields
    if field_config.required and not value.strip():
        return False, f"{field_name} is required"
    
    # Check regex validation
    if field_config.validation and value:
        if not re.match(field_config.validation, value):
            return False, f"{field_name} format is invalid. Expected format: {field_config.placeholder or 'see field description'}"
    
    # Check dropdown options
    if field_config.options and value not in field_config.options:
        return False, f"{field_name} must be one of: {', '.join(field_config.options)}"
    
    return True, None


# Global configuration instance (loaded on import)
try:
    config = load_config()
except (FileNotFoundError, ValueError) as e:
    # In development/testing, we might not have a config file yet
    import warnings
    warnings.warn(f"Could not load configuration: {e}")
    config = None 