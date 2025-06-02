#!/usr/bin/env python3
"""
Release Notes Generator

Generates Confluence-ready release notes from PR data using Jinja2 templates.
"""

import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, Template

from src.utils.logging import get_logger


def categorize_prs(prs: List) -> Dict[str, List]:
    """Categorize PRs by their labels for better organization."""
    logger = get_logger(__name__)
    
    categories = {
        "schema": [],
        "features": [],
        "bugfixes": [],
        "dependencies": [],
        "documentation": [],
        "infrastructure": [],
        "other": []
    }
    
    # Define label mappings
    label_mappings = {
        "schema": ["schema", "graphql", "api", "breaking", "migration", "database"],
        "features": ["feature", "enhancement", "new feature", "feat"],
        "bugfixes": ["bug", "fix", "bugfix", "hotfix", "patch"],
        "dependencies": ["dependencies", "dependency", "deps", "bump"],
        "documentation": ["documentation", "docs", "readme"],
        "infrastructure": ["infrastructure", "ci", "cd", "deploy", "devops", "infra"]
    }
    
    for pr in prs:
        categorized = False
        pr_labels = [label.name.lower() for label in pr.labels]
        pr_title_lower = pr.title.lower()
        pr_body_lower = getattr(pr, 'body', '').lower() if hasattr(pr, 'body') and pr.body else ''
        
        # Check each category (schema first since it's highest priority)
        for category, keywords in label_mappings.items():
            # Check in labels, title, and body
            if (any(keyword in " ".join(pr_labels) for keyword in keywords) or
                any(keyword in pr_title_lower for keyword in keywords) or
                any(keyword in pr_body_lower for keyword in keywords)):
                categories[category].append(pr)
                categorized = True
                break
        
        # If no category found, put in "other"
        if not categorized:
            categories["other"].append(pr)
    
    # Log categorization results
    for category, prs_in_category in categories.items():
        if prs_in_category:
            logger.info(f"  {category}: {len(prs_in_category)} PRs")
    
    return categories


def create_confluence_template() -> Template:
    """Create the Confluence wiki markup template."""
    template_content = """h1. Release Notes - {{ service_name }} {{ new_version }}

*Release Date:* {{ release_date }}  
*Release Coordinator:* {{ rc_name }}  
*Release Manager:* {{ rc_manager }}  
*Release Type:* {{ release_type|title }}

---

h2. 📋 Summary

This release includes {{ total_prs }} pull request(s) with the following changes:
{% if categories.features %}
* ✨ **{{ categories.features|length }} New Features**
{%- endif %}
{% if categories.bugfixes %}
* 🐛 **{{ categories.bugfixes|length }} Bug Fixes**
{%- endif %}
{% if categories.dependencies %}
* 📦 **{{ categories.dependencies|length }} Dependency Updates**
{%- endif %}
{% if categories.documentation %}
* 📚 **{{ categories.documentation|length }} Documentation Updates**
{%- endif %}
{% if categories.infrastructure %}
* 🔧 **{{ categories.infrastructure|length }} Infrastructure Changes**
{%- endif %}
{% if categories.other %}
* 🔹 **{{ categories.other|length }} Other Changes**
{%- endif %}

---

{% if categories.features %}
h2. ✨ New Features

{% for pr in categories.features %}
* *PR #{{ pr.number }}:* {{ pr.title }}
  * Author: @{{ pr.user.login }}
  * Labels: {{ pr.labels|map(attribute='name')|join(', ') or 'None' }}
  * [View PR|{{ pr.html_url }}]

{% endfor %}
{% endif %}

{% if categories.bugfixes %}
h2. 🐛 Bug Fixes

{% for pr in categories.bugfixes %}
* *PR #{{ pr.number }}:* {{ pr.title }}
  * Author: @{{ pr.user.login }}
  * Labels: {{ pr.labels|map(attribute='name')|join(', ') or 'None' }}
  * [View PR|{{ pr.html_url }}]

{% endfor %}
{% endif %}

{% if categories.dependencies %}
h2. 📦 Dependency Updates

{% for pr in categories.dependencies %}
* *PR #{{ pr.number }}:* {{ pr.title }}
  * Author: @{{ pr.user.login }}
  * [View PR|{{ pr.html_url }}]

{% endfor %}
{% endif %}

{% if categories.documentation %}
h2. 📚 Documentation Updates

{% for pr in categories.documentation %}
* *PR #{{ pr.number }}:* {{ pr.title }}
  * Author: @{{ pr.user.login }}
  * [View PR|{{ pr.html_url }}]

{% endfor %}
{% endif %}

{% if categories.infrastructure %}
h2. 🔧 Infrastructure Changes

{% for pr in categories.infrastructure %}
* *PR #{{ pr.number }}:* {{ pr.title }}
  * Author: @{{ pr.user.login }}
  * [View PR|{{ pr.html_url }}]

{% endfor %}
{% endif %}

{% if categories.other %}
h2. 🔹 Other Changes

{% for pr in categories.other %}
* *PR #{{ pr.number }}:* {{ pr.title }}
  * Author: @{{ pr.user.login }}
  * Labels: {{ pr.labels|map(attribute='name')|join(', ') or 'None' }}
  * [View PR|{{ pr.html_url }}]

{% endfor %}
{% endif %}

---

h2. 🚀 Deployment Information

*Deployment Schedule:*
* *Day 1 ({{ day1_date }}):* Pre-deployment setup and validation
* *Day 2 ({{ day2_date }}):* Production deployment

*Rollback Plan:* 
If issues are encountered, we can rollback to {{ prod_version }} using our standard rollback procedures.

*Validation:*
* All automated tests passing
* Manual QA validation completed
* Performance benchmarks verified
* Security scans completed

---

h2. 📞 Contact Information

*Release Coordinator:* {{ rc_name }}  
*Release Manager:* {{ rc_manager }}  
*For issues or questions:* Contact the release team in #release-rc

---

*Generated automatically by RC Release Automation on {{ generation_timestamp }}*"""

    return Template(template_content)


def render_release_notes(prs: List, params: Dict[str, Any], output_dir: Path, config=None) -> Path:
    """
    Generate Confluence-formatted release notes from PR data.
    
    Args:
        prs: List of PR objects from GitHub API
        params: Dictionary with release parameters
        output_dir: Path to output directory
        config: Optional configuration object (loads default if None)
        
    Returns:
        Path to generated release notes file
    """
    logger = get_logger(__name__)
    
    try:
        # Load configuration if not provided
        if config is None:
            from src.config.config import load_config
            config = load_config()
        
        # Setup output directory
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Categorize PRs for better organization
        logger.info(f"Categorizing {len(prs)} PRs...")
        categories = categorize_prs(prs)
        
        # Create PR categories mapping for template
        pr_categories = {}
        for category, prs_in_category in categories.items():
            for pr in prs_in_category:
                if category == "schema":
                    pr_categories[pr.number] = "schema"
                elif category == "features":
                    pr_categories[pr.number] = "feature"
                elif category == "bugfixes":
                    pr_categories[pr.number] = "bugfix"
                elif category == "dependencies":
                    pr_categories[pr.number] = "dependency"
                elif category == "documentation":
                    pr_categories[pr.number] = "docs"
                elif category == "infrastructure":
                    pr_categories[pr.number] = "infra"
                else:
                    pr_categories[pr.number] = "feature"
        
        # Extract GitHub repository info from config
        github_repo = getattr(config.github, 'repo', 'company/repo')
        
        # Prepare comprehensive template variables
        template_vars = {
            # Basic release information
            "service_name": params["service_name"],
            "new_version": params["new_version"],
            "prod_version": params["prod_version"],
            "release_type": params["release_type"],
            "rc_name": params["rc_name"],
            "rc_manager": params["rc_manager"],
            "day1_date": params["day1_date"],
            "day2_date": params["day2_date"],
            "release_date": params["day2_date"],  # Use Day 2 as release date
            "total_prs": len(prs),
            "generation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            
            # GitHub and version control
            "github_repo": github_repo,
            "base_branch": "main",  # Could be made configurable
            "head_branch": "main",
            "base_sha": "TBD",  # Would need Git integration to get actual SHAs
            "head_sha": "TBD",
            
            # URLs and links
            "slack_thread_url": f"https://company.slack.com/channels/release-rc",
            "diff_url": f"https://github.com/{github_repo}/compare/{params['prod_version']}...{params['new_version']}",
            "grafana_url": f"https://grafana.company.com/d/{params['service_name']}-dashboard",
            "dashboard_url": f"https://dashboard.company.com/{params['service_name']}",
            "datadog_url": f"https://app.datadoghq.com/apm/services/{params['service_name']}",
            "alerts_url": f"https://alerts.company.com/{params['service_name']}",
            
            # CRQ information
            "crq1_id": f"CRQ-{params['service_name']}-{params['day1_date'].replace('-', '')}",
            "crq1_url": "TBD",  # Would be populated after CRQ creation
            "crq2_id": f"CRQ-{params['service_name']}-{params['day2_date'].replace('-', '')}",
            "crq2_url": "TBD",
            
            # Release team (defaults from params if not in config)
            "idc_captain": getattr(config.organization, 'idc_captain', params['rc_name']),
            "idc_engineer": getattr(config.organization, 'idc_engineer', params['rc_name']),
            "us_captain": getattr(config.organization, 'us_captain', params['rc_manager']),
            "us_engineer": getattr(config.organization, 'us_engineer', params['rc_manager']),
            
            # Deployment clusters
            "cluster1": getattr(config.organization, 'regions', ['EUS'])[0] if hasattr(config.organization, 'regions') else 'EUS',
            "cluster2": getattr(config.organization, 'regions', ['EUS', 'SCUS'])[1] if len(getattr(config.organization, 'regions', [])) > 1 else 'SCUS',
            "cluster3": getattr(config.organization, 'regions', ['EUS', 'SCUS', 'WUS'])[2] if len(getattr(config.organization, 'regions', [])) > 2 else 'WUS',
            "cluster1_notes": "Standard deployment - no special notes",
            "cluster2_notes": "Standard deployment - no special notes", 
            "cluster3_notes": "Standard deployment - no special notes",
            
            # Rollback information
            "rollback_branch": "main",
            "rollback_version": params["prod_version"],
            "rollback_sha": "TBD",
            
            # PR data and categorization
            "prs": prs,
            "pr_categories": pr_categories,
            "categories": categories,
            
            # International PRs (use from params if provided, otherwise empty)
            "international_prs": params.get("international_prs", []),
            "ccm_updates": [],  # Would come from external system
            
            # Schema and automation URLs
            "schema_report_url": "TBD",
            "automation_run_url": "TBD", 
            "test_results_url": "TBD",
            
            # Time defaults
            "day1_time": "09:00",
            "day2_time": "09:00"
        }
        
        # Generate section 8 and 9 using the new inline panel functions
        section_8_markup = generate_schema_and_features_section(prs, pr_categories)
        section_9_markup = generate_international_section(template_vars.get('international_prs', []))
        
        # Add pre-generated sections to template vars
        template_vars["section_8_markup"] = section_8_markup
        template_vars["section_9_markup"] = section_9_markup
        
        # Debug: Log the pre-generated sections
        logger.info(f"Section 8 markup preview: {section_8_markup[:150]}...")
        logger.info(f"Section 9 markup preview: {section_9_markup[:150]}...")
        
        # Load and render template
        try:
            # Try to load custom template first
            template_path = Path("src/templates/release_notes.j2")
            logger.info(f"Checking template path: {template_path.absolute()}")
            logger.info(f"Template exists: {template_path.exists()}")
            
            if template_path.exists():
                env = Environment(loader=FileSystemLoader("src/templates"))
                template = env.get_template("release_notes.j2")
                logger.info("Loading custom template successfully")
                rendered_content = template.render(**template_vars)
            else:
                # Fall back to built-in template
                logger.warning("Custom template not found, using built-in template")
                template = create_confluence_template()
                rendered_content = template.render(**template_vars)
        except Exception as template_error:
            logger.warning(f"Template rendering failed: {template_error}, using fallback")
            # Use the simple built-in template as fallback
            template = create_confluence_template()
            rendered_content = template.render(**template_vars)
        
        # Save to file
        output_file = output_dir / "release_notes.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(rendered_content)
        
        logger.info(f"Release notes generated successfully: {output_file}")
        logger.info(f"Content preview (first 200 chars): {rendered_content[:200]}...")
        
        return output_file
        
    except Exception as e:
        logger.error(f"Failed to generate release notes: {e}")
        raise


def render_release_notes_markdown(prs: List, params: Dict[str, Any], output_dir: Path, config=None) -> Path:
    """Alternative markdown format for GitHub/GitLab."""
    logger = get_logger(__name__)
    
    try:
        # Load configuration if not provided
        if config is None:
            from src.config.config import load_config
            config = load_config()
        
        categories = categorize_prs(prs)
        
        markdown_content = f"""# Release Notes - {params['service_name']} {params['new_version']}

**Release Date:** {params['day2_date']}  
**Release Coordinator:** {params['rc_name']}  
**Release Manager:** {params['rc_manager']}  
**Release Type:** {params['release_type'].title()}

---

## 📋 Summary

This release includes {len(prs)} pull request(s) with the following changes:

"""
        
        # Add summary by category
        for category, prs_in_category in categories.items():
            if prs_in_category:
                category_names = {
                    "schema": "🔗 Schema Changes",
                    "features": "✨ New Features",
                    "bugfixes": "🐛 Bug Fixes", 
                    "dependencies": "📦 Dependency Updates",
                    "documentation": "📚 Documentation Updates",
                    "infrastructure": "🔧 Infrastructure Changes",
                    "other": "🔹 Other Changes"
                }
                category_name = category_names.get(category, f"🔹 {category.title()} Changes")
                markdown_content += f"* **{len(prs_in_category)} {category_name}**\n"
        
        # Add detailed sections
        for category, prs_in_category in categories.items():
            if prs_in_category:
                category_names = {
                    "schema": "## 🔗 Schema Changes",
                    "features": "## ✨ New Features",
                    "bugfixes": "## 🐛 Bug Fixes",
                    "dependencies": "## 📦 Dependency Updates", 
                    "documentation": "## 📚 Documentation Updates",
                    "infrastructure": "## 🔧 Infrastructure Changes",
                    "other": "## 🔹 Other Changes"
                }
                
                category_header = category_names.get(category, f"## 🔹 {category.title()} Changes")
                markdown_content += f"\n{category_header}\n\n"
                
                for pr in prs_in_category:
                    labels = ", ".join([label.name for label in pr.labels]) or "None"
                    markdown_content += f"* **PR #{pr.number}:** {pr.title}\n"
                    markdown_content += f"  * Author: @{pr.user.login}\n"
                    if labels != "None":
                        markdown_content += f"  * Labels: {labels}\n"
                    markdown_content += f"  * [View PR]({pr.html_url})\n\n"
        
        # Save markdown version
        markdown_file = output_dir / "release_notes.md"
        with open(markdown_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)
            
        logger.info(f"Markdown release notes generated: {markdown_file}")
        return markdown_file
        
    except Exception as e:
        logger.error(f"Failed to generate markdown release notes: {e}")
        raise


def generate_confluence_section_with_panels(section_num: int, section_title: str, panels: List[Dict[str, Any]]) -> str:
    """
    Generate a Confluence wiki markup section with inline panels to avoid table structure breaking.
    
    Args:
        section_num: Section number (e.g., 8, 9)
        section_title: Section title (e.g., "GraphQL Schema Changes")
        panels: List of panel configurations, each containing:
            - title: Panel title
            - description: Optional description text
            - headers: List of column headers
            - rows: List of row data (each row is a list of cell values)
            - bg_color: Optional background color (default: #F7F7F7)
    
    Returns:
        Properly formatted Confluence wiki markup as a single line
    """
    
    # Start the section row
    markup = f"|| {section_num} || {section_title} || "
    
    # Generate each panel inline
    for i, panel in enumerate(panels):
        bg_color = panel.get('bg_color', '#F7F7F7')
        
        # Panel opening
        markup += f"{{panel:title={panel['title']}|borderStyle=solid|borderColor=#ccc|titleBGColor={bg_color}|bgColor=#FFFFFF}}"
        
        # Add description if provided
        if panel.get('description'):
            markup += panel['description'] + "\n\n"
        
        # Add table headers
        headers = panel.get('headers', [])
        if headers:
            markup += "|| " + " || ".join(headers) + " ||\n"
        
        # Add table rows
        rows = panel.get('rows', [])
        for row in rows:
            markup += "| " + " | ".join(str(cell) for cell in row) + " |\n"
        
        # Panel closing
        markup += "{panel}"
    
    # Close the section row
    markup += " ||"
    
    return markup


def generate_schema_and_features_section(prs: List, pr_categories: Dict[int, str]) -> str:
    """
    Generate Section 8 (GraphQL Schema Changes) with both Schema and Features/Bugfixes panels.
    
    Args:
        prs: List of GitHub PR objects
        pr_categories: Dictionary mapping PR numbers to categories
        
    Returns:
        Confluence wiki markup for section 8
    """
    
    # Separate schema PRs from feature/bugfix PRs
    schema_prs = [pr for pr in prs if pr_categories.get(pr.number) == 'schema']
    feature_bugfix_prs = [pr for pr in prs if pr_categories.get(pr.number) in ['feature', 'bugfix', 'enhancement']]
    
    panels = []
    
    # Schema Changes Panel
    schema_headers = ["Sign-off", "PR link", "Author", "Description", "Backwards Compatible", "Pre-prod testing", "Image / Query"]
    schema_rows = []
    
    if schema_prs:
        for pr in schema_prs:
            row = [
                "❌",
                f"[#{pr.number}|{pr.html_url}]",
                f"@{pr.user.login}",
                pr.title[:50] + ("..." if len(pr.title) > 50 else ""),
                "✅",
                "✅", 
                getattr(pr, 'image_url', 'None') or 'None'
            ]
            schema_rows.append(row)
    else:
        # Default empty row
        schema_rows.append(["❌", "TBD", "TBD", "No schema changes in this release", "✅", "✅", "None"])
    
    panels.append({
        'title': 'Schema Changes',
        'description': 'All new additions are optional (no default value but none required).',
        'headers': schema_headers,
        'rows': schema_rows
    })
    
    # Features/Bugfixes Panel
    feature_headers = ["Sign-off", "PR link", "Author", "Description", "Type (bugfix, schema, feature)", "Feature CCM", "Pre-Prod Testing", "CCM ON", "CCM OFF", "Image / Query", "iOS Screenshots", "Android Screenshots", "Comments"]
    feature_rows = []
    
    for pr in (feature_bugfix_prs or prs):  # Use all PRs if no specific feature/bugfix PRs
        pr_type = pr_categories.get(pr.number, 'feature')
        
        row = [
            "❌",
            f"[#{pr.number}|{pr.html_url}]",
            f"@{pr.user.login}",
            pr.title[:50] + ("..." if len(pr.title) > 50 else ""),
            pr_type,
            "TBD",
            "✅",
            "✅",
            "⭕",
            getattr(pr, 'image_url', 'None') or 'None',
            "✅" if getattr(pr, 'screenshots', {}).get('iOS') else "❌",
            "✅" if getattr(pr, 'screenshots', {}).get('Android') else "❌",
            getattr(pr, 'comments', '') or ''
        ]
        feature_rows.append(row)
    
    panels.append({
        'title': 'Features / Bugfixes',
        'headers': feature_headers,
        'rows': feature_rows
    })
    
    return generate_confluence_section_with_panels(8, "GraphQL Schema Changes", panels)


def generate_international_section(international_prs: List = None) -> str:
    """
    Generate Section 9 (Internationalization & Localization Changes).
    
    Args:
        international_prs: List of international-related PRs
        
    Returns:
        str: Confluence markup for international changes section
    """
    rows = []
    
    if international_prs:
        for pr in international_prs:
            rows.append([
                f"PR #{pr.number}",
                pr.user.login if hasattr(pr, 'user') and hasattr(pr.user, 'login') else "Unknown",
                pr.title,
                pr.html_url if hasattr(pr, 'html_url') else f"#PR{pr.number}",
                "✅"
            ])
    else:
        # Default row when no international changes
        rows.append(["N/A", "N/A", "No internationalization changes in this release", "N/A", "✅"])
    
    panels = [{
        'title': 'Internationalization & Localization Changes',
        'rows': rows,
        'headers': ['PR', 'Developer', 'Description', 'Link', 'Status']
    }]
    
    return generate_confluence_section_with_panels(9, "Internationalization & Localization Changes", panels) 