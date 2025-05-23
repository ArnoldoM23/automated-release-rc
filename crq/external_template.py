#!/usr/bin/env python3
"""
External CRQ Template Downloader and Processor.
Supports downloading CRQ templates from external sources like Microsoft Word documents,
text files, etc., and converting them to Jinja2 templates.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
import requests
from datetime import datetime, timedelta

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False

from utils.logging import get_logger


class ExternalTemplateManager:
    """Manages downloading and processing of external CRQ templates."""
    
    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__)
        self.cache_dir = Path("cache/templates")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_cached_template_path(self, template_url: str) -> Path:
        """Generate cache file path for a template URL."""
        # Create safe filename from URL
        safe_name = template_url.replace('/', '_').replace(':', '_').replace('?', '_')[:100]
        timestamp = datetime.now().strftime("%Y%m%d")
        return self.cache_dir / f"crq_template_{safe_name}_{timestamp}.j2"
    
    def is_cache_valid(self, cache_path: Path, cache_duration: int) -> bool:
        """Check if cached template is still valid."""
        if not cache_path.exists():
            return False
        
        file_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
        return file_age.total_seconds() < cache_duration
    
    def download_template(self, template_url: str) -> Optional[str]:
        """Download template content from URL."""
        try:
            self.logger.info(f"Downloading CRQ template from: {template_url}")
            
            headers = {
                'User-Agent': 'RC-Release-Automation/1.0'
            }
            
            response = requests.get(template_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Detect content type
            content_type = response.headers.get('content-type', '').lower()
            
            if 'word' in content_type or template_url.endswith(('.docx', '.doc')):
                return self.process_word_document(response.content)
            elif 'text' in content_type or template_url.endswith('.txt'):
                return response.text
            elif 'markdown' in content_type or template_url.endswith('.md'):
                return self.process_markdown(response.text)
            else:
                # Default to text processing
                return response.text
                
        except Exception as e:
            self.logger.error(f"Failed to download template from {template_url}: {e}")
            return None
    
    def process_word_document(self, content: bytes) -> Optional[str]:
        """Process Microsoft Word document content."""
        if not DOCX_AVAILABLE:
            self.logger.warning("python-docx not installed, cannot process Word documents")
            return None
        
        try:
            # Save content to temporary file
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_file:
                tmp_file.write(content)
                tmp_file_path = tmp_file.name
            
            # Read with python-docx
            doc = docx.Document(tmp_file_path)
            
            # Extract text content
            text_content = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_content.append(paragraph.text)
            
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
            # Convert to Jinja2 template format
            return self.convert_to_jinja_template('\n'.join(text_content))
            
        except Exception as e:
            self.logger.error(f"Failed to process Word document: {e}")
            if 'tmp_file_path' in locals():
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass
            return None
    
    def process_markdown(self, content: str) -> Optional[str]:
        """Process Markdown content."""
        try:
            # Convert markdown to plain text for template processing
            if MARKDOWN_AVAILABLE:
                # Remove markdown formatting for template
                import re
                # Simple markdown removal - could be enhanced
                content = re.sub(r'[*_`#]', '', content)
            
            return self.convert_to_jinja_template(content)
            
        except Exception as e:
            self.logger.error(f"Failed to process Markdown content: {e}")
            return None
    
    def convert_to_jinja_template(self, content: str) -> str:
        """Convert plain text content to Jinja2 template format."""
        try:
            # Replace common placeholders with Jinja2 variables
            replacements = {
                # Service information
                r'\{?service[_\s]?name\}?': '{{ service_name }}',
                r'\{?application[_\s]?name\}?': '{{ service_name }}',
                r'\{?namespace\}?': '{{ namespace }}',
                r'\{?assembly\}?': '{{ assembly }}',
                r'\{?platform\}?': '{{ platform }}',
                
                # Versions
                r'\{?new[_\s]?version\}?': '{{ new_version }}',
                r'\{?prod[_\s]?version\}?': '{{ prod_version }}',
                r'\{?forward[_\s]?version\}?': '{{ new_version }}',
                r'\{?rollback[_\s]?version\}?': '{{ prod_version }}',
                
                # Regions
                r'\{?regions?\}?': '{{ regions | join(" and ") }}',
                r'\{?deployment[_\s]?regions?\}?': '{{ regions | join(", ") }}',
                
                # Day number
                r'\{?day[_\s]?number\}?': '{{ day_number }}',
                r'\{?day[_\s]?type\}?': '{{ day_number }}',
                
                # URLs and links
                r'\{?confluence[_\s]?link\}?': '{{ confluence_link }}',
                r'\{?dashboard[_\s]?url\}?': '{{ confluence_dashboard_url }}',
                r'\{?p0[_\s]?dashboard[_\s]?url\}?': '{{ p0_dashboard_url }}',
                r'\{?l1[_\s]?dashboard[_\s]?url\}?': '{{ l1_dashboard_url }}',
                r'\{?services[_\s]?dashboard[_\s]?url\}?': '{{ services_dashboard_url }}',
                r'\{?wcnp[_\s]?dashboard[_\s]?url\}?': '{{ wcnp_dashboard_url }}',
                r'\{?istio[_\s]?dashboard[_\s]?url\}?': '{{ istio_dashboard_url }}',
                r'\{?grafana[_\s]?url\}?': '{{ p0_dashboard_url }}',  # Legacy support
                
                # Conditional sections for Day 1/2
                r'Day\s+1\s*[-:]?\s*': '{% if day_number == "1" %}Day 1:',
                r'Day\s+2\s*[-:]?\s*': '{% else %}Day 2:',
            }
            
            import re
            template_content = content
            
            for pattern, replacement in replacements.items():
                template_content = re.sub(pattern, replacement, template_content, flags=re.IGNORECASE)
            
            # Add conditional ending if we added conditionals
            if '{% if day_number == "1" %}' in template_content and '{% endif %}' not in template_content:
                template_content += '\n{% endif %}'
            
            return template_content
            
        except Exception as e:
            self.logger.error(f"Failed to convert content to Jinja2 template: {e}")
            return content  # Return original content as fallback
    
    def get_external_template(self) -> Optional[str]:
        """Get external template content, using cache if valid."""
        if not self.config.external_template.enabled:
            return None
        
        if not self.config.external_template.template_url:
            self.logger.warning("External template enabled but no URL provided")
            return None
        
        template_url = self.config.external_template.template_url
        cache_path = self.get_cached_template_path(template_url)
        
        # Check cache first
        if self.is_cache_valid(cache_path, self.config.external_template.cache_duration):
            self.logger.info(f"Using cached external template: {cache_path}")
            try:
                return cache_path.read_text(encoding='utf-8')
            except Exception as e:
                self.logger.warning(f"Failed to read cached template: {e}")
        
        # Download fresh template
        template_content = self.download_template(template_url)
        
        if template_content:
            # Cache the template
            try:
                cache_path.write_text(template_content, encoding='utf-8')
                self.logger.info(f"Cached external template: {cache_path}")
            except Exception as e:
                self.logger.warning(f"Failed to cache template: {e}")
            
            return template_content
        
        # If download failed and fallback is enabled, return None to use built-in
        if self.config.external_template.fallback_to_builtin:
            self.logger.info("External template download failed, falling back to built-in template")
            return None
        
        # If no fallback, this is an error
        raise Exception(f"Failed to download external template and fallback is disabled")


def install_dependencies():
    """Install optional dependencies for external template processing."""
    dependencies = []
    
    if not DOCX_AVAILABLE:
        dependencies.append("python-docx")
    
    if not MARKDOWN_AVAILABLE:
        dependencies.append("markdown")
    
    if dependencies:
        print(f"To support external templates, install: pip install {' '.join(dependencies)}")
        return False
    
    return True 