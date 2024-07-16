#!usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import sys


# noinspection PyBroadException,PyProtectedMember
def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("..")
    return os.path.join(base_path, relative_path)


class Config:
    # Metadata
    PROJECT_NAME = "KalloPic"
    PROJECT_NAME_LOWER = PROJECT_NAME.lower()
    VERSION = "0.2.1"
    AUTHOR = "Recogeta"
    DESCRIPTION = "Folder-based picture viewer, filter and archiver."
    URL = 'https://github.com/R3c0ger/KalloPic'
    BUG_REPORT_URL = URL + '/issues'
    BANNER = """
    ██╗░░██╗░█████╗░██╗░░░░░██╗░░░░░░█████╗░██████╗░██╗░█████╗░
    ██║░██╔╝██╔══██╗██║░░░░░██║░░░░░██╔══██╗██╔══██╗██║██╔══██╗
    █████═╝░███████║██║░░░░░██║░░░░░██║░░██║██████╔╝██║██║░░╚═╝
    ██╔═██╗░██╔══██║██║░░░░░██║░░░░░██║░░██║██╔═══╝░██║██║░░██╗
    ██║░╚██╗██║░░██║███████╗███████╗╚█████╔╝██║░░░░░██║╚█████╔╝
    ╚═╝░░╚═╝╚═╝░░╚═╝╚══════╝╚══════╝░╚════╝░╚═╝░░░░░╚═╝░╚════╝░
    """  # thanks to https://text-symbols.com/

    # 运行配置
    LOGO_ICON_RELPATH = "resources/logo/logo.ico"
    LOGO_ICON_PATH = get_resource_path(LOGO_ICON_RELPATH)
    DEFAULT_WIN_SIZE = "500x400"
    IMG_SUFFIX = (
        '.jpeg', '.JPEG',
        '.jpg', '.JPG',
        '.png', '.PNG',
        '.bmp', '.BMP',
        '.webp', '.WEBP',
        '.gif', '.GIF',
    )


class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = logging.DEBUG
    LOG_RELPATH = rf"../log/{Config.PROJECT_NAME_LOWER}.log"


class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = logging.WARNING
    # LOG_RELPATH = rf"{Config.PROJECT_NAME_LOWER}.log"
    LOG_RELPATH = None


def get_config():
    env = os.getenv('APP_ENV', 'production')
    if env == 'production':
        return ProductionConfig
    return DevelopmentConfig


Conf = get_config()
