#!usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, simpledialog

from src.config import Conf

class DictEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("Dictionary Configuration")

        self.button_frame = ttk.Frame(master)
        self.button_frame.pack(anchor=tk.CENTER)
        self.add_button = ttk.Button(self.button_frame, text="Add", command=self.add_item)
        self.add_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.delete_button = ttk.Button(self.button_frame, text="Delete", command=self.delete_selected)
        self.delete_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.move_up_button = ttk.Button(self.button_frame, text="Up", command=self.move_up)
        self.move_up_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.move_down_button = ttk.Button(self.button_frame, text="Down", command=self.move_down)
        self.move_down_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.edit_button = ttk.Button(self.button_frame, text="Edit", command=self.edit_item)
        self.edit_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.clear_button = ttk.Button(self.button_frame, text="Clear", command=self.clear_list)
        self.read_default_button = ttk.Button(self.button_frame, text="Read Default", command=self.read_default_dict)
        self.read_default_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.export_button = ttk.Button(self.button_frame, text="Export", command=self.export_dict)
        self.export_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.import_button = ttk.Button(self.button_frame, text="Import", command=self.import_dict)
        self.import_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.save_button = ttk.Button(self.button_frame, text="Save", command=self.save_dict)
        self.save_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.cancel_button = ttk.Button(self.button_frame, text="Cancel", command=self.cancel)
        self.cancel_button.pack(side=tk.LEFT, padx=5, pady=5)

        # 配置列表
        self.tree_frame = ttk.Frame(master)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
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
        self.tree.column("Role", width=150, minwidth=100, stretch=tk.NO, anchor=tk.W)
        self.tree.column("Keyword", stretch=tk.YES, anchor=tk.W)
        self.tree.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        # 绑定Scrollbar到Treeview
        self.tree_scrollbar.config(command=self.tree.yview)
        # 部分快捷键
        self.tree.bind("<Delete>", lambda e: self.delete_selected())
        self.tree.bind("<Double-1>", lambda e: self.edit_item())

        # 下方状态栏
        self.status_bar = ttk.Label(master, text="Default dictionary ready.")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.read_default_dict()

    def clear_list(self):
        self.tree.delete(*self.tree.get_children())
        self.status_bar.config(text="Cleared.")

    def read_default_dict(self):
        self.clear_list()
        for role, keyword in Conf.DIR_KEYWORD_MAP.items():
            self.tree.insert("", tk.END, values=(role, keyword))

    def add_item(self):
        role = simpledialog.askstring("Input name", "Name:")
        if not role:
            return
        keyword = simpledialog.askstring("Input keyword", "Keyword:")
        if not keyword:
            return
        self.tree.insert("", tk.END, values=(role, keyword))

    def delete_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            self.status_bar.config(text="Please choose the row(s) to delete.")
            return
        for item in selected_items:
            self.tree.delete(item)
        self.status_bar.config(text="")

    def move_up(self):
        selected_items = self.tree.selection()
        if not selected_items:
            self.status_bar.config(text="Please choose the row(s) to move.")
            return
        for item in selected_items:
            prev_item = self.tree.prev(item)
            if prev_item:
                self.tree.move(item, self.tree.parent(prev_item), self.tree.index(prev_item))
        self.status_bar.config(text="")

    def move_down(self):
        selected_items = self.tree.selection()
        if not selected_items:
            self.status_bar.config(text="Please choose the row(s) to move.")
            return
        for item in reversed(selected_items):
            next_item = self.tree.next(item)
            if next_item:
                self.tree.move(item, self.tree.parent(next_item), self.tree.index(next_item))
        self.status_bar.config(text="")

    def edit_item(self):
        selected_items = self.tree.selection()
        if len(selected_items) != 1:
            self.status_bar.config(text="Please choose one row to edit.")
            return
        item = selected_items[0]
        current_values = self.tree.item(item, "values")
        new_role = simpledialog.askstring("Edit name", "Name:", initialvalue=current_values[0])
        if not new_role:
            return
        new_keyword = simpledialog.askstring("Edit keyword", "Keyword:", initialvalue=current_values[1])
        if not new_keyword:
            return
        self.tree.item(item, values=(new_role, new_keyword))
        self.status_bar.config(text="")

    def export_dict(self):
        """导出ini文件到当前目录"""
        new_dict = {}
        for item in self.tree.get_children():
            role, keyword = self.tree.item(item, "values")
            new_dict[role] = keyword
        with open("DirnameShortcutDict.ini", "w", encoding="utf-8") as f:
            f.write(str(new_dict))
        pass

    def import_dict(self):
        pass

    def save_dict(self):
        """保存到全局变量"""
        pass

    def cancel(self):
        """取消对字典的配置并退出"""
        pass
