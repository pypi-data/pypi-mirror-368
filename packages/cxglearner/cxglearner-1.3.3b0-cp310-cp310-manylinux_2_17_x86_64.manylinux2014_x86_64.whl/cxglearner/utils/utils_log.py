import logging
from pathlib import Path
from datetime import datetime


def init_logger(config) -> logging.Logger:
    """
    Initialize the logger.
    :param config: The config class
    :return: logging.Logger
    """
    log_format = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
    logger = logging.getLogger()
    logger.setLevel(config.experiment.log_level)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    logger.handlers = [console_handler]

    if config.experiment.log_path is not None:
        log_path = Path(config.experiment.log_path)
        if log_path.suffix == '' or log_path.is_dir():
            if log_path.is_dir() or not log_path.suffix:
                current_date = datetime.now().strftime("%Y%m%d")
                log_file = log_path / f"{current_date}.log"
            else:
                log_file = log_path
        else:
            log_file = log_path

        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="UTF-8")
        file_handler.setLevel(config.experiment.log_file_level)
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)

    return logger
