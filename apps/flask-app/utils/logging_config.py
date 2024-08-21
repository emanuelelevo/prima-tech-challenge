import logging
from pythonjsonlogger import jsonlogger

def setup_logging(app):
    logger = logging.getLogger()
    level = getattr(logging, app.config['LOG_LEVEL'].upper(), logging.ERROR)
    logger.setLevel(level)
    
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(levelname)s %(name)s %(message)s'
    )
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
