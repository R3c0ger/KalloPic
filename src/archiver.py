#!usr/bin/env python
# -*- coding: utf-8 -*-

import heapq
import os
import shutil
import string
import tkinter as tk
from difflib import SequenceMatcher
from functools import partial
from tkinter import ttk, messagebox

from pypinyin import pinyin, Style

from src.config import Conf
from src.dict_editor import DictEditor
from src.filter import Filter
from src.utils.logger import Logger
from src.viewer import ImageViewer


def get_closest_match(input_str):
    """根据用户输入的字符串寻找字典中最接近的字符串"""
    def similarity(a, b):
        return SequenceMatcher(None, a, b).ratio()

    # 创建一个优先队列来保存最接近的前n个字符串
    closest_matches = []
    for name, shortcuts in Conf.DIR_KEYWORD_MAP.items():
        # 先按相似度排序，再按优先级排序，取有序字典顺序作为优先级
        priority = Conf.DIR_KEYWORD_MAP_LIST.index(name)
        for shortcut in shortcuts:
            sim = similarity(input_str, shortcut)
            if sim == 0:
                continue
            if len(closest_matches) < 7:
                heapq.heappush(closest_matches, (sim, priority, name))
            else:
                heapq.heappushpop(closest_matches, (sim, priority, name))

    closest_matches = sorted(closest_matches, key=lambda x: (x[0], -x[1]), reverse=True)

    name_rank = []
    for _, _, name in closest_matches:
        if name not in name_rank:
            name_rank.append(name)
    return name_rank[:5]


class Archiver(ImageViewer):
    def __init__(self, master):
        super().__init__(master)
        # 获取角色列表
        self.chara_list = list([name for name, _ in Conf.DIR_KEYWORD_MAP.items()])
        # 按汉字拼音首字母排序
        self.sort_by_pinyin_first_letter()
        # 快捷移动输入框中可更新列表的按键
        self.refresh_opr = [char for char in string.ascii_letters]
        self.refresh_opr.append("BackSpace")
        # 快捷移动输入框中允许执行的按键，不会更新列表
        self.able_opr = [
            "Left", "Right", "Up", "Down",
            "Shift_L", "Shift_R", "Control_L", "Control_R",
            "Alt_L", "Alt_R", "Home", "End", "space"
        ]

        # 打开过滤器
        self.filter_button = ttk.Button(
            self.button_frame,
            text="Filter",
            command=self.open_filter_window,
            width=10
        )
        self.filter_button.grid(row=0, column=13, padx=10)

        # 打开目标文件夹，选择要将图片移动的目的地址
        self.tgt_frame = ttk.Frame(master)
        self.tgt_frame.pack(fill=tk.X)
        # 目标文件夹标签
        self.tgt_label = ttk.Label(self.tgt_frame, text="Target Folder:", width=12)
        self.tgt_label.pack(side=tk.LEFT, padx=10)
        # 输入框
        self.tgt_entry = ttk.Entry(self.tgt_frame)
        self.tgt_entry.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self.tgt_entry.insert(0, "example: D:/Pictures")
        # 选择文件夹按钮
        self.tgt_browse_dir = partial(self.input_dir, self.tgt_entry)
        self.tgt_browse_button = ttk.Button(self.tgt_frame, text="Browse", command=self.tgt_browse_dir)
        self.tgt_browse_button.pack(side=tk.LEFT)
        # 下拉列表
        self.tgt_option_menu = ttk.Combobox(
            self.tgt_frame, values=self.chara_list,
            width=14, state="readonly"
        )
        self.tgt_option_menu.set("Pick a character")
        self.tgt_option_menu.pack(side=tk.LEFT)
        # 确认移动按钮
        self.tgt_move_button = ttk.Button(self.tgt_frame, text="Move", command=self.move_img)
        self.tgt_move_button.pack(side=tk.LEFT)
        # 打开配置字典窗口
        self.config_button = ttk.Button(
            self.tgt_frame, text="Config", command=self.open_config_window
        )
        self.config_button.pack(fill=tk.X)

        # 快捷移动输入框和备选列表
        self.input_box = None
        self.option_list = None

        # 设置快捷键
        self.master.bind("<Control-t>", lambda event: self.tgt_browse_dir())
        self.master.bind("<Control-p>", lambda event: self.tgt_option_menu.focus())
        self.master.bind("<Control-a>", lambda event: self.tgt_move_button.invoke())
        self.master.bind("<Escape>", self.input_shortcut)
        self.master.bind("<F9>", self.open_filter_window)
        self.master.bind("<F10>", self.open_config_window)

        # 为help_items添加新的帮助提示
        self.help_items += [
            ("——"*50, "——"*50, None),  # 分割线
            ("", "Enter the target folder path at the right.", self.tgt_label),
            ("", "Type the target folder path. (Ctrl+T to browse)", self.tgt_entry),
            ("Ctrl+T", "Browse to select the target folder.", self.tgt_browse_button),
            ("Ctrl+P", "Focus on the target character combobox.", self.tgt_option_menu),
            ("Ctrl+A", "Move the current image to the target folder.", self.tgt_move_button),
            ("Esc", "Show/Hide the quick move input box and option list.", None),
            ("1,2,3,4,5", "Choose the corresponding option in the option list.", None),
            ("F9", "Open the filter window.", self.filter_button),
            ("F10", "Open the folder-name dictionary config window.", self.config_button),
        ]

        # 预执行
        self.pre_execute()

    def sort_by_pinyin_first_letter(self):
        """根据汉语拼音的拉丁字母排序角色列表"""
        pinyin_list = [pinyin(name, style=Style.FIRST_LETTER) for name in self.chara_list]
        pinyin_list = ["".join([c[0] for c in letter_list]) for letter_list in pinyin_list]
        # Logger.debug(pinyin_list)
        sorted_words = sorted(zip(pinyin_list, self.chara_list), key=lambda x: x[0])
        self.chara_list = [word for _, word in sorted_words]

    def input_shortcut(self, _=None):
        # 如果没打开快捷移动输入框，则打开
        if self.input_box is None:
            self.input_box = ttk.Entry(self.canvas)
            self.input_box.pack(anchor=tk.NE)
            self.input_box.focus()
            # 输入框绑定事件，只要内容有更新，就更新备选列表
            self.input_box.bind("<KeyRelease>", self.update_option_list)
            # 解除绑定左右键
            self.master.bind("<Left>", lambda e: None)
            self.master.bind("<Right>", lambda e: None)
        # 如果已打开快捷移动输入框，则销毁
        else:
            # 销毁输入框和备选列表
            self.input_box.destroy()
            self.input_box = None
            if self.option_list is not None:
                self.option_list.destroy()
                self.option_list = None
            # 重新绑定左右键动作
            self.master.bind("<Left>", lambda e: self.show_prev_img())
            self.master.bind("<Right>", lambda e: self.show_next_img())

    def update_option_list(self, event):
        input_str = self.input_box.get()
        trimmed_str = "".join([c for c in input_str if c in string.ascii_letters])
        # Logger.debug(event.keysym)
        # 只有按下字母和删除键，才更新备选列表。按下允许执行的按键则不会清理输入框内容
        if event.keysym not in self.refresh_opr:
            if event.keysym not in self.able_opr:
                self.input_box.delete(0, tk.END)
                self.input_box.insert(0, trimmed_str)
            return
        trimmed_str = trimmed_str.lower()
        # Logger.debug(trimmed_str)

        # 如果备选列表存在，则销毁
        if self.option_list is not None:
            self.option_list.destroy()
            self.option_list = None
        # 更新显示备选列表。如果输入的有效内容为空，则不显示备选列表
        if trimmed_str:
            name_rank = get_closest_match(trimmed_str)
            self.option_list = tk.Listbox(self.canvas)
            # 根据条目数设置高度
            self.option_list.config(height=len(name_rank))
            self.option_list.pack(anchor=tk.NE)
            for no, name in enumerate(name_rank):
                self.option_list.insert(tk.END, f"{no+1} {name}")
            # 绑定事件，选择列表项则移动文件
            self.option_list.bind("<<ListboxSelect>>", lambda e: self.on_option_select(e))
            # 绑定数字1-5按键，按下则选择对应的备选列表项
            for i in range(1, 6):
                self.master.bind(str(i), lambda e, idx=i: self.on_num_select(e, idx))

    def on_option_select(self, _):
        selected_idx = self.option_list.curselection()
        if selected_idx:
            selected_name = self.option_list.get(selected_idx)[2:]
            self.move_img(selected_name)
            # 清空输入框，销毁备选列表
            self.option_list.destroy()
            self.option_list = None
            self.input_box.delete(0, tk.END)
            self.input_box.focus()

    def on_num_select(self, event, idx):
        if self.option_list is None or idx > self.option_list.size():
            return
        self.option_list.select_set(idx - 1)
        self.on_option_select(event)

    def move_img(self, character=None):
        """将图片移动到目标文件夹下的下拉菜单指定角色的文件夹中
        :param character: 目标角色名，如果为空则从下拉菜单中获取
        """
        # 获取总目标文件夹路径，如果为空则提示用户输入，如果不存在则提示用户文件夹不存在
        tgt_dir = self.tgt_entry.get()
        if not tgt_dir:
            warning_noinput = "Please input the target directory path."
            messagebox.showwarning("Warning", warning_noinput)
            self.status_bar.config(text=warning_noinput)
            self.tgt_browse_button.focus()
            return
        if not os.path.exists(tgt_dir) or not os.path.isdir(tgt_dir):
            warning_notfolder = "The target directory does not exist."
            messagebox.showwarning("Warning", warning_notfolder)
            self.status_bar.config(text=warning_notfolder)
            self.tgt_browse_button.focus()
            return

        # 获取目标角色名（文件夹名）
        if not character:
            character = self.tgt_option_menu.get()
            # 未选择角色则警告
            if character == "Pick a character":
                self.status_bar.config(text="Please choose a charactor.")
                return
        tgt_chr_dir = f"{tgt_dir}/{character}"
        # Logger.debug(tgt_chr_dir)

        # 获取当前图片绝对路径
        if not self.img_name:
            self.status_bar.config(text="There's no image to move.")
            return
        img_relpath = self.img_name
        img_abspath = f"{self.img_dir}/{img_relpath}"
        # Logger.debug(img_abspath)

        # 将图片移动到目标角色文件夹
        if not os.path.exists(tgt_chr_dir) or not os.path.isdir(tgt_chr_dir):
            os.makedirs(tgt_chr_dir)
        try:
            shutil.move(img_abspath, tgt_chr_dir)
        except Exception as e:
            self.status_bar.config(text=f"Error: {e}, failed to move {self.img_name} to {tgt_chr_dir}")
            return

        # 如果是最后一张图片，则将图片名和PIL.Image对象置空
        if len(self.img_paths) == 1:
            self.img_name = None
            self.img_pil = None
        # 加载后一张图片，并重新加载文件夹
        self.show_next_img()
        self.load_dir(is_reload=True)

        moved_msg = f"Moved {img_relpath} to {tgt_chr_dir}."
        Logger.debug(moved_msg)
        self.status_bar.config(text=moved_msg)

    def open_config_window(self, _=None):
        """打开配置字典窗口"""
        # 停用打开配置窗口按钮与快捷键
        self.config_button.config(state="disabled")
        self.master.unbind("<F10>")
        # 打开配置字典窗口
        config_window = tk.Toplevel(self.master)
        config_window.title("Dictionary Configuration")
        config_window.geometry("1000x400")
        config_window.wm_iconbitmap(Conf.LOGO_ICON_PATH)
        config_window.focus()
        DictEditor(config_window)  # 传入配置字典窗口对象

        def on_closing_config_window():
            if messagebox.askokcancel(
                "Quit", "Do you want to quit?\nChanges will not be automatically saved."
            ):
                self.config_button.config(state="enabled")
                self.master.bind("<F10>", self.open_config_window)
                config_window.destroy()
            else:
                config_window.focus()

        # 检测该窗口是否关闭，如果是则启用按钮和快捷键
        config_window.protocol("WM_DELETE_WINDOW", on_closing_config_window)
        # Logger.debug(Conf.DIR_KEYWORD_MAP)

    def open_filter_window(self, _=None):
        """打开过滤器窗口"""
        # 停用打开过滤器窗口按钮与快捷键
        self.filter_button.config(state="disabled")
        self.master.unbind("<F9>")
        # 打开过滤器窗口
        filter_window = tk.Toplevel(self.master)
        filter_window.title("Filter")
        filter_window.geometry("0x0")
        filter_window.wm_iconbitmap(Conf.LOGO_ICON_PATH)
        filter_window.focus()

        def on_closing_filter_window():
            self.filter_button.config(state="enabled")
            self.master.bind("<F9>", self.open_filter_window)
            filter_window.destroy()

        filter_window.protocol("WM_DELETE_WINDOW", on_closing_filter_window)
        filter_instance = Filter(filter_window, self.src_entry.get())
        if not filter_instance.safety:
            on_closing_filter_window()


if __name__ == '__main__':
    root = tk.Tk()
    root.title(Conf.PROJECT_NAME)
    app = Archiver(root)
    root.geometry(Conf.DEFAULT_WIN_SIZE)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    root.wm_iconbitmap(Conf.LOGO_ICON_PATH)
    root.minsize(400, 400)
    root.maxsize(1960, 1080)
    root.mainloop()
