# ⚙️ Configuration Reference

**Complete guide to configuring the RC Release Automation Agent**

---

## 📋 **Configuration Overview**

The RC Release Automation Agent uses YAML configuration files for customization. This allows you to:
- Customize organization-specific settings
- Configure AI providers and models
- Set up GitHub enterprise integration
- Define regional deployment clusters
- Customize output templates and branding

**Main Configuration File:** `config/settings.yaml`

---

## 🏢 **Organization Settings**

Configure your organization's specific details:

```yaml
organization:
  name: "Your Company Name"
  platform: "Azure"  # Azure, AWS, GCP
  regions: ["EUS", "SCUS", "WUS", "NEU", "SEA"]
  
  # Release team defaults
  idc_captain: "Release Team Lead"
  idc_engineer: "IDC Release Engineer"  
  us_captain: "US Release Manager"
  us_engineer: "US Release Engineer"
  
  # Environment settings
  environments:
    - name: "staging"
      url: "https://staging.yourcompany.com"
    - name: "pre-prod"
      url: "https://preprod.yourcompany.com"
    - name: "production"
      url: "https://www.yourcompany.com"
  
  # Dashboard URLs
  dashboards:
    grafana: "https://grafana.yourcompany.com/d"
    datadog: "https://app.datadoghq.com/apm/services"
    azure_insights: "https://portal.azure.com/#view/AppInsights"
    alerts: "https://alerts.yourcompany.com"
```

---

## 🔗 **GitHub Integration**

Configure GitHub API access and repository settings:

```yaml
github:
  # Repository configuration
  repo: "your-org/your-repo"
  base_url: "https://api.github.com"  # For GitHub Enterprise: https://github.yourcompany.com/api/v3
  
  # Branch configuration
  default_branch: "main"
  release_branch_pattern: "release/*"
  
  # PR filtering
  pr_filters:
    ignore_labels: ["dependabot", "automated", "skip-release"]
    require_labels: []  # Optional: only include PRs with these labels
    
  # Enterprise features
  enterprise:
    enabled: false
    saml_sso: false
    advanced_security: false
```

**Environment Variables:**
```bash
# Required
GITHUB_TOKEN="ghp_your_personal_access_token"

# Optional for GitHub Enterprise
GITHUB_ENTERPRISE_URL="https://github.yourcompany.com"
```

---

## 🤖 **AI Provider Configuration**

Configure multiple AI providers with automatic fallback:

```yaml
ai:
  # Provider priority order (will try in this order)
  providers: ["openai", "azure_openai", "anthropic"]
  
  # Enable/disable AI features
  enabled: true
  fallback_enabled: true
  timeout: 30  # seconds
  
  # OpenAI Configuration
  openai:
    model: "gpt-4-1106-preview"
    max_tokens: 2000
    temperature: 0.3
    
  # Azure OpenAI Configuration  
  azure_openai:
    model: "gpt-4"
    deployment_name: "gpt-4-deployment"
    api_version: "2024-02-15-preview"
    
  # Anthropic Configuration
  anthropic:
    model: "claude-3-sonnet-20240229"
    max_tokens: 2000
    temperature: 0.3
```

**Environment Variables:**
```bash
# OpenAI
OPENAI_API_KEY="sk-your_openai_key"

# Azure OpenAI
AZURE_OPENAI_API_KEY="your_azure_key"
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"

# Anthropic
ANTHROPIC_API_KEY="your_anthropic_key"
```

---

## 📝 **Template Configuration**

Customize document generation templates:

```yaml
templates:
  # Release notes configuration
  release_notes:
    template_file: "templates/release_notes.j2"
    include_sections:
      - "deployment_crq"
      - "schema_changes"
      - "feature_bugfixes"
      - "international_changes"
      - "ccm_updates"
      - "rollback_info"
    
    # Custom field mappings
    custom_fields:
      artifact_channel: "#your-release-channel"
      deployment_windows:
        day1_time: "09:00 PST"
        day2_time: "09:00 PST"
  
  # CRQ template configuration
  crq:
    template_file: "templates/crq_template.j2"
    risk_assessment: true
    include_rollback_plan: true
    
    # CRQ categories
    categories:
      standard: "Standard Change"
      emergency: "Emergency Change"
      normal: "Normal Change"
```

---

## 🚀 **Deployment Configuration**

Configure deployment-specific settings:

```yaml
deployment:
  # Cluster configuration
  clusters:
    - name: "EUS"
      region: "East US"
      environment: "production"
      notes: "Primary production cluster"
      
    - name: "SCUS"  
      region: "South Central US"
      environment: "production"
      notes: "Secondary production cluster"
      
    - name: "WUS"
      region: "West US"
      environment: "production" 
      notes: "Tertiary production cluster"
  
  # Deployment windows
  windows:
    standard:
      day1: "09:00-17:00 PST"
      day2: "09:00-12:00 PST"
    emergency:
      any_time: true
      approval_required: true
      
  # Validation requirements
  validation:
    required_approvals: 2
    automated_tests: true
    manual_testing: true
    performance_validation: true
```

---

## 📊 **Logging Configuration**

Configure structured logging and observability:

```yaml
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  format: "json"  # json, text
  
  # Output destinations
  outputs:
    console: true
    file: 
      enabled: true
      path: "logs/release_automation.log"
      max_size: "10MB"
      backup_count: 5
      
  # Structured logging fields
  include_fields:
    - "timestamp"
    - "level" 
    - "service_name"
    - "version"
    - "pr_count"
    - "execution_time"
```

---

## 🔧 **Feature Flags**

Enable/disable specific features:

```yaml
features:
  # Core features
  ai_content_generation: true
  github_pr_fetching: true
  confluence_output: true
  markdown_output: true
  
  # Advanced features
  schema_change_detection: true
  international_pr_detection: true
  ccm_integration: false
  jira_integration: false
  
  # Experimental features
  automated_testing: false
  slack_notifications: false
  approval_workflows: false
```

---

## 📈 **Performance Configuration**

Optimize performance for your environment:

```yaml
performance:
  # API rate limiting
  github_api:
    requests_per_second: 10
    max_concurrent: 5
    
  ai_api:
    requests_per_second: 2
    retry_attempts: 3
    backoff_factor: 2
    
  # Caching
  cache:
    enabled: true
    ttl: 300  # seconds
    max_size: 100  # number of entries
    
  # Processing limits
  max_prs_per_release: 100
  max_file_size: "10MB"
  timeout_seconds: 300
```

---

## 🔒 **Security Configuration**

Configure security and compliance settings:

```yaml
security:
  # Data handling
  sensitive_data:
    mask_user_emails: true
    mask_api_keys: true
    include_audit_trail: true
    
  # Access control
  access_control:
    required_team_membership: "release-team"
    allowed_repositories: ["your-org/*"]
    
  # Compliance
  compliance:
    gdpr_compliant: true
    data_retention_days: 90
    audit_logging: true
```

---

## 🌍 **Multi-Environment Configuration**

Configure different settings per environment:

```yaml
# Development environment
development:
  github:
    repo: "your-org/your-repo-dev"
  ai:
    enabled: false  # Use fallback content in dev
  logging:
    level: "DEBUG"

# Staging environment  
staging:
  github:
    repo: "your-org/your-repo-staging"
  ai:
    providers: ["openai"]  # Single provider for staging
  features:
    experimental_features: true

# Production environment
production:
  github:
    repo: "your-org/your-repo"
  ai:
    providers: ["openai", "azure_openai", "anthropic"]
  logging:
    level: "INFO"
  security:
    audit_logging: true
```

---

## 📋 **Configuration Validation**

Test your configuration:

```bash
# Validate configuration file
python test_cli.py --test-config

# Test with specific config file
python test_cli.py --test-config --config-path config/production.yaml

# Validate all features
python test_cli.py --test-all
```

**Configuration Schema Validation:**
The system automatically validates your configuration against the expected schema and will show helpful error messages for any issues.

---

## 🔄 **Configuration Migration**

When updating to newer versions:

1. **Backup current config:**
   ```bash
   cp config/settings.yaml config/settings.backup.yaml
   ```

2. **Update configuration:**
   ```bash
   # Compare with new example
   diff config/settings.yaml config/settings.example.yaml
   
   # Add new required fields
   # Update deprecated settings
   ```

3. **Validate changes:**
   ```bash
   python test_cli.py --test-config
   ```

---

## 📚 **Configuration Examples**

### **Small Team Setup**
```yaml
organization:
  name: "Startup Inc"
  regions: ["US-EAST"]
  
github:
  repo: "startup/main-app"
  
ai:
  providers: ["openai"]
  
features:
  ai_content_generation: true
  github_pr_fetching: true
```

### **Enterprise Setup**
```yaml
organization:
  name: "Enterprise Corp"
  platform: "Azure"
  regions: ["EUS", "SCUS", "WUS", "NEU", "SEA"]
  
github:
  repo: "enterprise/microservice-platform"
  base_url: "https://github.enterprise.com/api/v3"
  enterprise:
    enabled: true
    saml_sso: true
    
ai:
  providers: ["azure_openai", "openai"]
  azure_openai:
    deployment_name: "enterprise-gpt4"
    
security:
  compliance:
    gdpr_compliant: true
    audit_logging: true
```

---

## 🔗 **Related Documentation**

- **[Quick Start Guide](quickstart.md)** - Get up and running
- **[Template Customization](templates.md)** - Customize output formats
- **[Enterprise Deployment](enterprise.md)** - Large-scale deployment
- **[Troubleshooting](troubleshooting.md)** - Common configuration issues

**Need help with configuration?** [Create an issue](https://github.com/ArnoldoM23/automated-release-rc/issues) or check our [discussions](https://github.com/ArnoldoM23/automated-release-rc/discussions). 