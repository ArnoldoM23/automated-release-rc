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
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import BaseSettings


class SlackConfig(BaseModel):
    """Slack integration configuration."""
    bot_token: str = Field(..., description="Slack bot token (xoxb-...)")
    signing_secret: str = Field(..., description="Slack app signing secret")
    app_token: Optional[str] = Field(None, description="Slack app token for Socket Mode (xapp-...)")
    default_channels: List[str] = Field(default=["#releases"], description="Default notification channels")

    @field_validator('bot_token')
    @classmethod
    def validate_bot_token(cls, v):
        if not v.startswith('xoxb-'):
            raise ValueError('Bot token must start with xoxb-')
        return v

    @field_validator('app_token')
    @classmethod
    def validate_app_token(cls, v):
        if v and not v.startswith('xapp-'):
            raise ValueError('App token must start with xapp-')
        return v


class GitHubConfig(BaseModel):
    """GitHub integration configuration."""
    token: str = Field(..., description="GitHub personal access token or app token")
    repo: str = Field(..., description="Repository in format owner/repo")
    api_url: str = Field(default="https://api.github.com", description="GitHub API base URL")

    @field_validator('repo')
    @classmethod
    def validate_repo_format(cls, v):
        if not re.match(r'^[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+$', v):
            raise ValueError('Repository must be in format owner/repo')
        return v

    @field_validator('token')
    @classmethod
    def validate_token(cls, v):
        # Allow dummy token for testing/development
        if v == "dummy-token-for-testing":
            return v
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

    @field_validator('provider')
    @classmethod
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


class LLMConfig(BaseModel):
    """Version 3.0 LLM configuration for enhanced AI features."""
    provider: str = Field(default="walmart_sandbox", description="LLM provider: walmart_sandbox, openai, anthropic")
    model: str = Field(default="gpt-4o-mini", description="Model to use")
    api_key: Optional[str] = Field(None, description="API key for the LLM provider")
    gateway_url: Optional[str] = Field(None, description="Gateway URL for Walmart LLM")
    enabled: bool = Field(default=True, description="Enable LLM features")
    fallback_enabled: bool = Field(default=True, description="Use fallback logic if LLM fails")
    cache_duration: int = Field(default=3600, description="Cache duration in seconds")
    max_tokens: int = Field(default=2000, description="Maximum tokens for responses")
    temperature: float = Field(default=0.1, description="Temperature for response generation")
    require_llm_for_crq: bool = Field(default=False, description="Require LLM for CRQ generation")
    cache_summaries: bool = Field(default=True, description="Cache summaries to reduce API calls")
    
    # v4.0 Multi-provider API key support
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(None, description="Anthropic API key") 
    walmart_api_key: Optional[str] = Field(None, description="Walmart LLM API key")

    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v):
        if v not in ['walmart_sandbox', 'openai', 'anthropic']:
            raise ValueError('Provider must be one of: walmart_sandbox, openai, anthropic')
        return v

    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v):
        if v < 0.0 or v > 2.0:
            raise ValueError('Temperature must be between 0.0 and 2.0')
        return v


class OrganizationConfig(BaseModel):
    """Organization-specific configuration."""
    name: str = Field(default="Your Company", description="Organization name")
    default_service: str = Field(default="your-service", description="Default service name")
    timezone: str = Field(default="UTC", description="Default timezone")
    regions: List[str] = Field(default=["EUS", "SCUS", "WUS"], description="Deployment regions")
    platform: str = Field(default="Glass", description="Platform type")
    
    # Release team defaults (optional)
    idc_captain: Optional[str] = Field(default=None, description="IDC Release Captain")
    idc_engineer: Optional[str] = Field(default=None, description="IDC Release Engineer")
    us_captain: Optional[str] = Field(default=None, description="US Release Captain")
    us_engineer: Optional[str] = Field(default=None, description="US Release Engineer")
    
    # International and tenant labels configuration
    international_labels: List[str] = Field(
        default=["international", "i18n", "localization", "locale", "tenant", "multi-tenant"],
        description="List of labels that identify international or tenant-related PRs"
    )


class AppConfig(BaseModel):
    """Application configuration."""
    environment: str = Field(default="development", description="Environment: development, staging, production")
    log_level: str = Field(default="INFO", description="Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL")
    deployment_mode: str = Field(default="socket", description="Deployment mode: socket, http")
    port: int = Field(default=3000, description="Server port for HTTP mode")
    output_dir: str = Field(default="output", description="Output directory for generated files")

    @field_validator('environment')
    @classmethod
    def validate_environment(cls, v):
        if v not in ['development', 'staging', 'production']:
            raise ValueError('Environment must be one of: development, staging, production')
        return v

    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v):
        if v not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            raise ValueError('Log level must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL')
        return v

    @field_validator('deployment_mode')
    @classmethod
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
    
    @field_validator('template_type')
    @classmethod
    def validate_template_type(cls, v):
        if v not in ['auto', 'word', 'text', 'markdown', 'html']:
            raise ValueError('Template type must be one of: auto, word, text, markdown, html')
        return v


class Settings(BaseModel):
    """Main application settings."""
    slack: SlackConfig
    github: GitHubConfig
    ai: AIConfig
    llm: LLMConfig = Field(default_factory=LLMConfig)  # Version 3.0 LLM configuration
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


def load_config(config_path: Optional[Union[str, Path]] = None, allow_missing_token: bool = False) -> Settings:
    """
    Load configuration from YAML file with environment variable substitution.
    v4.0 Enhancement: All secrets come from environment variables, YAML contains system config only.
    
    Args:
        config_path: Path to configuration file. If None, looks for:
                    - config/settings.local.yaml (for local overrides)
                    - config/settings.yaml
                    - config/settings.example.yaml (fallback)
        allow_missing_token: If True, allows missing GitHub token for testing/development
    
    Returns:
        Settings instance with validated configuration.
        
    Raises:
        FileNotFoundError: If no configuration file is found.
        ValidationError: If configuration is invalid.
    """
    if config_path is None:
        # Look for configuration files in order of preference
        possible_paths = [
            Path("src/config/settings.local.yaml"),
            Path("src/config/settings.yaml"),
            Path("src/config/settings.example.yaml")
        ]
        
        config_path = None
        for path in possible_paths:
            if path.exists():
                config_path = path
                break
        
        if config_path is None:
            raise FileNotFoundError(
                "No configuration file found. Please create src/config/settings.yaml "
                "or copy src/config/settings.example.yaml to src/config/settings.yaml"
            )
    
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    # Load and parse YAML
    with open(config_path, 'r') as f:
        raw_config = yaml.safe_load(f)
    
    # Substitute environment variables
    processed_config = substitute_env_vars(raw_config)
    
    # v4.0 Enhancement: Inject environment variables for secrets
    # GitHub Configuration
    if 'github' not in processed_config:
        processed_config['github'] = {}
    processed_config['github']['token'] = os.getenv('GITHUB_TOKEN', 'dummy-token-for-testing' if allow_missing_token else '')
    processed_config['github']['repo'] = os.getenv('GITHUB_REPO', 'ArnoldoM23/PerfCopilot')
    
    # Slack Configuration
    if 'slack' not in processed_config:
        processed_config['slack'] = {}
    processed_config['slack']['bot_token'] = os.getenv('SLACK_BOT_TOKEN', 'xoxb-000000000000-000000000000-placeholder-for-testing' if allow_missing_token else 'xoxb-missing-token')
    processed_config['slack']['signing_secret'] = os.getenv('SLACK_SIGNING_SECRET', 'placeholder-signing-secret' if allow_missing_token else 'missing-secret')
    processed_config['slack']['app_token'] = os.getenv('SLACK_APP_TOKEN', '')
    
    # LLM Configuration (v3.0/v4.0)
    if 'llm' not in processed_config:
        processed_config['llm'] = {}
    processed_config['llm']['api_key'] = os.getenv('WMT_LLM_API_KEY', 'dummy-llm-key' if allow_missing_token else '')
    processed_config['llm']['gateway_url'] = os.getenv('WMT_LLM_API_URL', 'https://llm-internal.walmart.com/gateway')
    
    # Store all API keys for multi-provider support (v4.0 enhancement)
    processed_config['llm']['openai_api_key'] = os.getenv('OPENAI_API_KEY', 'dummy-openai-key' if allow_missing_token else 'sk-missing-key')
    processed_config['llm']['anthropic_api_key'] = os.getenv('ANTHROPIC_API_KEY', 'dummy-anthropic-key' if allow_missing_token else '')
    processed_config['llm']['walmart_api_key'] = os.getenv('WMT_LLM_API_KEY', 'dummy-llm-key' if allow_missing_token else '')
    
    # AI Configuration (Legacy)
    if 'ai' not in processed_config:
        processed_config['ai'] = {}
    if 'openai' not in processed_config['ai']:
        processed_config['ai']['openai'] = {}
    processed_config['ai']['openai']['api_key'] = os.getenv('OPENAI_API_KEY', 'dummy-openai-key' if allow_missing_token else 'sk-missing-key')
    
    # Azure OpenAI Configuration
    if 'azure' not in processed_config['ai']:
        processed_config['ai']['azure'] = {}
    processed_config['ai']['azure']['api_key'] = os.getenv('AZURE_OPENAI_API_KEY', 'dummy-azure-key' if allow_missing_token else '')
    processed_config['ai']['azure']['endpoint'] = os.getenv('AZURE_OPENAI_ENDPOINT', 'https://your-instance.openai.azure.com')
    processed_config['ai']['azure']['deployment'] = os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4')
    
    # Anthropic Configuration
    if 'anthropic' not in processed_config['ai']:
        processed_config['ai']['anthropic'] = {}
    processed_config['ai']['anthropic']['api_key'] = os.getenv('ANTHROPIC_API_KEY', 'dummy-anthropic-key' if allow_missing_token else '')
    
    # Handle missing GitHub token gracefully for development/testing
    if allow_missing_token and not processed_config.get('github', {}).get('token'):
        # Provide a dummy token for development/testing
        if 'github' not in processed_config:
            processed_config['github'] = {}
        processed_config['github']['token'] = 'dummy-token-for-testing'
    
    # Validate with Pydantic
    try:
        return Settings(**processed_config)
    except Exception as e:
        # Enhanced error message for GitHub token issues
        if "GitHub token must be provided and valid" in str(e):
            raise ValueError(
                f"GitHub token configuration error: {e}\n\n"
                "v4.0 Configuration Setup:\n"
                "1. Create .rc_env_checkout.sh from template\n"
                "2. Set your GitHub token:\n"
                "   export GITHUB_TOKEN='your-token-here'\n"
                "3. Source the environment file:\n"
                "   source .rc_env_checkout.sh\n\n"
                "To get a GitHub token:\n"
                "   - Go to https://github.com/settings/tokens\n"
                "   - Click 'Generate new token (classic)'\n"
                "   - Select 'repo' scope for private repos or 'public_repo' for public repos\n"
                "   - Copy the token (starts with 'ghp_' or 'github_pat_')\n\n"
                "For testing/development without a token, use load_config(allow_missing_token=True)"
            )
        else:
            raise ValueError(f"Configuration validation failed: {e}")


def load_config_safe() -> Optional[Settings]:
    """
    Load configuration safely without raising exceptions.
    
    Returns:
        Settings instance if successful, None if configuration cannot be loaded.
    """
    try:
        return load_config(allow_missing_token=True)
    except Exception as e:
        import warnings
        warnings.warn(
            f"Configuration could not be loaded: {e}\n"
            "This is expected during development/testing when GitHub token is not set.",
            UserWarning
        )
        return None


# Global configuration instance (loaded on import with safe loading)
config = load_config_safe()


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


def extract_service_name_from_repo(repo_url: str) -> str:
    """
    Extract service name from GitHub repository URL.
    
    Args:
        repo_url: Repository URL in format "owner/repo-name"
        
    Returns:
        Service name extracted from repo name
    """
    try:
        # Handle both full URLs and owner/repo format
        if "/" in repo_url:
            repo_name = repo_url.split("/")[-1]
        else:
            repo_name = repo_url
            
        # Remove common prefixes and clean up name
        service_name = repo_name.lower()
        
        # Remove common prefixes
        prefixes_to_remove = ["service-", "app-", "api-", "microservice-"]
        for prefix in prefixes_to_remove:
            if service_name.startswith(prefix):
                service_name = service_name[len(prefix):]
                break
                
        return service_name
    except Exception:
        return "unknown-service" 