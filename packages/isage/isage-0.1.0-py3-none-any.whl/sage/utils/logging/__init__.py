"""
Logging utilities module

Re-exports logging functionality from sage.common.utils.logging
"""

try:
    from sage.common.utils.logging.custom_logger import CustomLogger
    from sage.common.utils.logging.custom_formatter import CustomFormatter
except ImportError:
    # Fallback if sage-common is not available
    import logging
    
    class CustomLogger:
        def __init__(self, outputs=None, name="SAGE", log_base_folder="./logs"):
            self.logger = logging.getLogger(name)
            if not self.logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
                self.logger.setLevel(logging.INFO)
        
        def info(self, msg):
            self.logger.info(msg)
        
        def debug(self, msg):
            self.logger.debug(msg)
        
        def warning(self, msg):
            self.logger.warning(msg)
        
        def error(self, msg):
            self.logger.error(msg)
    
    class CustomFormatter:
        pass

__all__ = [
    "CustomLogger",
    "CustomFormatter"
]
