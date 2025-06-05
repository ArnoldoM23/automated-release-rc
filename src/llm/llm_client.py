# src/llm/llm_client.py

import os
import logging
from typing import Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    WALMART_SANDBOX = "walmart_sandbox"

class LLMClient:
    """Multi-provider LLM client with fallback support."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider = LLMProvider(config.get("provider", "openai"))
        self.enabled = config.get("enabled", True)
        self.fallback_enabled = config.get("fallback_enabled", True)
        self.model = config.get("model", "gpt-4o-mini")
        self.max_tokens = config.get("max_tokens", 2000)
        self.temperature = config.get("temperature", 0.1)
        
        # Initialize provider-specific clients
        self._init_providers()
    
    def _init_providers(self):
        """Initialize provider-specific clients."""
        if self.provider == LLMProvider.WALMART_SANDBOX:
            from .wmt_gateway_adapter import call_llm as wmt_call_llm
            self._wmt_client = wmt_call_llm
        elif self.provider == LLMProvider.OPENAI:
            self._init_openai()
        elif self.provider == LLMProvider.ANTHROPIC:
            self._init_anthropic()
    
    def _init_openai(self):
        """Initialize OpenAI client."""
        try:
            import openai
            api_key = self.config.get("api_key") or os.getenv("OPENAI_API_KEY")
            if api_key:
                openai.api_key = api_key
                self._openai_client = openai
            else:
                logger.warning("OpenAI API key not found")
                self._openai_client = None
        except ImportError:
            logger.warning("OpenAI package not installed")
            self._openai_client = None
    
    def _init_anthropic(self):
        """Initialize Anthropic client."""
        try:
            import anthropic
            api_key = self.config.get("api_key") or os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self._anthropic_client = anthropic.Anthropic(api_key=api_key)
            else:
                logger.warning("Anthropic API key not found")
                self._anthropic_client = None
        except ImportError:
            logger.warning("Anthropic package not installed")
            self._anthropic_client = None
    
    def generate_response(self, prompt: str, max_tokens: Optional[int] = None, temperature: Optional[float] = None) -> Optional[str]:
        """Generate a response using the configured LLM provider."""
        if not self.enabled:
            logger.info("LLM is disabled, skipping generation")
            return None
        
        # Use provided parameters or defaults
        max_tokens = max_tokens or self.max_tokens
        temperature = temperature or self.temperature
        
        try:
            if self.provider == LLMProvider.WALMART_SANDBOX:
                return self._call_walmart_llm(prompt, max_tokens, temperature)
            elif self.provider == LLMProvider.OPENAI:
                return self._call_openai(prompt, max_tokens, temperature)
            elif self.provider == LLMProvider.ANTHROPIC:
                return self._call_anthropic(prompt, max_tokens, temperature)
        except Exception as e:
            logger.error(f"LLM generation failed with {self.provider.value}: {e}")
            if self.fallback_enabled:
                return self._try_fallback_providers(prompt, max_tokens, temperature)
            return None
    
    def _call_walmart_llm(self, prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """Call Walmart LLM gateway."""
        return self._wmt_client(prompt, max_tokens, temperature)
    
    def _call_openai(self, prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """Call OpenAI API."""
        if not self._openai_client:
            raise Exception("OpenAI client not initialized")
        
        response = self._openai_client.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content
    
    def _call_anthropic(self, prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """Call Anthropic API."""
        if not self._anthropic_client:
            raise Exception("Anthropic client not initialized")
        
        response = self._anthropic_client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    
    def _try_fallback_providers(self, prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """Try fallback providers if primary fails."""
        fallback_order = [LLMProvider.OPENAI, LLMProvider.ANTHROPIC, LLMProvider.WALMART_SANDBOX]
        
        # Remove current provider from fallback list
        if self.provider in fallback_order:
            fallback_order.remove(self.provider)
        
        for fallback_provider in fallback_order:
            try:
                logger.info(f"Trying fallback provider: {fallback_provider.value}")
                original_provider = self.provider
                self.provider = fallback_provider
                self._init_providers()
                
                if fallback_provider == LLMProvider.WALMART_SANDBOX:
                    result = self._call_walmart_llm(prompt, max_tokens, temperature)
                elif fallback_provider == LLMProvider.OPENAI:
                    result = self._call_openai(prompt, max_tokens, temperature)
                elif fallback_provider == LLMProvider.ANTHROPIC:
                    result = self._call_anthropic(prompt, max_tokens, temperature)
                
                if result:
                    logger.info(f"Fallback successful with {fallback_provider.value}")
                    # Restore original provider
                    self.provider = original_provider
                    return result
                    
            except Exception as e:
                logger.warning(f"Fallback provider {fallback_provider.value} also failed: {e}")
                continue
        
        logger.error("All LLM providers failed")
        return None
    
    def generate_crq(self, release_notes: str, settings_yaml: str) -> Optional[str]:
        """Generate CRQ document using LLM."""
        from .prompt_templates import generate_crq_prompt
        
        prompt = generate_crq_prompt(release_notes, settings_yaml)
        return self.generate_response(prompt, max_tokens=2000, temperature=0.1)
    
    def generate_release_summary(self, pr_list: list, exclude_international: bool = True) -> Optional[str]:
        """Generate release summary using LLM."""
        from .prompt_templates import generate_release_summary_prompt
        
        prompt = generate_release_summary_prompt(pr_list, exclude_international)
        return self.generate_response(prompt, max_tokens=500, temperature=0.1)
    
    def analyze_pr(self, pr_title: str, pr_body: str) -> Optional[str]:
        """Analyze PR using LLM."""
        from .prompt_templates import generate_pr_analysis_prompt
        
        prompt = generate_pr_analysis_prompt(pr_title, pr_body)
        return self.generate_response(prompt, max_tokens=300, temperature=0.1) 