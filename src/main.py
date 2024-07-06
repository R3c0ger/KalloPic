#!usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tkinter as tk

from src.constants import Constants
from src.archiver import Archiver as MainWindow
from src.utils.gradient_print import print_gradient_text


if __name__ == '__main__':
    print_gradient_text(Constants.BANNER)
    root = tk.Tk()
    root.title(Constants.PROJECT_NAME)
    app = MainWindow(root)
    root.geometry(Constants.DEFAULT_WIN_SIZE)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    root.wm_iconbitmap(Constants.LOGO_ICON_PATH)
    root.minsize(400, 400)
    root.maxsize(1960, 1080)
    root.mainloop()
