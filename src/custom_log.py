import logging


def setup_logger(name, log_file, level=logging.CRITICAL):
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

