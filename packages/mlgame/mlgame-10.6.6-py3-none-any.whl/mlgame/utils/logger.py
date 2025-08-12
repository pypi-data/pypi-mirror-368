import sys
from functools import cache

import loguru

_logger = None


@cache
def get_singleton_logger():
    global _logger
    if _logger is None:
        # logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

        _logger = loguru.logger

        _logger.remove()
        _logger.add(
            sys.stdout,
            level="INFO",
            format='<green>{time:YYYY-MM-DD HH:mm:ss.SSSSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>'
        )


    return _logger


logger = get_singleton_logger()
