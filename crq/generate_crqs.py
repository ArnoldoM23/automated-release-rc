#!/usr/bin/env python3
"""
CRQ Generator

Generates Day 1 and Day 2 CRQ documents using AI and templates.
Integrates with the existing CRQ template structure.
"""

import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from jinja2 import Template

from utils.logging import get_logger
from utils.ai_client import AIClient
from config.config import load_config


def analyze_prs_with_ai(prs: List, params: Dict[str, Any], config=None) -> Dict[str, str]:
    """Use AI to analyze PRs and generate intelligent CRQ content."""
    logger = get_logger(__name__)
    
    try:
        # Load config for AI client if not provided
        if config is None:
            config = load_config()
        ai_client = AIClient(config.ai)
        
        # Prepare PR summary for AI analysis
        pr_summary = []
        for pr in prs:
            pr_info = {
                "number": pr.number,
                "title": pr.title,
                "author": pr.user.login,
                "labels": [label.name for label in pr.labels],
                "body": pr.body[:500] if pr.body else "No description"  # Limit body length
            }
            pr_summary.append(pr_info)
        
        # Create AI prompt for CRQ analysis
        ai_prompt = f"""
You are a technical release manager creating a Change Request (CRQ) for a production deployment.

SERVICE: {params['service_name']}
VERSION: {params['prod_version']} → {params['new_version']}
RELEASE TYPE: {params['release_type']}

PULL REQUESTS INCLUDED:
{pr_summary}

Please analyze these changes and provide the following:

1. RISK_ASSESSMENT: What are the potential risks of this deployment? Consider code changes, dependencies, and impact.

2. TECHNICAL_SUMMARY: Summarize the technical changes in 2-3 sentences for stakeholders.

3. VALIDATION_STEPS: What specific validation steps should be performed to ensure the deployment is successful?

4. ROLLBACK_SCENARIOS: Under what circumstances should we rollback? What are the specific triggers?

5. BUSINESS_IMPACT: What is the business impact of these changes? Any user-facing improvements or fixes?

Format your response as:
RISK_ASSESSMENT: [your analysis]
TECHNICAL_SUMMARY: [your summary]
VALIDATION_STEPS: [your steps]
ROLLBACK_SCENARIOS: [your scenarios]
BUSINESS_IMPACT: [your impact analysis]
"""
        
        logger.info("Analyzing PRs with AI for intelligent CRQ content...")
        ai_response = ai_client.generate_text(ai_prompt)
        
        # Parse AI response into components
        ai_analysis = {}
        current_section = None
        current_content = []
        
        for line in ai_response.split('\n'):
            line = line.strip()
            if line.startswith(('RISK_ASSESSMENT:', 'TECHNICAL_SUMMARY:', 'VALIDATION_STEPS:', 
                               'ROLLBACK_SCENARIOS:', 'BUSINESS_IMPACT:')):
                # Save previous section
                if current_section:
                    ai_analysis[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = line.split(':')[0]
                current_content = [line.split(':', 1)[1].strip()]
            elif current_section and line:
                current_content.append(line)
        
        # Save last section
        if current_section:
            ai_analysis[current_section] = '\n'.join(current_content).strip()
        
        logger.info("AI analysis completed successfully")
        return ai_analysis
        
    except Exception as e:
        logger.warning(f"AI analysis failed, using fallback content: {e}")
        # Return fallback content if AI fails
        return {
            "RISK_ASSESSMENT": "Medium risk - Standard release with multiple code changes. Requires careful validation.",
            "TECHNICAL_SUMMARY": f"Deployment of {params['service_name']} {params['new_version']} including {len(prs)} pull requests with various improvements and fixes.",
            "VALIDATION_STEPS": "Verify application startup, check key functionality, monitor logs and metrics for 30 minutes post-deployment.",
            "ROLLBACK_SCENARIOS": "Rollback if: application fails to start, critical functionality broken, error rates >5%, or performance degradation >20%.",
            "BUSINESS_IMPACT": "Improved functionality and bug fixes for end users. Enhanced system reliability and performance."
        }


def create_day1_crq_template() -> Template:
    """Create Day 1 CRQ template matching the user's format."""
    template_content = """
**CHANGE REQUEST - DAY 1 (Preparation & Setup)**

**Summary:** {{ service_name }} Application Code deployment for {{ platform }} ({{ regions | join(', ') }}) - Day 1 Preparation

**Change Request Details:**

**Service:** {{ service_name }}
**Version:** {{ prod_version }} → {{ new_version }}
**Release Type:** {{ release_type | title }}
**Date:** {{ day1_date }}
**Time:** Pre-deployment preparation
**Duration:** 2-4 hours
**Release Coordinator:** {{ rc_name }}
**Release Manager:** {{ rc_manager }}

---

**DESCRIPTION**

**1. What is the business reason for this change?**
{{ ai_analysis.get('BUSINESS_IMPACT', 'Scheduled release containing bug fixes, feature enhancements, and system improvements to maintain service quality and add new functionality.') }}

**2. What is the technical summary of this change?**
{{ ai_analysis.get('TECHNICAL_SUMMARY', 'Deployment of ' + service_name + ' version ' + new_version + ' containing ' + total_prs|string + ' pull requests with code changes, dependency updates, and configuration modifications.') }}

**3. What testing has been performed?**
- All automated test suites passing
- Integration tests completed successfully  
- Performance testing completed
- Security scans completed
- Code review and approval processes completed

**4. What is the risk assessment for this change?**
{{ ai_analysis.get('RISK_ASSESSMENT', 'Medium risk - Standard deployment process with established rollback procedures. Changes have been tested in staging environment.') }}

**5. What is the impact if this change fails?**
Service downtime limited to rollback duration (~15-30 minutes). Established monitoring and rollback procedures minimize impact.

**6. What are the dependencies for this change?**
- Infrastructure team coordination
- Database migration compatibility (if applicable)
- External service compatibility verified
- Monitoring systems operational

**7. Who are the stakeholders and how will they be notified?**
- Engineering teams via Slack #release-rc
- Operations team via standard deployment notifications
- Business stakeholders via release communications

---

**IMPLEMENTATION PLAN - DAY 1**

**Pre-Deployment Tasks:**
1. **Environment Preparation (09:00-10:00)**
   - Verify staging environment matches production
   - Confirm all dependencies are ready
   - Validate monitoring systems operational

2. **Artifact Preparation (10:00-11:00)**
   - Build and validate deployment artifacts
   - Run final automated test suite
   - Package deployment with version {{ new_version }}

3. **Infrastructure Validation (11:00-12:00)**
   - Verify target environment capacity
   - Confirm database migration readiness (if applicable)
   - Test rollback procedures in staging

4. **Team Coordination (12:00-13:00)**
   - Final deployment readiness review
   - Confirm Day 2 deployment team availability
   - Validate communication channels

**Success Criteria Day 1:**
- All deployment artifacts validated
- Infrastructure readiness confirmed
- Team coordination completed
- Go/No-go decision made for Day 2

---

**VALIDATION PLAN - DAY 1**

{{ ai_analysis.get('VALIDATION_STEPS', 'Validate deployment artifacts, confirm staging environment stability, verify rollback procedures, and complete team readiness assessment.') }}

**Validation Steps:**
1. Deployment artifact integrity checks
2. Staging environment smoke tests
3. Rollback procedure verification
4. Monitoring dashboard validation
5. Team communication test

---

**BACKOUT PLAN - DAY 1**

**Criteria for Stopping Day 1 Activities:**
{{ ai_analysis.get('ROLLBACK_SCENARIOS', 'Stop if: deployment artifacts fail validation, infrastructure issues detected, critical team members unavailable, or staging environment issues identified.') }}

**Backout Steps:**
1. Halt deployment preparation
2. Notify stakeholders via #release-rc
3. Schedule post-mortem if needed
4. Reschedule deployment window

**Decision Authority:** {{ rc_manager }}
**Communication:** Release team lead

---

**Generated:** {{ generation_timestamp }}
**Total PRs:** {{ total_prs }}
**Automation:** RC Release Automation System
"""
    return Template(template_content)


def create_day2_crq_template() -> Template:
    """Create Day 2 CRQ template for actual deployment."""
    template_content = """
**CHANGE REQUEST - DAY 2 (Production Deployment)**

**Summary:** {{ service_name }} Application Code deployment for {{ platform }} ({{ regions | join(', ') }}) - Day 2 Production Release

**Change Request Details:**

**Service:** {{ service_name }}
**Version:** {{ prod_version }} → {{ new_version }}
**Release Type:** {{ release_type | title }}
**Date:** {{ day2_date }}
**Time:** Production deployment window
**Duration:** 1-2 hours + 1 hour monitoring
**Release Coordinator:** {{ rc_name }}
**Release Manager:** {{ rc_manager }}

---

**DESCRIPTION**

**1. What is the business reason for this change?**
{{ ai_analysis.get('BUSINESS_IMPACT', 'Execute production deployment of tested and validated changes to deliver bug fixes, feature enhancements, and system improvements to end users.') }}

**2. What is the technical summary of this change?**
{{ ai_analysis.get('TECHNICAL_SUMMARY', 'Production deployment of ' + service_name + ' version ' + new_version + ' containing ' + total_prs|string + ' pull requests that have been validated in Day 1 preparation.') }}

**3. What testing has been performed?**
- Day 1 preparation completed successfully
- All validation criteria met
- Deployment artifacts verified
- Rollback procedures tested

**4. What is the risk assessment for this change?**
{{ ai_analysis.get('RISK_ASSESSMENT', 'Low-Medium risk - All Day 1 preparation completed. Standard deployment with established procedures and validated rollback plan.') }}

**5. What is the impact if this change fails?**
Temporary service disruption during rollback (15-30 minutes). Monitoring alerts will trigger immediate response. Business operations continue with previous version.

**6. What are the dependencies for this change?**
- Day 1 preparation completed successfully
- Deployment team available and coordinated
- Monitoring systems operational
- Communication channels active

**7. Who are the stakeholders and how will they be notified?**
- Real-time updates in #release-rc Slack channel
- Deployment status via monitoring dashboards
- Immediate notification of any issues
- Post-deployment summary to stakeholders

---

**IMPLEMENTATION PLAN - DAY 2**

**Production Deployment Tasks:**
1. **Pre-Deployment Checks (09:00-09:30)**
   - Verify Day 1 preparation completion
   - Confirm team readiness
   - Final go/no-go decision

2. **Production Deployment (09:30-10:30)**
   - Deploy {{ service_name }} version {{ new_version }}
   - Execute database migrations (if applicable)
   - Update configuration as needed
   - Verify service startup

3. **Post-Deployment Validation (10:30-11:30)**
   - Smoke test critical functionality
   - Monitor error rates and performance
   - Validate user-facing features
   - Confirm metrics within expected ranges

4. **Monitoring & Stabilization (11:30-12:30)**
   - Extended monitoring period
   - Performance validation
   - User feedback monitoring
   - Final deployment confirmation

**Success Criteria Day 2:**
- Service successfully deployed and running
- All validation tests passing
- Performance metrics within acceptable ranges
- No critical errors detected

---

**VALIDATION PLAN - DAY 2**

{{ ai_analysis.get('VALIDATION_STEPS', 'Comprehensive post-deployment validation including functionality testing, performance monitoring, error rate analysis, and user experience verification.') }}

**Post-Deployment Validation:**
1. **Immediate Checks (0-15 minutes)**
   - Application startup successful
   - Health check endpoints responding
   - Database connectivity confirmed
   - Load balancer routing properly

2. **Functional Validation (15-45 minutes)**
   - Key user workflows tested
   - API endpoints responding correctly
   - Integration points functioning
   - Authentication/authorization working

3. **Performance Monitoring (45-90 minutes)**
   - Response times within SLA
   - Error rates < 1%
   - Resource utilization normal
   - Database performance stable

**Monitoring Dashboards:**
- DataDog: Application performance and errors
- Grafana: Infrastructure metrics
- AppInsights: User experience metrics

---

**BACKOUT PLAN - DAY 2**

**Criteria for Rollback:**
{{ ai_analysis.get('ROLLBACK_SCENARIOS', 'Immediate rollback if: application fails to start, critical functionality broken, error rates >5%, response times >3x baseline, or any P1 incident triggered.') }}

**Rollback Triggers:**
- Application startup failure
- Critical functionality unavailable
- Error rate exceeds 5%
- Performance degradation >50%
- P1/P0 incident triggered

**Rollback Steps:**
1. **Immediate Response (0-5 minutes)**
   - Stop new deployments
   - Notify via #release-rc
   - Begin rollback procedure

2. **Rollback Execution (5-20 minutes)**
   - Deploy previous version {{ prod_version }}
   - Restore database to pre-deployment state (if needed)
   - Verify rollback success
   - Update load balancer routing

3. **Post-Rollback (20-30 minutes)**
   - Confirm service stability
   - Notify stakeholders
   - Begin incident post-mortem
   - Document rollback reason

**Decision Authority:** {{ rc_manager }}
**Escalation:** Available 24/7 during deployment window

---

**PULL REQUESTS INCLUDED:**
{% for pr in prs %}
- PR #{{ pr.number }}: {{ pr.title }} (@{{ pr.user.login }})
{% endfor %}

**Generated:** {{ generation_timestamp }}
**Total PRs:** {{ total_prs }}
**Automation:** RC Release Automation System
"""
    return Template(template_content)


def generate_crqs(prs: List, params: Dict[str, Any], output_dir: Path, config=None) -> List[Path]:
    """
    Generate Day 1 and Day 2 CRQ documents using enterprise template.
    
    Args:
        prs: List of GitHub PR objects
        params: Release parameters from CLI
        output_dir: Directory to save the CRQ documents
        config: Optional configuration object (loads default if None)
        
    Returns:
        List of paths to generated CRQ files
    """
    logger = get_logger(__name__)
    
    try:
        # Get AI analysis of PRs
        logger.info("Generating AI-powered CRQ content...")
        ai_analysis = analyze_prs_with_ai(prs, params, config)
        
        # Load configuration for organization details if not provided
        if config is None:
            config = load_config()
        
        # Prepare common template variables
        base_template_vars = {
            "service_name": params["service_name"],
            "new_version": params["new_version"],
            "prod_version": params["prod_version"],
            "release_type": params["release_type"],
            "rc_name": params["rc_name"],
            "rc_manager": params["rc_manager"],
            "day1_date": params["day1_date"],
            "day2_date": params["day2_date"],
            "platform": getattr(config.organization, 'platform', 'Glass'),
            "regions": getattr(config.organization, 'regions', ['EUS', 'SCUS', 'WUS']),
            "namespace": params["service_name"].lower().replace('_', '-'),
            "assembly": f"{params['service_name'].lower().replace('_', '-')}-assembly",
            "total_prs": len(prs),
            "prs": prs,
            "ai_analysis": ai_analysis,
            "generation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "confluence_link": f"https://confluence.company.com/display/RELEASES/{params['service_name'].upper()}/Release-{params['new_version']}",
            "dashboard_url": f"https://confluence.company.com/display/{params['service_name'].upper()}/Dashboards",
            "grafana_url": f"https://grafana.company.com/d/{params['service_name']}-p0",
            "l1_dashboard_url": f"https://grafana.company.com/d/{params['service_name']}-l1",
            "services_dashboard_url": f"https://grafana.company.com/d/{params['service_name']}-services",
            "wcnp_dashboard_url": f"https://grafana.company.com/d/{params['service_name']}-wcnp",
            "istio_dashboard_url": f"https://grafana.company.com/d/{params['service_name']}-istio"
        }
        
        generated_files = []
        
        # Try to load enterprise template
        try:
            from jinja2 import Environment, FileSystemLoader
            template_path = Path("templates")
            
            if (template_path / "crq_template.j2").exists():
                logger.info("Using enterprise CRQ template")
                env = Environment(loader=FileSystemLoader("templates"))
                template = env.get_template("crq_template.j2")
                
                # Generate Day 1 CRQ
                logger.info("Generating Day 1 CRQ document...")
                day1_vars = {**base_template_vars, "day_number": "1"}
                day1_content = template.render(**day1_vars)
                
                day1_file = output_dir / "crq_day1.txt"
                with open(day1_file, "w", encoding="utf-8") as f:
                    f.write(day1_content)
                
                generated_files.append(day1_file)
                logger.info(f"Day 1 CRQ generated: {day1_file}")
                
                # Generate Day 2 CRQ  
                logger.info("Generating Day 2 CRQ document...")
                day2_vars = {**base_template_vars, "day_number": "2"}
                day2_content = template.render(**day2_vars)
                
                day2_file = output_dir / "crq_day2.txt"
                with open(day2_file, "w", encoding="utf-8") as f:
                    f.write(day2_content)
                    
                generated_files.append(day2_file)
                logger.info(f"Day 2 CRQ generated: {day2_file}")
                
            else:
                # Fallback to built-in templates
                logger.warning("Enterprise template not found, using built-in templates")
                
                # Generate Day 1 CRQ
                logger.info("Generating Day 1 CRQ document...")
                day1_template = create_day1_crq_template()
                day1_content = day1_template.render(**base_template_vars)
                
                day1_file = output_dir / "crq_day1.txt"
                with open(day1_file, "w", encoding="utf-8") as f:
                    f.write(day1_content)
                
                generated_files.append(day1_file)
                logger.info(f"Day 1 CRQ generated: {day1_file}")
                
                # Generate Day 2 CRQ  
                logger.info("Generating Day 2 CRQ document...")
                day2_template = create_day2_crq_template()
                day2_content = day2_template.render(**base_template_vars)
                
                day2_file = output_dir / "crq_day2.txt"
                with open(day2_file, "w", encoding="utf-8") as f:
                    f.write(day2_content)
                    
                generated_files.append(day2_file)
                logger.info(f"Day 2 CRQ generated: {day2_file}")
                
        except Exception as template_error:
            logger.error(f"Template processing failed: {template_error}")
            raise
        
        # Log preview of generated content
        if generated_files:
            for i, file_path in enumerate(generated_files, 1):
                if file_path.exists():
                    content = file_path.read_text()
                    logger.info(f"CRQ content preview - Day {i} (first 300 chars): {content[:300]}...")
        
        logger.info(f"Successfully generated {len(generated_files)} CRQ documents")
        return generated_files
        
    except Exception as e:
        logger.error(f"Failed to generate CRQ documents: {e}")
        raise 