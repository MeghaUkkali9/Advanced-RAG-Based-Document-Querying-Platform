import logging
import os
from datetime import datetime
from pathlib import Path
import structlog

class CustomLogger:
    def __init__(self, log_dir="logs"):
        base_dir = Path(__file__).resolve().parent
        self.log_dir = base_dir / log_dir
        os.makedirs(self.log_dir, exist_ok=True)

        log_file = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
        self.log_file_path = os.path.join(self.log_dir, log_file)

    def get_logger(self, name=__file__):
        logger_name = os.path.basename(name)

        # Creating std logger
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)

        # Preventing duplicate handlers
        if not logger.handlers:
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")

            # File handler
            file_handler = logging.FileHandler(self.log_file_path)
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)

            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)

            logger.addHandler(file_handler)
            logger.addHandler(console_handler)

        # Proper structlog integration
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
                structlog.processors.add_log_level,
                structlog.processors.EventRenamer("event"),
                structlog.processors.JSONRenderer()
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        return structlog.get_logger(logger_name)
    
if __name__ == "__main__":
    custom_logger = CustomLogger()
    logger = custom_logger.get_logger(__file__)
    logger.info("custom 1111")