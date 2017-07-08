#!/usr/bin/env python

import logging
import sys


class ShutdownHandler(logging.Handler):
    def emit(self, record):
        logging.shutdown()
        sys.exit(1)


def get_my_logger(name):
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))

    logger = logging.getLogger(name)
    logger.handlers[:] = [handler]
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(ShutdownHandler(level=50))

    return logger
