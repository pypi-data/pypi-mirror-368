import logging

from colorlog import ColoredFormatter


def setup_logging(verbose=False):
    log_level = logging.DEBUG if verbose else logging.INFO
    log_format = "%(log_color)s%(asctime)s %(levelname)s: %(message)s"

    formatter = ColoredFormatter(
        log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
        secondary_log_colors={},
        style="%",
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger = logging.getLogger("bfjira")
    logger.setLevel(log_level)
    logger.addHandler(handler)
    logger.propagate = False

    return logger
