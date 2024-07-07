#!usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tkinter as tk

from src.archiver import Archiver as MainWindow
from src.config import Conf
from src.utils.gradient_print import print_gradient_text
from src.utils.logger import setup_logger


if __name__ == '__main__':
    logger = setup_logger(
        level=Conf.LOG_LEVEL,
        log_file=Conf.LOG_RELPATH
    )
    print_gradient_text(Conf.BANNER)
    root = tk.Tk()
    root.title(Conf.PROJECT_NAME)
    app = MainWindow(root)
    root.geometry(Conf.DEFAULT_WIN_SIZE)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    logger.debug(f"Current working directory: {os.getcwd()}")
    root.wm_iconbitmap(Conf.LOGO_ICON_PATH)
    root.minsize(400, 400)
    root.maxsize(1960, 1080)
    root.mainloop()
