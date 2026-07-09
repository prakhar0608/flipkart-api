import logging
import sys

def setup_logger(name: str = "flipkart_ads_platform") -> logging.Logger:
    """
    Configures and returns a standard logger with system stdout stream handling.
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if logger is already configured
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Format logs clearly for stdout/stream consumption (e.g., Render/local terminal logs)
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        )
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger
