import logging

LOG_LEVEL_MAP = {"info": logging.INFO, "debug": logging.DEBUG, "error": logging.ERROR}


def get_logger(name: str, log_level: str = "info"):
    logging.basicConfig(
        level=LOG_LEVEL_MAP[log_level],
        format="[%(asctime)s] {{%(filename)s:%(lineno)d}} %(levelname)s - %(message)s",
        force=True,
    )
    return logging.getLogger(name)
