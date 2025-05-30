# RC Release Agent - Main Package

"""
RC Release Automation Agent

Automated Release Workflow System for RC Release Coordination.

Author: Arnoldo Munoz
Version: 1.0.0
License: Proprietary
"""

__version__ = "1.0.0"
__author__ = "Arnoldo Munoz"
__email__ = "arnoldomunoz23@gmail.com"
__license__ = "Proprietary"
__description__ = "Automated Release Workflow System for RC Release Coordination"

# Package metadata
from pathlib import Path

# Main modules
from .config.config import load_config
from .utils.logging import get_logger

__all__ = [
    "load_config",
    "get_logger",
    "__version__",
    "__author__",
    "__license__",
]

"""
This package provides:
- CLI automation for release coordination
- GitHub Actions integration  
- Slack automation for sign-off collection
- CRQ document generation
- Enterprise compliance tools
""" 