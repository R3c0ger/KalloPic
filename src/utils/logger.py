#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import warnings
from logging.handlers import RotatingFileHandler

from src.config import Conf


def setup_logger(level=logging.INFO, log_file=None):
    logger = logging.getLogger('appLogger')
    logger.setLevel(level)

    # 捕获警告
    def warning_to_log(message, category, filename, lineno, file=None, line=None):
        logger.warning(f'{filename}:{lineno}: {category.__name__}: {message}')

    warnings.showwarning = warning_to_log

    # 创建输出到控制台的handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    formatter = logging.Formatter(
        fmt='[ %(asctime)s | %(name)s ] %(message)s',
        datefmt='%Y/%m/%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 如果不需要写入文件，直接返回logger；否则创建文件
    if not log_file:
        return logger
    try:
        log_relpath = os.path.dirname(log_file)
        if not os.path.exists(log_relpath):
            os.makedirs(log_relpath)
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write('')
    except Exception as e:
        raise e

    # 创建输出到文件的handler
    file_handler = RotatingFileHandler(log_file, maxBytes=1048576, backupCount=5)
    file_handler.setLevel(level)
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y/%m/%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


Logger = setup_logger(
    level=Conf.LOG_LEVEL,
    log_file=Conf.LOG_RELPATH
)
