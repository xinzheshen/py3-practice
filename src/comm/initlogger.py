#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Init logger
"""


import logging
from logging import handlers


def init_logger(file_name=None, cfg_file=None):
    if cfg_file is None:
        formatter = logging.Formatter("[%(levelname)s]%(asctime)s %(filename)s:%(lineno)d : %(message)s")
        std_handler = logging.StreamHandler()
        std_handler.setFormatter(formatter)
        if file_name is None:
            file_name = 'debug.log'
        file_handler = handlers.RotatingFileHandler(file_name)
        file_handler.setFormatter(formatter)
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(std_handler)
        root_logger.addHandler(file_handler)
    else:
        logging.config.fileConfig(cfg_file)
