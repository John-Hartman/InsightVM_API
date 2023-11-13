# Logging class

import logging
import sys


class Logger:
    def __init__(self):
        self.logger = logging.getLogger(sys.modules[self.__module__].__name__)
