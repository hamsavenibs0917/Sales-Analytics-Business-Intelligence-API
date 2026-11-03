import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(app):
    """
    Configure application logging with rotating file handler and console handler.
    """
    log_level_name = app.config.get("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    log_file_path = app.config.get("LOG_FILE", "logs/app.log")
    log_dir = os.path.dirname(log_file_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(name)s.%(module)s:%(lineno)d] %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    handlers = [console_handler]

    # File handler (10 MB per file, keep 5 rotating backups)
    try:
        file_handler = RotatingFileHandler(
            log_file_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        handlers.append(file_handler)
    except Exception as e:
        print(f"Warning: Could not initialize rotating file logger: {e}")

    # Configure root/app logger
    app.logger.handlers.clear()
    for h in handlers:
        app.logger.addHandler(h)
    app.logger.setLevel(log_level)

    # Silence excessive werkzeug request logs in production
    logging.getLogger("werkzeug").setLevel(logging.WARNING if not app.debug else logging.INFO)
    
    app.logger.info("Application logger initialized successfully at level: %s", log_level_name)
