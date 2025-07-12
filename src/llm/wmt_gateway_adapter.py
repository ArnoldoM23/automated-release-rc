# src/llm/wmt_gateway_adapter.py

import os
import requests
import logging
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Walmart-specific certificate setup (cross-platform compatible)
# Only set custom SSL paths if running on expected corporate environment
if os.path.exists("/etc/ssl/certs/ca-bundle.crt"):
    WMT_CA_PATH = "/etc/ssl/certs/ca-bundle.crt"
    os.environ["SSL_CERT_FILE"] = WMT_CA_PATH
    os.environ["REQUESTS_CA_BUNDLE"] = WMT_CA_PATH
    logger.info("Using corporate SSL certificate bundle")
else:
    # Use system default SSL certificates on macOS/Windows/other systems
    logger.info("Using system default SSL certificates")

# LLM Gateway config
LLM_GATEWAY_URL = os.getenv("WMT_LLM_API_URL")  # Get URL from environment variable
API_KEY = os.getenv("WMT_LLM_API_KEY")  # Must be set in .env or environment

def call_llm(prompt: str, max_tokens: int = 300, temperature: float = 0.7) -> Optional[str]:
    """Send a prompt to Walmart's internal LLM Gateway."""
    
    # Check if configuration is available
    if not LLM_GATEWAY_URL or not API_KEY:
        logger.warning("LLM Gateway not configured (missing WMT_LLM_API_URL or WMT_LLM_API_KEY), skipping LLM call")
        return None
    
    headers = {
        "X-Api-Key": API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini",
        "model-version": "2024-07-18",
        "api-version": "2024-10-21",
        "task": "chat/completions",
        "model-params": {
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
    }

    try:
        # v4.0 Fix: Add short timeout to prevent hanging on unreachable internal URLs
        response = requests.post(LLM_GATEWAY_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        logger.error(f"LLM Gateway request failed: {e}")
        return None 