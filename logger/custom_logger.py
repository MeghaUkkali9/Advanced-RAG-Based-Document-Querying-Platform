import logging
import os
from datetime import datetime
import structlog

class CustomLogger:
    def __init__(self, log_dir="logs"):
        os.makedirs(log_dir, exist_ok=True)
        self.log_dir = os.path.join(os.getcwd(), log_dir)

        log_file = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
        self.log_file_path = os.path.join(self.log_dir, log_file)

    def get_logger(self, name=__file__):
        logger_name = os.path.basename(name)

        file_handler = logging.FileHandler(self.log_file_path)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(message)s")
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            handlers=[file_handler, console_handler]
        )

        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
                structlog.processors.add_log_level,
                structlog.processors.EventRenamer(to='event'),
                structlog.processors.JSONRenderer()
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        return structlog.get_logger(logger_name)

if __name__ == "__main__":
    custom_logger = CustomLogger()
    logger = custom_logger.get_logger(__file__)
    logger.info("custom 1111")