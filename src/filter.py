#!usr/bin/env python
# -*- coding: utf-8 -*-
import os
import tkinter as tk
from tkinter import ttk


class FolderConfig:
    def __init__(self, dir_abspath):
        self.dir_abspath = dir_abspath
        self.delete_mode_list = ["trash", "extract"]  # 移动到回收站、移动到文件夹下的特殊文件夹
        self.delete_mode = self.delete_mode_list[1]


class Filter:
    def __init__(self, master, dir_abspath):
        self.master = master
        self.master.title("Filter")
        self.dir_abspath = dir_abspath
        print(self.dir_abspath)
        self.dir_conf = FolderConfig(self.dir_abspath)

        self.stat_group = ttk.LabelFrame(master, text="Statistics")
        self.stat_group.pack(anchor=tk.W, padx=5, pady=5)
        self.stat_label = ttk.Label(
            self.stat_group,
            text="Statistics of files in current folder:"
        )
        self.stat_label.pack(side=tk.LEFT, padx=5, pady=5)
