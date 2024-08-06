#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk

from src.config import Conf


# noinspection PyTypeChecker
class AskStringDialog(tk.Toplevel):
    def __init__(self, parent, title=None, prompt=None, initialvalue=None):
        super().__init__(parent)
        self.transient(parent)  # 设置窗口为父窗口的子窗口

        if title:
            self.title(title)

        self.parent = parent
        self.prompt = prompt
        self.initialvalue = initialvalue
        self.result = None

        self.body = ttk.Frame(self)
        self.body.pack(padx=5, pady=5)

        self.initialize_ui()

        self.grab_set()  # 获取焦点
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 50,
                                  parent.winfo_rooty() + 50))

        self.iconbitmap(Conf.LOGO_ICON_PATH)  # 设置图标
        self.wait_window(self)  # 等待窗口关闭

    # noinspection PyAttributeOutsideInit
    def initialize_ui(self):
        self.label = ttk.Label(self.body, text=self.prompt)
        self.label.grid(row=0, column=0, sticky=tk.W, padx=5)

        self.entry = ttk.Entry(self.body)
        if self.initialvalue:
            self.entry.insert(0, self.initialvalue)
        self.entry.grid(row=0, column=1, sticky=tk.EW, padx=5)
        self.entry.focus_set()

        box = ttk.Frame(self)
        box.pack(pady=5)

        w = ttk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

    def ok(self):
        self.result = self.entry.get()
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()


def custom_ask_string(parent, title=None, prompt=None, initialvalue=None):
    if not isinstance(parent, (tk.Tk, tk.Toplevel)):
        raise ValueError("Parent must be a Tk or Toplevel instance.")

    dialog = AskStringDialog(parent, title, prompt, initialvalue)
    return dialog.result
