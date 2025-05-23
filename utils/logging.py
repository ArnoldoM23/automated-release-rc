"""
Structured logging configuration for Automated RC Release Workflow.
Uses structlog for consistent, structured logging across the application.
"""

import logging
import logging.config
import sys
from typing import Any, Dict

import structlog
from structlog.stdlib import add_log_level, filter_by_level


def configure_logging(log_level: str = "INFO", environment: str = "development") -> None:
    """
    Configure structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        environment: Environment (development, staging, production)
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=numeric_level,
    )
    
    # Define processors based on environment
    if environment == "development":
        # Human-readable format for development
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    else:
        # JSON format for production
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ]
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


def add_request_id(request_id: str) -> Dict[str, Any]:
    """
    Create a logging context with request ID for tracking.
    
    Args:
        request_id: Unique request identifier
        
    Returns:
        Context dictionary for structlog
    """
    return {"request_id": request_id}


def log_function_call(logger: structlog.stdlib.BoundLogger, function_name: str, **kwargs):
    """
    Log function calls with parameters (useful for debugging).
    
    Args:
        logger: Structlog logger instance
        function_name: Name of the function being called
        **kwargs: Function parameters to log
    """
    logger.debug(
        "Function called",
        function=function_name,
        parameters=kwargs
    )


def log_api_call(logger: structlog.stdlib.BoundLogger, service: str, endpoint: str, 
                method: str = "GET", status_code: int = None, duration_ms: float = None):
    """
    Log external API calls for monitoring and debugging.
    
    Args:
        logger: Structlog logger instance
        service: Service name (e.g., "github", "slack", "openai")
        endpoint: API endpoint
        method: HTTP method
        status_code: Response status code
        duration_ms: Request duration in milliseconds
    """
    log_data = {
        "api_call": True,
        "service": service,
        "endpoint": endpoint,
        "method": method
    }
    
    if status_code is not None:
        log_data["status_code"] = status_code
    
    if duration_ms is not None:
        log_data["duration_ms"] = duration_ms
    
    if status_code and status_code >= 400:
        logger.warning("API call failed", **log_data)
    else:
        logger.info("API call completed", **log_data)


def log_workflow_step(logger: structlog.stdlib.BoundLogger, step: str, status: str, 
                     duration_ms: float = None, **context):
    """
    Log workflow steps for tracking release process progress.
    
    Args:
        logger: Structlog logger instance
        step: Workflow step name
        status: Step status (started, completed, failed)
        duration_ms: Step duration in milliseconds
        **context: Additional context information
    """
    log_data = {
        "workflow_step": step,
        "status": status,
        **context
    }
    
    if duration_ms is not None:
        log_data["duration_ms"] = duration_ms
    
    if status == "failed":
        logger.error("Workflow step failed", **log_data)
    elif status == "completed":
        logger.info("Workflow step completed", **log_data)
    else:
        logger.info("Workflow step started", **log_data)


# Initialize logging on module import
try:
    # Try to get configuration from environment or config
    import os
    log_level = os.getenv("LOG_LEVEL", "INFO")
    environment = os.getenv("ENVIRONMENT", "development")
    configure_logging(log_level, environment)
except Exception:
    # Fallback to basic configuration
    configure_logging()


# Create a default logger for this module
logger = get_logger(__name__)
logger.info("Logging system initialized") 