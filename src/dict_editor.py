#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configparser
import tkinter as tk
from collections import OrderedDict
from tkinter import ttk, messagebox, filedialog

from src.config import Conf
from src.utils.dialog import custom_ask_string
from src.utils.logger import Logger


def check_dirname(dirname):
    """检查文件夹名。文件夹不能命名为Windows或DOS保留的名称，或包含特殊字符"""
    reserved_dirnames = [
        "CON", "PRN", "AUX", "NUL",
        "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
    ]
    special_chars = r'\/:*?"<>|'
    if dirname in reserved_dirnames:
        return False
    if any(c in special_chars for c in dirname):
        return False
    return True


def check_keywords_str(keywords_str):
    """检查关键字字符串，只允许其中有小写字母和空格"""
    return all(c.islower() or c.isspace() for c in keywords_str)


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
            self.tree_frame, columns=("Order", "Dirname", "Keyword"), show="headings",
            yscrollcommand=self.tree_scrollbar.set
        )
        self.tree.heading("Order", text="Order")
        self.tree.heading("Dirname", text="Directory name")
        self.tree.heading("Keyword", text="Key words")
        self.tree.column("Order", width=50, minwidth=50, stretch=False, anchor="center")
        self.tree.column("Dirname", width=150, minwidth=100, stretch=False, anchor=tk.W)
        self.tree.column("Keyword", stretch=True, anchor=tk.W)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # 绑定Scrollbar到Treeview
        self.tree_scrollbar.config(command=self.tree.yview)

        # 右侧功能按钮栏
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(side=tk.RIGHT, anchor=tk.N, padx=5)
        self.add_button = ttk.Button(self.button_frame, text="Add (Ctrl+A)", command=self.add_item)
        self.add_button.pack(side=tk.TOP, padx=5, pady=2)
        self.delete_button = ttk.Button(self.button_frame, text="Delete (Del)", command=self.delete_selected)
        self.delete_button.pack(side=tk.TOP, padx=5, pady=2)
        self.move_up_button = ttk.Button(
            self.button_frame, text="Move up (Alt+W)", command=lambda x="up": self.move_item(x))
        self.move_up_button.pack(side=tk.TOP, padx=5, pady=2)
        self.move_down_button = ttk.Button(
            self.button_frame, text="Move down (Alt+S)", command=lambda x="down": self.move_item(x))
        self.move_down_button.pack(side=tk.TOP, padx=5, pady=2)
        self.edit_button = ttk.Button(self.button_frame, text="Edit (Ctrl+E)", command=self.edit_item)
        self.edit_button.pack(side=tk.TOP, padx=5, pady=2)
        self.clear_button = ttk.Button(self.button_frame, text="Clear (Alt+C)", command=self.clear_list)
        self.clear_button.pack(side=tk.TOP, padx=5, pady=2)
        self.read_saved_button = ttk.Button(
            self.button_frame, text="Read saved (Ctrl+R)", command=self.read_saved_dict)
        self.read_saved_button.pack(side=tk.TOP, padx=5, pady=2)
        self.read_default_button = ttk.Button(
            self.button_frame, text="Read Default (Ctrl+D)", command=self.read_default_dict)
        self.read_default_button.pack(side=tk.TOP, padx=5, pady=2)
        self.save_button = ttk.Button(self.button_frame, text="Save (Ctrl+S)", command=self.save_dict)
        self.save_button.pack(side=tk.TOP, padx=5, pady=2)
        self.export_button = ttk.Button(
            self.button_frame, text="Export (Alt+E)", command=lambda: self.export_dict())
        self.export_button.pack(side=tk.TOP, padx=5, pady=2)
        self.import_button = ttk.Button(
            self.button_frame, text="Import (Alt+I)", command=lambda: self.import_dict())
        self.import_button.pack(side=tk.TOP, padx=5, pady=2)
        # 设置所有的功能按钮的宽度一致，文字左对齐
        child: ttk.Button
        for child in self.button_frame.winfo_children():
            child.config(width=18, style='LeftAligned.TButton')

        # 下方状态栏
        self.status_bar = ttk.Label(master, text="Default dictionary ready.")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        # 快捷键
        self.tree.bind("<Double-1>", lambda e: self.edit_item())
        self.master.bind("<Delete>", lambda e: self.delete_selected())
        self.master.bind("<Control-a>", lambda e: self.add_item())
        self.master.bind("<Control-s>", lambda e: self.save_dict())
        self.master.bind("<Control-e>", lambda e: self.edit_item())
        self.master.bind("<Control-r>", lambda e: self.read_saved_dict())
        self.master.bind("<Control-d>", lambda e: self.read_default_dict())
        self.master.bind("<Alt-w>", lambda e: self.move_item("up"))
        self.master.bind("<Alt-s>", lambda e: self.move_item("down"))
        self.master.bind("<Alt-c>", lambda e: self.clear_list())
        self.master.bind("<Alt-e>", lambda e: self.export_dict())
        self.master.bind("<Alt-i>", lambda e: self.import_dict())

        # 读取所存储的字典
        self.read_saved_dict()
        self.saved = True

    def clear_list(self):
        self.tree.delete(*self.tree.get_children())
        self.status_bar.config(text="Cleared.")

    def _dict_to_tree(self, _dict):
        self.saved = False
        self.clear_list()
        for order, (dirname, keyword) in enumerate(_dict.items()):
            self.tree.insert("", tk.END, values=(order, dirname, keyword))

    def read_default_dict(self):
        self._dict_to_tree(Conf.DEFAULT_DIR_KEYWORD_MAP)
        self.status_bar.config(text="Default dictionary ready.")

    def read_saved_dict(self):
        self._dict_to_tree(Conf.DIR_KEYWORD_MAP)
        self.status_bar.config(text="Dictionary ready.")

    def add_item(self):
        dirname = custom_ask_string(self.master, "Input name", "Name:")
        if not dirname:
            self.status_bar.config(text="No directory name input. Cancelled.")
            return
        if not check_dirname(dirname):
            self.status_bar.config(text=f"Invalid directory name: '{dirname}'.")
            return

        keywords_str = custom_ask_string(self.master, "Input keywords", "Keywords:")
        if not keywords_str:
            self.status_bar.config(text="No keywords input. Cancelled.")
            return
        if not check_keywords_str(keywords_str):
            self.status_bar.config(
                text=f"Invalid keywords: '{keywords_str}'."
                     " Keywords must be consisted of lower"
                     "case letters and separated by space."
            )
            return

        order = len(self.tree.get_children())
        self.tree.insert("", tk.END, values=(order, dirname, keywords_str))
        self.status_bar.config(text="Added successfully.")
        self.saved = False

    def _refresh_order(self):
        """重新排列Order列的值"""
        for i, item in enumerate(self.tree.get_children()):
            self.tree.item(item, values=(i, *self.tree.item(item, "values")[1:]))

    def delete_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            self.status_bar.config(text="Please select the row(s) to delete.")
            return
        for item in selected_items:
            self.tree.delete(item)
        self.status_bar.config(text="The selected row(s) have been deleted.")
        self._refresh_order()
        self.saved = False

    def move_item(self, direction):
        directions = ["up", "down"]
        if direction not in directions:
            raise ValueError(f"Invalid direction: {direction}")
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
        self._refresh_order()
        self.saved = False

    def edit_item(self):
        selected_items = self.tree.selection()
        if len(selected_items) != 1:
            self.status_bar.config(text="Please choose one row to edit.")
            return
        item = selected_items[0]
        current_values = self.tree.item(item, "values")

        new_dirname = custom_ask_string(
            self.master, "Edit name", "Name:", initialvalue=current_values[1])
        if not new_dirname:
            self.status_bar.config(text="No directory name input. Cancelled.")
            return
        if not check_dirname(new_dirname):
            self.status_bar.config(text=f"Invalid directory name: '{new_dirname}'.")
            return

        new_keywords_str = custom_ask_string(
            self.master, "Edit keyword", "Keywords:", initialvalue=current_values[2])
        if not new_keywords_str:
            self.status_bar.config(text="No keywords input. Cancelled.")
            return
        if not check_keywords_str(new_keywords_str):
            self.status_bar.config(
                text=f"Invalid keywords: '{new_keywords_str}'."
                     " Keywords must be consisted of lower"
                     "case letters and separated by space."
            )
            return

        # 若均未修改，则不更新
        if new_dirname == current_values[0] and new_keywords_str == current_values[1]:
            self.status_bar.config(text="No changes made.")
            return

        self.tree.item(item, values=(current_values[0], new_dirname, new_keywords_str))
        self.status_bar.config(text="The selected row has been edited.")
        self.saved = False

    def _tree_to_ordered_dict(self):
        new_dict = {}
        for item in self.tree.get_children():
            _, dirname, keywords_str = self.tree.item(item, "values")
            if not check_dirname(dirname):
                self.status_bar.config(text=f"Invalid directory name: '{dirname}'.")
                return False
            if not check_keywords_str(keywords_str):
                self.status_bar.config(
                    text=f"Invalid keywords: '{keywords_str}'."
                         " Keywords must be consisted of lower"
                         "case letters and separated by space."
                )
                return False
            new_dict[dirname] = keywords_str.split()
        return OrderedDict(new_dict)

    def save_dict(self):
        """保存到全局变量"""
        self.saved = True
        dir_keyword_map = self._tree_to_ordered_dict()
        if not dir_keyword_map:
            pre_msg = self.status_bar.cget("text")
            self.status_bar.config(text=f"Save failed. {pre_msg}")
            return
        Conf.DIR_KEYWORD_MAP = dir_keyword_map
        self.status_bar.config(text="Dictionary saved successfully.")

    def export_dict(self, filename="DirnameShortcut"):
        """导出ini文件到当前目录"""
        # 根据是否保存，以及用户的选择来决定导出的字典
        dictionary = Conf.DIR_KEYWORD_MAP
        if not self.saved and messagebox.askokcancel(
            "Save dictionary",
            "Do you want to export the unsaved dictionary?\n"
            "If no, the last saved dictionary will be exported."
        ):
            dictionary = self._tree_to_ordered_dict()
        if not dictionary:
            pre_msg = self.status_bar.cget("text")
            self.status_bar.config(text=f"Export canceled. {pre_msg}")
            return

        config = configparser.ConfigParser()
        for key, value in dictionary.items():
            config[key] = {}
            if isinstance(value, list):
                value = " ".join(value)
            config[key]['variants'] = value

        # 打开窗口让用户选择保存位置和文件名，默认位置为当前目录
        save_path = filedialog.asksaveasfilename(
            initialdir=".", initialfile=filename, defaultextension=".ini",
            filetypes=[("INI files", "*.ini"), ("All files", "*.*")]
        )
        self.master.focus_force()
        Logger.debug(save_path)
        if not save_path:
            self.status_bar.config(text="Export canceled.")
            return

        # 写入ini文件
        try:
            with open(save_path, 'w', encoding='utf-8') as configfile:
                config.write(configfile)
        except Exception as e:
            self.status_bar.config(text=f"Export failed: {e}")
            return
        self.status_bar.config(text="Exported successfully.")

    def import_dict(self, filename="DirnameShortcut"):
        """从ini文件导入"""
        # 打开窗口让用户选择文件，默认位置为当前目录
        ini_path = filedialog.askopenfilename(
            initialdir=".", initialfile=filename, defaultextension=".ini",
            filetypes=[("INI files", "*.ini"), ("All files", "*.*")]
        )
        self.master.focus_force()
        Logger.debug(ini_path)
        if not ini_path:
            self.status_bar.config(text="Import canceled.")
            return

        # 读取ini文件
        config = configparser.ConfigParser()
        try:
            with open(ini_path, 'r', encoding='utf-8') as configfile:
                config.read_file(configfile)
        except Exception as e:
            self.status_bar.config(text=f"Import failed: {e}")
            return

        # 清空当前列表，写入新的数据
        self.tree.delete(*self.tree.get_children())
        for order, key in enumerate(config.sections()):
            dirname, keywords_str = key, config[key]['variants']
            if not check_dirname(dirname):
                self.status_bar.config(text=f"Import Failed. Invalid directory name: '{dirname}'.")
                return
            if not check_keywords_str(keywords_str):
                self.status_bar.config(text=f"Import Failed. Invalid keywords: '{keywords_str}'.")
                return
            self.tree.insert("", tk.END, values=(order, dirname, keywords_str))
        self.status_bar.config(text="Imported successfully.")
        self.saved = False
