import logging
import json
from typing import Dict, Any
from datetime import datetime

class StructuredLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
            
        return json.dumps(log_data)

class LoggingHandler:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(config['logger_name'])
        self.logger.setLevel(config['log_level'])
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(StructuredLogFormatter())
        self.logger.addHandler(console_handler)
        
        # Create file handler if configured
        if 'log_file' in config:
            file_handler = logging.FileHandler(config['log_file'])
            file_handler.setFormatter(StructuredLogFormatter())
            self.logger.addHandler(file_handler)

    def log(self, level: str, message: str, extra: Dict[str, Any] = None):
        """Log message with additional context"""
        log_method = getattr(self.logger, level.lower())
        log_method(message, extra=extra)

    def debug(self, message: str, extra: Dict[str, Any] = None):
        self.log('debug', message, extra)

    def info(self, message: str, extra: Dict[str, Any] = None):
        self.log('info', message, extra)

    def warning(self, message: str, extra: Dict[str, Any] = None):
        self.log('warning', message, extra)

    def error(self, message: str, extra: Dict[str, Any] = None):
        self.log('error', message, extra)

    def critical(self, message: str, extra: Dict[str, Any] = None):
        self.log('critical', message, extra)
