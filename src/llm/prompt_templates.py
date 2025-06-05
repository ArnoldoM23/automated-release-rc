# src/llm/prompt_templates.py

def generate_crq_prompt(release_notes: str, settings_yaml: str) -> str:
    """
    Construct the LLM prompt to generate a CRQ document based on release notes and settings.
    """
    return f"""
You are a Release Engineering AI assistant. Your job is to generate a CRQ (Change Request Questionnaire) for deployment approval.

Context:
- You are generating the CRQ for Walmart's production deployment.
- You are using the following inputs:

--- RELEASE NOTES ---
{release_notes}

--- SETTINGS YAML ---
{settings_yaml}

Instructions:
- Fill all required CRQ fields: Summary, Description (answer 7 risk-related questions inline), Implementation Plan, Validation Plan, and Backout Plan.
- Use markdown-safe formatting with NO markdown syntax (this will be inserted into Confluence).
- Add version numbers and deployment namespaces from the settings.yaml.
- Use job-specific reasoning to fill rollout and rollback logic.

Output Format:
1. Summary:
2. Description (answer 7 risk-related questions inline):
3. Implementation Plan:
4. Validation Plan:
5. Backout Plan:
"""


def generate_release_summary_prompt(pr_list: list, exclude_international: bool = True) -> str:
    """
    Construct the LLM prompt to generate a leadership-facing release summary.
    """
    filtered_prs = [pr for pr in pr_list if not (exclude_international and pr.get('is_international', False))]
    
    pr_details = "\n".join([
        f"- PR #{pr.get('number', 'N/A')}: {pr.get('title', 'No title')} ({pr.get('author', 'Unknown')})"
        for pr in filtered_prs
    ])
    
    return f"""
You are a Release Engineering AI assistant. Generate a concise, leadership-facing release summary.

Context:
- This summary will be included in Section 8 of our release notes
- Target audience: Leadership and stakeholders  
- Focus on business impact and customer value

PR Details:
{pr_details}

Instructions:
- Write 2-3 sentences maximum
- Focus on customer-facing improvements and business value
- Exclude technical implementation details
- Use professional, executive-level language
- Highlight major features, critical fixes, and performance improvements

Output a clean summary without any markdown formatting.
"""


def generate_pr_analysis_prompt(pr_title: str, pr_body: str) -> str:
    """
    Construct the LLM prompt to analyze and categorize a PR.
    """
    return f"""
You are a Release Engineering AI assistant. Analyze this PR and provide categorization.

PR Title: {pr_title}
PR Body: {pr_body}

Instructions:
- Categorize as: schema, feature, bugfix, or international
- Assess impact level: low, medium, high
- Identify blast radius: component, service, platform
- Suggest testing focus areas

Output format:
Category: [category]
Impact: [level]  
Blast Radius: [scope]
Testing Focus: [areas]
Risk Assessment: [brief analysis]
""" 