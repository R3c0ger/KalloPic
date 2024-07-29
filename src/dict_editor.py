#!usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, simpledialog

from src.config import Conf


class DictEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("Dictionary Configuration")
        self.master.geometry("1000x500")
        self.master.minsize(1000, 500)
        self.master.maxsize(1920, 1080)

        # 逻辑控制
        self.saved = True

        # 主要组件
        self.main_frame = ttk.Frame(master)
        self.main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 左侧字典列表
        self.tree_frame = ttk.Frame(self.main_frame)
        self.tree_frame.pack(side=tk.LEFT, anchor=tk.N, fill=tk.BOTH, expand=True)
        # 添加右侧滚动条
        self.tree_scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL)
        self.tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # 添加Treeview
        self.tree = ttk.Treeview(
            self.tree_frame, columns=("Role", "Keyword"), show="headings",
            yscrollcommand=self.tree_scrollbar.set
        )
        self.tree.heading("Role", text="Role name")
        self.tree.heading("Keyword", text="Key words")
        self.tree.column("Role", width=150, minwidth=100, stretch=False, anchor=tk.W)
        self.tree.column("Keyword", stretch=True, anchor=tk.W)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # 绑定Scrollbar到Treeview
        self.tree_scrollbar.config(command=self.tree.yview)

        # 右侧功能按钮栏
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(side=tk.RIGHT, anchor=tk.N)
        self.add_button = ttk.Button(self.button_frame, text="Add(Ctrl+A)", command=self.add_item)
        self.add_button.pack(side=tk.TOP, padx=5, pady=5)
        self.delete_button = ttk.Button(self.button_frame, text="Delete(Del)", command=self.delete_selected)
        self.delete_button.pack(side=tk.TOP, padx=5, pady=5)
        self.move_up_button = ttk.Button(
            self.button_frame, text="Move up", command=lambda x="up": self.move_item(x))
        self.move_up_button.pack(side=tk.TOP, padx=5, pady=5)
        self.move_down_button = ttk.Button(
            self.button_frame, text="Move down", command=lambda x="down": self.move_item(x))
        self.move_down_button.pack(side=tk.TOP, padx=5, pady=5)
        self.edit_button = ttk.Button(self.button_frame, text="Edit(Ctrl+E)", command=self.edit_item)
        self.edit_button.pack(side=tk.TOP, padx=5, pady=5)
        self.clear_button = ttk.Button(self.button_frame, text="Clear", command=self.clear_list)
        self.clear_button.pack(side=tk.TOP, padx=5, pady=5)
        self.read_saved_button = ttk.Button(
            self.button_frame, text="Read saved\n    (Ctrl+R)", command=self.read_saved_dict)
        self.read_saved_button.pack(side=tk.TOP, padx=5, pady=5)
        self.read_default_button = ttk.Button(
            self.button_frame, text="Read Default\n    (Ctrl+D)", command=self.read_default_dict)
        self.read_default_button.pack(side=tk.TOP, padx=5, pady=5)
        self.export_button = ttk.Button(self.button_frame, text="Export", command=self.export_dict)
        self.export_button.pack(side=tk.TOP, padx=5, pady=5)
        self.import_button = ttk.Button(self.button_frame, text="Import", command=self.import_dict)
        self.import_button.pack(side=tk.TOP, padx=5, pady=5)
        self.save_button = ttk.Button(self.button_frame, text="Save(Ctrl+S)", command=self.save_dict)
        self.save_button.pack(side=tk.TOP, padx=5, pady=5)

        # 下方状态栏
        self.status_bar = ttk.Label(master, text="Default dictionary ready.")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        # 快捷键
        self.master.bind("<Delete>", lambda e: self.delete_selected())
        self.master.bind("<Double-1>", lambda e: self.edit_item())
        self.master.bind("<Control-a>", lambda e: self.add_item())
        self.master.bind("<Control-s>", lambda e: self.save_dict())
        self.master.bind("<Control-e>", lambda e: self.edit_item())
        self.master.bind("<Control-r>", lambda e: self.read_saved_dict())
        self.master.bind("<Control-d>", lambda e: self.read_default_dict())

        # 读取所存储的字典
        self.read_saved_dict()
        self.saved = True

    def clear_list(self):
        self.tree.delete(*self.tree.get_children())
        self.status_bar.config(text="Cleared.")

        self.saved = False
        self.clear_list()
        for role, keyword in _dict.items():
            self.tree.insert("", tk.END, values=(role, keyword))

    def read_default_dict(self):
        self.read_dict(Conf.DEFAULT_DIR_KEYWORD_MAP)
        self.status_bar.config(text="Default dictionary ready.")

    def read_saved_dict(self):
        self.read_dict(Conf.DIR_KEYWORD_MAP)
        self.status_bar.config(text="Dictionary ready.")

    def add_item(self):
        self.saved = False
        role = simpledialog.askstring("Input name", "Name:")
        if not role:
            self.saved = True
            return
        keyword = simpledialog.askstring("Input keyword", "Keyword:")
        if not keyword:
            self.saved = True
            return
        self.tree.insert("", tk.END, values=(role, keyword))

    def delete_selected(self):
        self.saved = False
        selected_items = self.tree.selection()
        if not selected_items:
            self.status_bar.config(text="Please select the row(s) to delete.")
            return
        for item in selected_items:
            self.tree.delete(item)
        self.status_bar.config(text="The selected row(s) have been deleted.")

    def move_item(self, direction):
        self.saved = False
        selected_items = self.tree.selection()
        if not selected_items:
            self.status_bar.config(text="Please select the row(s) to move.")
            return

        if direction == "up":
            for item in selected_items:
                prev_item = self.tree.prev(item)
                if prev_item and prev_item not in selected_items:
                    self.tree.move(item, self.tree.parent(prev_item), self.tree.index(prev_item))
        elif direction == "down":
            for item in reversed(selected_items):
                next_item = self.tree.next(item)
                if next_item and next_item not in selected_items:
                    self.tree.move(item, self.tree.parent(next_item), self.tree.index(next_item))

        self.status_bar.config(text=f"Moved {len(selected_items)} row(s) {direction}.")

    def edit_item(self):
        self.saved = False
        selected_items = self.tree.selection()
        if len(selected_items) != 1:
            self.status_bar.config(text="Please choose one row to edit.")
            return
        item = selected_items[0]
        current_values = self.tree.item(item, "values")
        new_role = simpledialog.askstring("Edit name", "Name:", initialvalue=current_values[0])
        if not new_role:
            self.saved = True
            return
        new_keyword = simpledialog.askstring("Edit keyword", "Keyword:", initialvalue=current_values[1])
        if not new_keyword:
            if new_role == current_values[0]:
                self.saved = True
            return
        else:
            if new_role == current_values[0] and new_keyword == current_values[1]:
                self.saved = True
                return
        self.tree.item(item, values=(new_role, new_keyword))
        self.status_bar.config(text="The selected row has been edited.")

    def tree_to_ordered_dict(self):
        new_dict = {}
        for item in self.tree.get_children():
            role, keyword = self.tree.item(item, "values")
            new_dict[role] = keyword
        return OrderedDict(new_dict)

    def save_dict(self):
        """保存到全局变量"""
        self.saved = True
        Conf.DIR_KEYWORD_MAP = self.tree_to_ordered_dict()
        self.status_bar.config(text="Dictionary saved.")
        pprint(Conf.DIR_KEYWORD_MAP)
