import json
import logging
import sys
import traceback
from datetime import datetime
from typing import Any, Dict, Optional

from pythonjsonlogger import jsonlogger


class DatadogJSONFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter optimized for Datadog ingestion"""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp in ISO format
        log_record['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        # Add standard fields for Datadog
        log_record['level'] = record.levelname
        log_record['logger_name'] = record.name
        log_record['service'] = 'tradewise-backend'
        log_record['environment'] = 'development'  # TODO: Make configurable
        
        # Add process/thread info
        log_record['process_id'] = record.process
        log_record['thread_id'] = record.thread
        
        # Add source location
        log_record['source'] = {
            'file': record.pathname,
            'line': record.lineno,
            'function': record.funcName
        }
        
        # Handle exceptions
        if record.exc_info:
            log_record['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
                'traceback': traceback.format_exception(*record.exc_info)
            }


def setup_logging(log_level: str = "INFO") -> None:
    """Setup JSON logging for the application"""
    
    # Create JSON formatter
    formatter = DatadogJSONFormatter(
        fmt='%(timestamp)s %(level)s %(logger_name)s %(message)s'
    )
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(console_handler)
    
    # Prevent duplicate logs
    root_logger.propagate = False
    
    # Setup specific loggers
    loggers = [
        'app',
        'uvicorn',
        'uvicorn.access',
        'uvicorn.error',
        'sqlalchemy.engine',
        'fastapi'
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, log_level.upper()))
        if not logger.handlers:
            logger.addHandler(console_handler)
        logger.propagate = False
    
    # Disable uvicorn access logs since we have our own middleware
    logging.getLogger("uvicorn.access").disabled = True


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance"""
    return logging.getLogger(f"app.{name}")


def log_api_request(
    method: str,
    path: str,
    user_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    request_id: Optional[str] = None,
    **kwargs
) -> None:
    """Log API request with structured data"""
    logger = get_logger("api")
    logger.info(
        "API request",
        extra={
            "event_type": "api_request",
            "http_method": method,
            "path": path,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "request_id": request_id,
            **kwargs
        }
    )


def log_api_response(
    method: str,
    path: str,
    status_code: int,
    response_time_ms: float,
    user_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    request_id: Optional[str] = None,
    **kwargs
) -> None:
    """Log API response with structured data"""
    logger = get_logger("api")
    logger.info(
        "API response",
        extra={
            "event_type": "api_response",
            "http_method": method,
            "path": path,
            "status_code": status_code,
            "response_time_ms": response_time_ms,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "request_id": request_id,
            **kwargs
        }
    )


def log_database_operation(
    operation: str,
    table: str,
    duration_ms: Optional[float] = None,
    rows_affected: Optional[int] = None,
    **kwargs
) -> None:
    """Log database operations"""
    logger = get_logger("database")
    logger.info(
        f"Database {operation}",
        extra={
            "event_type": "database_operation",
            "operation": operation,
            "table": table,
            "duration_ms": duration_ms,
            "rows_affected": rows_affected,
            **kwargs
        }
    )


def log_external_api_call(
    service: str,
    endpoint: str,
    method: str,
    status_code: Optional[int] = None,
    duration_ms: Optional[float] = None,
    **kwargs
) -> None:
    """Log external API calls"""
    logger = get_logger("external_api")
    logger.info(
        f"External API call to {service}",
        extra={
            "event_type": "external_api_call",
            "service": service,
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "duration_ms": duration_ms,
            **kwargs
        }
    )


def log_business_event(
    event_type: str,
    description: str,
    user_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    **kwargs
) -> None:
    """Log business events"""
    logger = get_logger("business")
    logger.info(
        description,
        extra={
            "event_type": f"business_{event_type}",
            "user_id": user_id,
            "tenant_id": tenant_id,
            **kwargs
        }
    )


def log_security_event(
    event_type: str,
    description: str,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    **kwargs
) -> None:
    """Log security-related events"""
    logger = get_logger("security")
    logger.warning(
        description,
        extra={
            "event_type": f"security_{event_type}",
            "user_id": user_id,
            "ip_address": ip_address,
            **kwargs
        }
    )