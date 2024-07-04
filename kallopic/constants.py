#!usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


# noinspection PyBroadException,PyProtectedMember
def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("..")
    return os.path.join(base_path, relative_path)


class Constants:
    PROJECT_NAME = "KalloPic"
    PROJECT_NAME_LOWER = PROJECT_NAME.lower()
    VERSION = "0.1.0"
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
    RSC_RELPATH = r"resources/"  # 相对于项目文件夹
    LOGO_ICON_RELPATH = RSC_RELPATH + r"logo/logo.ico"
    LOGO_ICON_PATH = get_resource_path(LOGO_ICON_RELPATH)
    DEFAULT_WIN_SIZE = "500x400"
