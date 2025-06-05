"""
LLM Integration Module for RC Release Agent

This module provides multi-provider LLM integration for:
- CRQ generation automation
- Release summary creation  
- PR analysis enhancement
- Walmart LLM gateway integration

Supports providers: OpenAI, Anthropic, Walmart sandbox
"""

__version__ = "3.0.0"
__author__ = "Arnoldo Munoz"

from .wmt_gateway_adapter import call_llm
from .prompt_templates import (
    generate_crq_prompt,
    generate_release_summary_prompt,
    generate_pr_analysis_prompt
)
from .llm_client import LLMClient, LLMProvider

__all__ = [
    "call_llm",
    "generate_crq_prompt",
    "generate_release_summary_prompt", 
    "generate_pr_analysis_prompt",
    "LLMClient",
    "LLMProvider"
] 