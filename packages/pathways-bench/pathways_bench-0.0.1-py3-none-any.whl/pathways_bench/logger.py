import logging

def get_logger(name=__name__, debug=False):
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    return logger
