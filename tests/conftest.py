#!/usr/bin/env python3
"""
Pytest configuration and fixtures for RC Release Agent tests.
"""

import os
import pytest
from pathlib import Path
from typing import Dict, Any, List
from types import SimpleNamespace

# Add project root to Python path for imports
import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config.config import load_config


@pytest.fixture
def params() -> Dict[str, Any]:
    """Default test parameters for release configuration."""
    return {
        "service_name": "test-service",
        "new_version": "v2.4.0", 
        "prod_version": "v2.3.1",
        "release_type": "standard",
        "rc_name": "Test RC",
        "rc_manager": "Test Manager",
        "day1_date": "2025-06-15",
        "day2_date": "2025-06-16",
        "config_path": "src/config/settings.yaml"
    }


@pytest.fixture
def prs() -> List:
    """Mock PR data for testing."""
    prs = []
    
    # Create diverse mock PRs with different categories
    pr_data = [
        {"number": 101, "title": "Add new user schema field", "author": "alice", "labels": ["schema"]},
        {"number": 102, "title": "Fix cart calculation bug", "author": "bob", "labels": ["bug", "cart"]},
        {"number": 103, "title": "Add internationalization support", "author": "carol", "labels": ["i18n", "feature"]},
        {"number": 104, "title": "Update dependency versions", "author": "dave", "labels": ["dependencies"]},
        {"number": 105, "title": "Improve tenant isolation", "author": "eve", "labels": ["tenant", "security"]},
    ]
    
    for pr_info in pr_data:
        pr = SimpleNamespace()
        pr.number = pr_info["number"]
        pr.title = pr_info["title"]
        pr.user = SimpleNamespace()
        pr.user.login = pr_info["author"]
        pr.user.display_name = f"{pr_info['author'].title()} (@{pr_info['author']})"
        pr.html_url = f"https://github.com/test/repo/pull/{pr_info['number']}"
        pr.labels = []
        
        for label_name in pr_info["labels"]:
            label = SimpleNamespace()
            label.name = label_name
            pr.labels.append(label)
            
        pr.body = f"Test PR: {pr_info['title']}"
        pr.merged = True
        prs.append(pr)
    
    return prs


@pytest.fixture
def output_dir(tmp_path) -> Path:
    """Temporary output directory for test files."""
    output_dir = tmp_path / "test_output"
    output_dir.mkdir(exist_ok=True)
    return output_dir


@pytest.fixture
def repo_name() -> str:
    """Test repository name."""
    return "test-org/test-repo"


@pytest.fixture
def old_tag() -> str:
    """Old git tag for testing."""
    return "v2.3.1"


@pytest.fixture
def new_tag() -> str:
    """New git tag for testing."""
    return "v2.4.0"


@pytest.fixture
def config():
    """Load test configuration."""
    try:
        return load_config()
    except Exception:
        # Return minimal config if loading fails
        from src.config.config import Settings, SlackConfig, GitHubConfig, AIConfig, OpenAIConfig, OrganizationConfig
        
        return Settings(
            slack=SlackConfig(
                bot_token="xoxb-test-token",
                signing_secret="test-secret"
            ),
            github=GitHubConfig(
                token="test-token",
                repo="test/repo"
            ),
            ai=AIConfig(
                provider="openai",
                openai=OpenAIConfig(api_key="test-key")
            ),
            organization=OrganizationConfig(
                name="Test Org",
                international_labels=["international", "i18n", "localization", "locale", "tenant", "multi-tenant"]
            )
        )


# Configure pytest settings
def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Suppress specific warnings for cleaner test output
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic")
    warnings.filterwarnings("ignore", category=UserWarning, module="pytest_asyncio")


# Add async support configuration
pytest_plugins = ('pytest_asyncio',) 