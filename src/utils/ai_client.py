"""
Multi-provider AI client for generating CRQ content and release notes.
Supports OpenAI, Azure OpenAI, and Anthropic with fallback mechanisms.
"""

import time
from typing import List, Dict, Any, Optional, Union
from abc import ABC, abstractmethod

import openai
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from config.config import AIConfig, OpenAIConfig, AzureOpenAIConfig, AnthropicConfig
from utils.logging import get_logger, log_api_call


class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    def generate_text(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate text using the AI provider."""
        pass


class OpenAIProvider(AIProvider):
    """OpenAI provider implementation."""
    
    def __init__(self, config: OpenAIConfig):
        self.config = config
        self.client = openai.OpenAI(
            api_key=config.api_key,
            base_url=config.api_base
        )
        self.logger = get_logger(__name__)
    
    def generate_text(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate text using OpenAI API."""
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates professional technical documentation."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.3  # Lower temperature for more consistent outputs
            )
            
            duration_ms = (time.time() - start_time) * 1000
            log_api_call(
                self.logger, 
                service="openai", 
                endpoint=f"/chat/completions/{self.config.model}",
                method="POST",
                status_code=200,
                duration_ms=duration_ms
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_api_call(
                self.logger,
                service="openai",
                endpoint=f"/chat/completions/{self.config.model}",
                method="POST", 
                status_code=500,
                duration_ms=duration_ms
            )
            raise Exception(f"OpenAI API call failed: {e}")


class AzureOpenAIProvider(AIProvider):
    """Azure OpenAI provider implementation."""
    
    def __init__(self, config: AzureOpenAIConfig):
        self.config = config
        self.client = openai.AzureOpenAI(
            api_key=config.api_key,
            api_version=config.api_version,
            azure_endpoint=config.endpoint
        )
        self.logger = get_logger(__name__)
    
    def generate_text(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate text using Azure OpenAI API."""
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.deployment,  # Use deployment name for Azure
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates professional technical documentation."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.3
            )
            
            duration_ms = (time.time() - start_time) * 1000
            log_api_call(
                self.logger,
                service="azure_openai",
                endpoint=f"/chat/completions/{self.config.deployment}",
                method="POST",
                status_code=200,
                duration_ms=duration_ms
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_api_call(
                self.logger,
                service="azure_openai", 
                endpoint=f"/chat/completions/{self.config.deployment}",
                method="POST",
                status_code=500,
                duration_ms=duration_ms
            )
            raise Exception(f"Azure OpenAI API call failed: {e}")


class AnthropicProvider(AIProvider):
    """Anthropic Claude provider implementation."""
    
    def __init__(self, config: AnthropicConfig):
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic package is not installed")
        
        self.config = config
        self.client = anthropic.Anthropic(api_key=config.api_key)
        self.logger = get_logger(__name__)
    
    def generate_text(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate text using Anthropic Claude API."""
        start_time = time.time()
        
        try:
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=max_tokens,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            duration_ms = (time.time() - start_time) * 1000
            log_api_call(
                self.logger,
                service="anthropic",
                endpoint=f"/messages/{self.config.model}",
                method="POST",
                status_code=200,
                duration_ms=duration_ms
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_api_call(
                self.logger,
                service="anthropic",
                endpoint=f"/messages/{self.config.model}",
                method="POST",
                status_code=500,
                duration_ms=duration_ms
            )
            raise Exception(f"Anthropic API call failed: {e}")


class AIClient:
    """
    Multi-provider AI client with fallback mechanisms.
    """
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.logger = get_logger(__name__)
        self.providers: List[AIProvider] = []
        
        # Initialize primary provider
        if config.provider == "openai" and config.openai:
            self.providers.append(OpenAIProvider(config.openai))
        elif config.provider == "azure" and config.azure:
            self.providers.append(AzureOpenAIProvider(config.azure))
        elif config.provider == "anthropic" and config.anthropic:
            if ANTHROPIC_AVAILABLE:
                self.providers.append(AnthropicProvider(config.anthropic))
            else:
                self.logger.warning("Anthropic provider selected but anthropic package not available")
        
        # Add fallback providers
        if config.provider != "openai" and config.openai:
            self.providers.append(OpenAIProvider(config.openai))
        
        if config.provider != "azure" and config.azure:
            self.providers.append(AzureOpenAIProvider(config.azure))
        
        if config.provider != "anthropic" and config.anthropic and ANTHROPIC_AVAILABLE:
            self.providers.append(AnthropicProvider(config.anthropic))
        
        if not self.providers:
            raise ValueError("No AI providers configured")
        
        self.logger.info(f"Initialized AI client with {len(self.providers)} provider(s)")
    
    def generate_text(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Generate text using the configured AI provider with fallback.
        
        Args:
            prompt: Text prompt for generation
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
            
        Raises:
            Exception: If all providers fail
        """
        errors = []
        
        for i, provider in enumerate(self.providers):
            try:
                self.logger.info(f"Attempting text generation with provider {i+1}/{len(self.providers)}")
                result = provider.generate_text(prompt, max_tokens)
                self.logger.info(f"Text generation successful with provider {i+1}")
                return result
                
            except Exception as e:
                error_msg = f"Provider {i+1} failed: {e}"
                errors.append(error_msg)
                self.logger.warning(error_msg)
                
                if i < len(self.providers) - 1:
                    self.logger.info(f"Falling back to provider {i+2}")
                    continue
        
        # All providers failed
        error_summary = "; ".join(errors)
        raise Exception(f"All AI providers failed: {error_summary}")
    
    def generate_crq_responses(self, prs: List[Any], params: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate AI-powered responses for CRQ questions.
        
        Args:
            prs: List of pull request objects
            params: Release parameters from modal
            
        Returns:
            Dictionary of question responses
        """
        # Prepare context from PRs
        pr_context = self._format_prs_for_context(prs)
        
        # Generate responses for each CRQ question
        questions = {
            "criticality": "What is the criticality of this change or why is this change required?",
            "validation": "How have we validated this change in the lower environment?", 
            "blast_radius": "What is the blast radius of this change?",
            "testing_risk_reduction": "Describe how testing has reduced risk for the deployment?",
            "issue_response": "What happens if we encounter an issue during release?",
            "customer_impact_controls": "What controls do we have to minimize the impact to our customers?",
            "monitoring": "What monitoring is in place to determine the errors?"
        }
        
        responses = {}
        
        for key, question in questions.items():
            prompt = self._build_crq_prompt(question, pr_context, params)
            try:
                response = self.generate_text(prompt, max_tokens=300)
                responses[key] = response
            except Exception as e:
                self.logger.warning(f"Failed to generate AI response for {key}: {e}")
                responses[key] = f"[AI generation failed for {key}. Please fill in manually.]"
        
        return responses
    
    def _format_prs_for_context(self, prs: List[Any]) -> str:
        """Format pull requests for AI context."""
        if not prs:
            return "No pull requests found in this release."
        
        context_lines = []
        for pr in prs[:10]:  # Limit to first 10 PRs to avoid token limits
            labels = ", ".join([label.name for label in pr.labels]) if pr.labels else "None"
            context_lines.append(
                f"- PR #{pr.number}: {pr.title} (Author: {pr.user.login}, Labels: {labels})"
            )
        
        if len(prs) > 10:
            context_lines.append(f"... and {len(prs) - 10} more pull requests")
        
        return "\n".join(context_lines)
    
    def _build_crq_prompt(self, question: str, pr_context: str, params: Dict[str, Any]) -> str:
        """Build a prompt for CRQ question generation."""
        return f"""
You are a technical writer creating a Change Request (CRQ) document for a software deployment.

Service: {params.get('service_name', 'Unknown')}
Release Type: {params.get('release_type', 'standard')}
Version: {params.get('production_version', 'Unknown')} → {params.get('new_version', 'Unknown')}

Pull Requests in this release:
{pr_context}

Question: {question}

Please provide a professional, technical response (2-3 sentences) that would be appropriate for a production deployment CRQ. Focus on:
- Technical accuracy
- Risk mitigation
- Professional tone
- Specific to this release context

Response:"""
    
    def generate_release_summary(self, prs: List[Any], params: Dict[str, Any]) -> str:
        """
        Generate a summary of the release for release notes.
        
        Args:
            prs: List of pull request objects
            params: Release parameters
            
        Returns:
            Release summary text
        """
        pr_context = self._format_prs_for_context(prs)
        
        prompt = f"""
Create a professional release summary for the following software deployment:

Service: {params.get('service_name', 'Unknown')}
Version: {params.get('production_version', 'Unknown')} → {params.get('new_version', 'Unknown')}
Release Type: {params.get('release_type', 'standard')}

Changes in this release:
{pr_context}

Please provide a concise, professional summary (3-4 sentences) highlighting:
- Key features and improvements
- Bug fixes (if any)
- Overall impact and benefits

Summary:"""

        try:
            return self.generate_text(prompt, max_tokens=200)
        except Exception as e:
            self.logger.warning(f"Failed to generate release summary: {e}")
            return f"Release {params.get('new_version', 'Unknown')} includes {len(prs)} changes with improvements and bug fixes." 