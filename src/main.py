#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tkinter as tk

from src.archiver import Archiver as MainWindow
from src.config import Conf
from src.utils.gradient_print import print_gradient_text
from src.utils.logger import Logger


if __name__ == '__main__':
    print_gradient_text(Conf.BANNER)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    Logger.debug(f"Current working directory: {os.getcwd()}")

    root = tk.Tk()
    app = MainWindow(root)
    root.wm_iconbitmap(Conf.LOGO_ICON_PATH)
    root.title(Conf.PROJECT_NAME)
    root.minsize(400, 400)
    root.maxsize(1960, 1080)

    # 居中显示
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    Logger.debug(f"Screen_width: {screen_width}, Screen_height: {screen_height}")
    Logger.debug(f"Window_width: {Conf.DEFAULT_WIN_WIDTH}, Window_height: {Conf.DEFAULT_WIN_HEIGHT}")
    dx = (screen_width - Conf.DEFAULT_WIN_WIDTH) // 2
    dy = (screen_height - Conf.DEFAULT_WIN_HEIGHT) // 2
    Logger.debug(f"Window position: {dx}+{dy}")
    root.geometry(f"{Conf.DEFAULT_WIN_SIZE}+{dx}+{dy}")

    root.mainloop()
