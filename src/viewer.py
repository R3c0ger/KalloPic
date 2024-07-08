#!usr/bin/env python
# -*- coding: utf-8 -*-

import imghdr
import os
import subprocess
import time
import tkinter as tk
from functools import partial
from tkinter import filedialog, colorchooser
from tkinter import ttk, messagebox

import pyperclip
import send2trash
from PIL import Image, ImageTk, ImageOps

from src.config import Conf


# 图片后缀名
ImgSuffixes = (
    '.jpeg', '.JPEG',
    '.jpg', '.JPG',
    '.png', '.PNG',
    '.bmp', '.BMP',
    '.webp', '.WEBP',
)
# 图片适应模式，每个模式分别包含：程序内名称缩写字符串、英文全称、快捷键
# 拉伸小图不算在内，是布尔值
ImageFitModes = [
    ["os", "Original Size", "0"],  # 原始大小（不适用拉伸小图）
    ["fc", "Fit Window", "9"],  # fit canvas，适合窗口
    ["fw", "Fit Width", "8"],  # 适合宽度
    ["fh", "Fit Height", "7"],  # 适合高度
    ["sf", "Stretch Fill", "6"],  # 拉伸铺满（不适用拉伸小图）
]


def get_img_list(source_dir, is_recursive=False, sort_by_time=False, sort_by_size=False):
    """
    获取指定目录下的所有图片文件路径

    :param source_dir: 源目录
    :param is_recursive: 是否递归查找
    :param sort_by_time: 是否按创建时间排序
    :param sort_by_size: 是否按文件大小排序
    :return: 图片文件路径列表
    """
    img_list = []
    if not is_recursive:
        for img_relpath in os.listdir(source_dir):
            if img_relpath.endswith(ImgSuffixes):
                img_list.append(img_relpath)
    else:
        for _root, dirs, files in os.walk(source_dir):
            for img_relpath in files:
                if img_relpath.endswith(ImgSuffixes):
                    img_abspath = os.path.join(_root, img_relpath)
                    img_full_relpath = os.path.relpath(str(img_abspath), source_dir)
                    img_list.append(img_full_relpath)
    # print(f"共找到 {len(img_list)} 张图片")
    if sort_by_size:
        img_list.sort(key=lambda x: os.path.getsize(os.path.join(source_dir, x)))
    elif sort_by_time:
        img_list.sort(key=lambda x: os.path.getctime(os.path.join(source_dir, x)))
    return img_list


def get_exif_data(img_relpath, img_pil):
    """读取图片数据，包括文件类型、大小、分辨率、最后修改时间等信息
    YCbCr颜色空间、ICC profile等信息暂不考虑

    :param img_relpath: 图片相对路径。此时输入的已经是能打开的图片，工作目录也已切换
    :param img_pil: PIL.Image对象
    :return: 图片数据字典转换成的字符串
    """
    # 获取基本信息
    img_size = os.path.getsize(img_relpath)
    img_size_str = f"{img_size} B" if img_size < 1024 else \
        f"{round(img_size / 1024, 3)} KB" if img_size < 1024 ** 2 else \
        f"{round(img_size / 1024 ** 2, 3)} MB" if img_size < 1024 ** 3 else \
        f"{round(img_size / 1024 ** 3, 3)} GB"
    img_size_str = f"{img_size_str}" if img_size >= 1024 else img_size_str
    last_modified_ts = time.localtime(os.path.getmtime(img_relpath))
    last_modified = time.strftime('%Y-%m-%d %H:%M:%S', last_modified_ts)
    filetype = imghdr.what(img_relpath)
    data_str = (
        f"filename: {img_relpath}\n"
        f"filesize: {img_size_str}\n"
        f"last modified: {last_modified}\n"
        f"filetype: {filetype}\n"
        f"resolution: {img_pil.size[0]} x {img_pil.size[1]}"
    )
    brief_data_str = f"{img_size_str}, {filetype}, {img_pil.size[0]} x {img_pil.size[1]}"
    return data_str[:-1], brief_data_str


class ImageViewer:
    def __init__(self, master):
        # 根窗口及其标题
        self.master = master
        self.root_title = self.master.title().split(" - ")[0]
        # 打开的图片所在文件夹，所选源文件夹
        self.img_dir = ""  # 源文件夹路径
        self.img_paths = []  # 源文件夹中搜集到的图片列表
        self.current_index = 0  # 源文件夹中的当前图片索引
        # 图片展示
        self.img_name = None  # 当前图片的文件名
        self.img_pil = None  # 当前图片的PIL.Image对象
        self.fit_mode = "fc"  # 图片填充模式，默认为适应窗口
        self.strech_small = False  # 是否拉伸小图
        self.img_tag = "img"  # 图片标签
        self.drag_data = {"x": 0, "y": 0}  # 拖动数据
        # 图片信息展示
        self.show_info = False  # 是否显示图片信息
        self.info_str = ""  # 图片信息字符串
        self.brief_info_str = ""  # 图片简略信息字符串
        self.text_tag = "info_text"  # 文本标签
        # 其他
        self.error_retry_count = 0  # 加载图片失败重试次数
        self.layout = {}  # 被隐藏控件的布局信息
        self.help_window = None  # 帮助窗口

        # 显示图片
        self.canvas = tk.Canvas(master)
        self.canvas.pack(fill=tk.BOTH, expand=1)
        self.canvas.config(highlightthickness=0, bg='black')
        self.img_in_canvas = None  # 当前图片的ImageTk对象

        # 打开源文件夹
        self.src_frame = ttk.Frame(master)
        self.src_frame.pack(fill=tk.X)
        # 源文件夹标签
        self.src_label = ttk.Label(self.src_frame, text="Source Folder:", width=12)
        self.src_label.pack(side=tk.LEFT, padx=10)
        # 输入框
        self.src_entry = ttk.Entry(self.src_frame)
        self.src_entry.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self.src_entry.insert(0, "example: D:/Pictures")
        # 选择文件夹按钮
        self.src_browse_dir = partial(self.input_dir, self.src_entry)
        self.src_browse_button = ttk.Button(self.src_frame, text="Browse", command=self.src_browse_dir)
        self.src_browse_button.pack(side=tk.LEFT)
        # 从文件夹加载图片
        self.src_frame.pack(fill=tk.X)
        # 选择按钮，控制是否递归查找
        self.load_recursive = tk.IntVar()
        self.load_recursive.set(1)
        self.load_checkbutton = ttk.Checkbutton(
            self.src_frame,
            text="Recursive",
            variable=self.load_recursive,
            width=8
        )
        self.load_checkbutton.pack(side=tk.LEFT, padx=10)
        # 加载图片按钮
        self.load_button = ttk.Button(
            self.src_frame,
            text="Load Images",  # (sort by filename)
            command=self.load_dir,
            width=15
        )
        self.load_button.pack(fill=tk.X)

        # 功能按钮
        self.button_frame = ttk.Frame(master)
        self.button_frame.pack(anchor=tk.CENTER, pady=5)
        # 第一张、最后一张按钮
        self.first_button = ttk.Button(self.button_frame, text="<|| First", command=self.show_first_img, width=8)
        self.first_button.grid(row=0, column=0, padx=10)
        self.last_button = ttk.Button(self.button_frame, text="Last ||>", command=self.show_last_img, width=8)
        self.last_button.grid(row=0, column=3, padx=10)
        # 上一张、下一张按钮
        self.prev_button = ttk.Button(self.button_frame, text="< Prev", command=self.show_prev_img, width=8)
        self.prev_button.grid(row=0, column=1, padx=10)
        self.next_button = ttk.Button(self.button_frame, text="Next >", command=self.show_next_img, width=8)
        self.next_button.grid(row=0, column=2, padx=10)
        # 将当前图片移动到回收站
        self.delete_button = ttk.Button(self.button_frame, text="Delete", command=self.delete_img, width=8)
        self.delete_button.grid(row=0, column=4, padx=10)
        # 输入数字跳转至对应的图片
        self.goto_frame = ttk.Frame(self.button_frame)
        self.goto_frame.grid(row=0, column=5, padx=10)
        self.goto_label = ttk.Label(self.goto_frame, text="Go to Image:", width=12)
        self.goto_label.pack(side=tk.LEFT)
        self.goto_entry = ttk.Entry(self.goto_frame, width=6)
        self.goto_entry.pack(side=tk.LEFT)
        self.goto_button = ttk.Button(
            self.goto_frame,
            text="Go",
            command=lambda: self.goto_img(self.goto_entry.get()),
            width=5
        )
        self.goto_button.pack(side=tk.RIGHT)
        # 使用外部默认程序打开图片
        self.open_button = ttk.Button(
            self.button_frame,
            text="Open",
            command=lambda: os.startfile(self.img_name) if self.img_name else None,
            width=8
        )
        self.open_button.grid(row=0, column=6, padx=10)
        # 查看图片信息，打开相应窗口
        self.info_button = ttk.Button(
            self.button_frame,
            text="Show Info",
            command=self.switch_show_info,
            width=10
        )
        self.info_button.grid(row=0, column=7, padx=10)
        # 按时间排序，重新加载当前文件夹
        self.sort_by_time_button = ttk.Button(
            self.button_frame,
            text="Sort by Time",
            command=lambda: self.load_dir(is_reload=True, sort_by_time=True),
            width=11
        )
        self.sort_by_time_button.grid(row=0, column=9, padx=10)
        # 按文件大小排序，重新加载当前文件夹
        self.sort_by_size_button = ttk.Button(
            self.button_frame,
            text="Sort by Size",
            command=lambda: self.load_dir(is_reload=True, sort_by_size=True),
            width=11
        )
        self.sort_by_size_button.grid(row=0, column=10, padx=10)
        # 重新加载当前文件夹（不按时间或大小排序，即按文件名排序）
        self.reload_button = ttk.Button(
            self.button_frame,
            text="Reload",
            command=lambda: self.load_dir(is_reload=True),
            width=8
        )
        self.reload_button.grid(row=0, column=8, padx=10)
        # 倒序显示图片，不用重新加载源文件夹
        self.reverse_button = ttk.Button(
            self.button_frame,
            text="Reverse",
            command=self.reverse_img,
            width=8
        )
        self.reverse_button.grid(row=0, column=11, padx=10)
        # 隐藏各栏
        self.hide_button = ttk.Button(
            self.button_frame,
            text="Hide widgets",
            command=self.hide_widgets,
            width=13
        )
        self.hide_button.grid(row=0, column=12, padx=10)

        # 信息通知栏，左为状态栏，右为帮助栏
        self.info_bar = ttk.Frame(master)
        self.info_bar.pack(side=tk.BOTTOM, fill=tk.X)
        # 状态栏
        self.status_bar = ttk.Label(self.info_bar, text="Ready.", anchor=tk.W)
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, padx=10)
        # 帮助栏，显示组件的帮助提示
        self.help_bar = ttk.Label(self.info_bar, text="", anchor=tk.W)
        self.help_bar.pack(side=tk.RIGHT, fill=tk.X, padx=10)

        # 右键菜单
        self.context_menu = tk.Menu(master, tearoff=0)
        # 1. 文件相关
        # 使用默认软件打开图片
        self.context_menu.add_command(
            label="Open",
            accelerator="Ctrl+O",
            command=lambda: os.startfile(self.img_name) if self.img_name else None
        )
        # 定位图片，打开资源管理器并选中到该图片
        self.context_menu.add_command(
            label="Locate File in Explorer", command=self.locate_file, accelerator="Ctrl+L"
        )
        # 复制信息
        self.copy_menu = tk.Menu(self.context_menu, tearoff=0)
        self.context_menu.add_cascade(label="Copy Info", menu=self.copy_menu)
        self.copy_menu.add_command(
            label="Copy Filename",
            accelerator="Ctrl+C",
            command=lambda: pyperclip.copy(self.img_name)
        )
        self.copy_menu.add_command(
            label="Copy Absolute Path",
            accelerator="Ctrl+Shift+C",
            command=lambda: pyperclip.copy(os.path.abspath(self.img_name))
        )
        self.copy_menu.add_command(
            label="Copy Image Data",
            accelerator="Ctrl+Y",
            command=lambda: pyperclip.copy(self.info_str)
        )
        # 删除当前图片
        self.context_menu.add_command(
            label="Delete",
            accelerator="Delete",
            command=self.delete_img
        )
        self.context_menu.add_separator()
        # 2. 更改背景颜色。提供黑、白、蓝、红、绿、护眼绿等颜色，以及自定义颜色
        self.bgcolor_menu = tk.Menu(self.context_menu, tearoff=0)
        self.context_menu.add_cascade(label="Change Background Color", menu=self.bgcolor_menu)
        self.bgcolor_menu.add_command(label="Black", command=lambda: self.canvas.config(bg='black'))
        self.bgcolor_menu.add_command(label="White", command=lambda: self.canvas.config(bg='white'))
        self.bgcolor_menu.add_command(label="Blue", command=lambda: self.canvas.config(bg='blue'))
        self.bgcolor_menu.add_command(label="Red", command=lambda: self.canvas.config(bg='red'))
        self.bgcolor_menu.add_command(label="Green", command=lambda: self.canvas.config(bg='green'))
        self.bgcolor_menu.add_command(label="Eye Protection Green", command=lambda: self.canvas.config(bg='#C1FFC1'))
        self.bgcolor_menu.add_separator()
        self.bgcolor_menu.add_command(label="Custom Color", command=self.custom_bg_color)
        # 3. 更改图片适应模式。提供原始大小、适应窗口、适应宽度、适应高度、拉伸铺满等模式
        self.fillmode_menu = tk.Menu(self.context_menu, tearoff=0)
        self.context_menu.add_cascade(label="Change Fit Mode", menu=self.fillmode_menu)
        self.fillmode_menu.add_command(
            label=ImageFitModes[0][1],
            accelerator=f"{ImageFitModes[0][2]}",
            command=lambda: self.change_fit_mode(ImageFitModes[0][0])
        )
        self.fillmode_menu.add_command(
            label=ImageFitModes[1][1],
            accelerator=f"{ImageFitModes[1][2]}",
            command=lambda: self.change_fit_mode(ImageFitModes[1][0])
        )
        self.fillmode_menu.add_command(
            label=ImageFitModes[2][1],
            accelerator=f"{ImageFitModes[2][2]}",
            command=lambda: self.change_fit_mode(ImageFitModes[2][0])
        )
        self.fillmode_menu.add_command(
            label=ImageFitModes[3][1],
            accelerator=f"{ImageFitModes[3][2]}",
            command=lambda: self.change_fit_mode(ImageFitModes[3][0])
        )
        self.fillmode_menu.add_command(
            label=ImageFitModes[4][1],
            accelerator=f"{ImageFitModes[4][2]}",
            command=lambda: self.change_fit_mode(ImageFitModes[4][0])
        )
        self.fillmode_menu.add_separator()
        self.fillmode_menu.add_checkbutton(
            label="Strech Small",
            accelerator="-",
            command=self.switch_strech_small
        )
        # 4. 图片操作
        self.rotate_menu = tk.Menu(self.context_menu, tearoff=0)
        self.context_menu.add_cascade(label="Rotate/Flip", menu=self.rotate_menu)
        # 左/右旋90度、旋转180度、水平/垂直翻转
        self.rotate_menu.add_command(label="Rotate 90° Left", command=lambda: self.rotate_img(90))
        self.rotate_menu.add_command(label="Rotate 90° Right", command=lambda: self.rotate_img(-90))
        self.rotate_menu.add_command(label="Rotate 180°", command=lambda: self.rotate_img(180))
        self.rotate_menu.add_separator()
        self.rotate_menu.add_command(label="Flip Horizontal", command=lambda: self.flip_img("h"))
        self.rotate_menu.add_command(label="Flip Vertical", command=lambda: self.flip_img("v"))
        self.context_menu.add_checkbutton(label="Invert Colors", command=self.invert_img)  # 反色
        # TODO: (PIL)OSError: not supported for mode RGBA
        # 5. 排序
        self.sort_menu = tk.Menu(self.context_menu, tearoff=0)
        self.context_menu.add_cascade(label="Sort Images", menu=self.sort_menu)
        self.sort_menu.add_command(
            label="Sort by Time",
            accelerator="Alt+T",
            command=lambda: self.load_dir(is_reload=True, sort_by_time=True)
        )
        self.sort_menu.add_command(
            label="Sort by Size",
            accelerator="Alt+S",
            command=lambda: self.load_dir(is_reload=True, sort_by_size=True)
        )
        self.sort_menu.add_command(
            label="Sort by Filename(Reload)",
            accelerator="Enter",
            command=lambda: self.load_dir(is_reload=True)
        )
        self.sort_menu.add_separator()
        self.sort_menu.add_command(
            label="Reverse Images(no Reload)",
            accelerator="Alt+R",
            command=self.reverse_img
        )
        self.context_menu.add_separator()
        # 6. 其他
        # 展示图片信息、隐藏控件、最大化/退出最大化、全屏/退出全屏、帮助、退出
        self.context_menu.add_command(
            label="Show Info",
            accelerator="Tab",
            command=self.switch_show_info
        )
        self.context_menu.add_command(
            label="Hide Widgets",
            accelerator="Ctrl+H",
            command=self.hide_widgets
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label="Maximize/Restore",
            accelerator="Ctrl+M",
            command=self.maximize_restore
        )
        self.context_menu.add_command(
            label="Fullscreen/Restore",
            accelerator="F11",
            command=self.fullscreen_restore
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label="Help",
            accelerator="F12",
            command=self.show_help_window
        )
        self.context_menu.add_command(
            label="Quit",
            accelerator="Ctrl+W",
            command=self.master.quit
        )

        # 帮助提示信息
        # 第一列为快捷键，第二列为（快捷键）帮助提示信息，第三列为对应的控件，第四列为控件的帮助提示信息
        self.help_items = [
            ("", "Enter the source folder path at the right.", self.src_label),
            ("", "Type the source folder path. (Ctrl+S to browse)", self.src_entry),
            ("F12", "Show this help window.", None),
            ("Ctrl+S", "Browse to select the source folder.", self.src_browse_button),
            ("Ctrl+`", "Check to load images recursively.", self.load_checkbutton),
            ("Enter", "Load/reload the current folder.", self.load_button),
            ("", "Reload the current folder. (Enter)", self.reload_button),
            ("Home", "Show the first image.", self.first_button),
            ("End", "Show the last image.", self.last_button),
            ("Left", "Show the previous image.", self.prev_button),
            ("Right", "Show the next image.", self.next_button),
            ("-", "Switch from/to stretching small images mode.", None),
            ("6", "Stretch the image to fill the window.", None),
            ("7", "Resize the image to fit the height of the window.", None),
            ("8", "Resize the image to fit the width of the window.", None),
            ("9", "Resize the image to fit the window.", None),
            ("0", "Resize the image to its original size.", None),
            ("Alt+T", "Sort images by time.", self.sort_by_time_button),
            ("Alt+S", "Sort images by size.", self.sort_by_size_button),
            ("Alt+R", "Reverse the order of images.", self.reverse_button),
            ("Ctrl+O", "Open the current image with the default program.", self.open_button),
            ("Ctrl+L", "Locate the current image in Explorer.", None),
            ("Ctrl+C", "Copy the current image filename.", None),
            ("Ctrl+Shift+C", "Copy the absolute path of the current image.", None),
            ("Ctrl+Y", "Copy the image data.", None),
            ("Delete", "Move the current image to the recycle bin.", self.delete_button),
            ("Ctrl+H", "Hide/show all widgets.", self.hide_button, "Hide all widgets."),
            ("Tab", "Show/hide image information.", self.info_button),
            ("Ctrl+M", "Maximize/Restore the window.", None),
            ("F11", "Fullscreen/Restore the window.", None),
            ("Ctrl+W", "Quit the application.", None),
            ("", "Enter the image number to go to. (Ctrl+F)", self.goto_label),
            ("Ctrl+F", "Focus on the image number input field.", self.goto_entry, "Type the image number to go to."),
            ("Ctrl+G", "Go to the specified image which you typed.", self.goto_button),
        ]

        # 预执行
        self.pre_execute()
        # 不可隐藏的控件列表
        self.unhidden_widgets = [self.canvas, self.context_menu]

    # 预执行的方法
    def pre_execute(self):
        """预执行的绑定事件"""
        self.bind_events_about_canvas()
        self.bind_shortcuts()
        self.bind_help_tips()

    def bind_events_about_canvas(self):
        """绑定画布事件"""
        # 画布缩放或移动
        self.canvas.bind("<Configure>", self.canvas_move_or_resize)
        # 鼠标拖动图片
        self.canvas.tag_bind(self.img_tag, "<ButtonPress-1>", self.on_image_press)
        self.canvas.tag_bind(self.img_tag, "<B1-Motion>", self.on_image_drag)
        # 鼠标右键菜单
        self.canvas.bind("<Button-3>", self.show_context_menu)

    def on_image_press(self, event):
        """记录鼠标点击位置"""
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_image_drag(self, event):
        """拖动图片"""
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        self.canvas.move(self.img_tag, dx, dy)
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def bind_shortcuts(self):
        """绑定快捷键"""
        self.master.bind("<Left>", lambda event: self.show_prev_img())
        self.master.bind("<Right>", lambda event: self.show_next_img())
        self.master.bind("<Up>", lambda event: self.show_prev_img())
        self.master.bind("<Down>", lambda event: self.show_next_img())
        self.canvas.bind(
            "<MouseWheel>",
            lambda event: self.show_prev_img() if event.delta > 0
            else self.show_next_img()
        )
        self.master.bind("<Home>", lambda event: self.show_first_img())
        self.master.bind("<End>", lambda event: self.show_last_img())
        self.master.bind("<Delete>", lambda event: self.delete_img())
        self.master.bind("<Tab>", lambda event: self.switch_show_info())
        self.master.bind("<Control-c>", lambda event: pyperclip.copy(self.img_name))
        self.master.bind("<Control-Shift-C>", lambda event: pyperclip.copy(os.path.abspath(self.img_name)))
        self.master.bind("<Control-y>", lambda event: pyperclip.copy(self.info_str))
        self.master.bind("<Control-`>", lambda event: self.load_recursive.set(not self.load_recursive.get()))
        self.master.bind("<Return>", lambda event: self.load_dir())
        self.master.bind("<Control-o>", lambda event: os.startfile(self.img_name) if self.img_name else None)
        self.master.bind("<Control-l>", lambda event: self.locate_file())
        self.master.bind("<Control-w>", lambda event: self.master.quit())
        self.master.bind("<Control-s>", lambda event: self.src_browse_dir())
        self.master.bind("<Control-r>", lambda event: self.reverse_button.invoke())
        self.master.bind("<Alt-s>", lambda event: self.sort_by_size_button.invoke())
        self.master.bind("<Alt-t>", lambda event: self.sort_by_time_button.invoke())
        self.master.bind("<Alt-r>", lambda event: self.reload_button.invoke())
        # 最大化/退出最大化、全屏、最小化
        self.master.bind("<Control-m>", lambda event: self.maximize_restore())
        self.master.bind(
            "<Alt-m>", lambda event:
            self.master.iconify() or self.master.attributes("-fullscreen", False)
        )
        self.master.bind("<F11>", lambda event: self.fullscreen_restore())
        # 聚焦在跳转输入框
        self.master.bind("<Control-f>", lambda event: (
            self.goto_entry.focus(), self.goto_entry.select_range(0, tk.END)))
        # 跳转到指定图片
        self.master.bind("<Control-g>", lambda event: self.goto_button.invoke())
        # 隐藏/显示控件
        self.master.bind(
            "<Control-h>", lambda event: self.show_widgets()
            if not self.hide_button.winfo_ismapped()
            else self.hide_widgets()
        )
        # 更改背景颜色
        self.master.bind("<Control-b>", lambda event: self.custom_bg_color())
        # 更改图片适应模式
        for mode in ImageFitModes:
            self.master.bind(
                f"<{mode[2]}>",
                lambda event, addr=mode[0]: self.change_fit_mode(addr)
            )
        # 拉伸小图
        self.master.bind("<minus>", lambda event: self.switch_strech_small())
        self.master.bind("<F12>", lambda event: self.show_help_window())

    def bind_help_tips(self):
        """绑定控件的帮助提示信息"""
        for help_tuple in self.help_items:
            if help_tuple[2]:
                help_tip = help_tuple[3] if len(help_tuple) > 3 else help_tuple[1]
                help_tip += f" ({help_tuple[0]})" if help_tuple[0] else ""
                help_tuple[2].bind("<Enter>", lambda e, tip=help_tip: self.help_bar.config(text=tip))
                help_tuple[2].bind("<Leave>", lambda e: self.help_bar.config(text=""))

    def show_help_window(self):
        """显示帮助窗口"""
        # 若已经打开，则直接返回
        if self.help_window is not None and tk.Toplevel.winfo_exists(self.help_window):
            self.help_window.focus()
            return

        self.help_window = tk.Toplevel(self.master)
        self.help_window.title("Help")
        self.help_window.geometry("600x400")
        self.help_window.focus()  # 防止信息窗口挡着

        tree_frame = ttk.Frame(self.help_window)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        tree_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tree = ttk.Treeview(
            tree_frame,
            columns=("Key", "Description"),
            show="headings",
            yscrollcommand=tree_scrollbar.set
        )
        tree.heading("Key", text="Key", anchor="w")
        tree.heading("Description", text="Description", anchor="w")
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 绑定Scrollbar到Treeview
        tree_scrollbar.config(command=tree.yview)

        # 插入快捷键和帮助信息
        for help_tuple in self.help_items:
            if help_tuple[0]:
                tree.insert("", tk.END, values=(help_tuple[0], help_tuple[1]))

        # 添加版本信息
        version_label = ttk.Label(
            self.help_window,
            text=f"{Conf.PROJECT_NAME}{Conf.VERSION}",
            anchor="center"
        )
        version_label.pack(pady=10)

        self.help_window.protocol("WM_DELETE_WINDOW", self.on_help_window_close)

    def on_help_window_close(self):
        self.help_window.destroy()
        self.help_window = None

    @staticmethod
    def input_dir(entry):
        dir_path = filedialog.askdirectory()
        if dir_path:
            entry.delete(0, tk.END)
            entry.insert(0, dir_path)

    def load_dir(self, is_reload=False, sort_by_time=False, sort_by_size=False):
        # 获取输入的文件夹路径，如果为空则提示用户输入，如果不存在则提示用户文件夹不存在
        src_dir = self.src_entry.get()
        # 如果是重新加载，则将源文件夹直接设定为当前文件夹属性值，若还没有源文件夹则获取用户输入
        if is_reload and self.img_dir:
            src_dir = self.img_dir
        if not src_dir:
            messagebox.showwarning("Warning", "Please input a directory path.")
            self.status_bar.config(text="Please input a directory path.")
            self.src_browse_button.focus()
            return
        if not os.path.exists(src_dir) or not os.path.isdir(src_dir):
            messagebox.showwarning("Warning", "The directory does not exist.")
            self.status_bar.config(text="The directory does not exist.")
            self.src_browse_button.focus()
            return
        # 获取是否递归查找
        recursive = True if self.load_recursive.get() == 1 else False
        # 获取图片列表
        self.img_paths = get_img_list(src_dir, recursive, sort_by_time, sort_by_size)

        self.master.title(f"{self.root_title} - {src_dir}")
        # 如果没有找到图片，则提示用户
        if not self.img_paths:
            self.status_bar.config(text="No images found.")
            return
        # 上述过程检查完后，存在且有图片的目录才能作为当前目录，存放在类的属性中
        self.img_dir = src_dir
        os.chdir(self.img_dir)
        # 若还能从列表中找到当前图片的文件名，姑且视为重新加载，从当前图片开始显示
        if self.img_name in self.img_paths:
            self.current_index = self.img_paths.index(self.img_name)
        else:
            self.current_index = 0
        # self.print_check()
        self.load_img()

    def resize_img(self, img, fit_mode="fc", strech_small=False):
        """根据图片显示模式调整图片大小"""
        if fit_mode == "os":
            return img
        elif fit_mode == "sf":
            return img.resize((self.canvas.winfo_width(), self.canvas.winfo_height()))
        img_width, img_height = img.size
        scale_width = self.canvas.winfo_width() / img_width
        scale_height = self.canvas.winfo_height() / img_height
        scale_min = min(scale_width, scale_height)
        if fit_mode == "fc":
            new_size = (int(img_width * scale_min), int(img_height * scale_min))
        elif fit_mode == "fw":
            new_size = (self.canvas.winfo_width(), int(img_height * scale_width))
        else:  # fit_mode == "fh"
            new_size = (int(img_width * scale_height), self.canvas.winfo_height())
        # 如果图片小于窗口，且不拉伸小图，则不进行缩放
        if strech_small or min(scale_width, scale_height) < 1:
            return img.resize(new_size)
        else:
            return img

    def draw_img(self, img):
        """在画布上绘制图片，同时绘制图片信息文本"""
        # 根据图片显示模式调整图片大小，保存在属性中
        img = self.resize_img(img, self.fit_mode, self.strech_small)
        self.img_in_canvas = ImageTk.PhotoImage(img)
        # 清除已有图片和文本
        self.canvas.delete(tk.ALL)
        # 绘制新图片，居中显示
        canvas_w, canvas_h = self.canvas.winfo_width(), self.canvas.winfo_height()
        self.canvas.create_image(
            canvas_w // 2, canvas_h // 2,
            image=self.img_in_canvas,
            tags=self.img_tag
        )
        # 复位canvas视图
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        if self.show_info:
            self.show_info_text()

    def handle_image_error(self, e, to_next=True):
        """处理图片加载错误"""
        # 尝试加载失败，计数器加1，如果所有图片都加载失败，则提示用户
        self.error_retry_count += 1
        if self.error_retry_count > len(self.img_paths):
            self.status_bar.config(text="All images failed to load.")
            self.error_retry_count = 0  # 报错后重置错误计数
            return
        # 向前或向后加载图片时，跳过的方式也分别为向前或向后
        self.show_next_img() if to_next else self.show_prev_img()
        # 在新的状态栏内容后面追加无法打开的报错信息
        self.status_bar.config(
            text=f"{self.status_bar.cget('text')}\n"
                 f"Error: {e}, skipping {self.img_paths[self.current_index]}")
        return

    def load_img(self, to_next=True):
        # 如果没有图片，则直接返回
        if not 0 <= self.current_index < len(self.img_paths):
            return
        # 根据索引加载图片
        img_relpath = self.img_paths[self.current_index]
        try:
            img = Image.open(img_relpath)
        # 如果图片无法打开，则跳过该图片
        except Exception as e:
            self.handle_image_error(e, to_next)
            return
        # 更新类属性
        self.img_pil = img  # 存储PIL.Image对象
        self.img_name = img_relpath
        self.error_retry_count = 0  # 成功加载图片后，重置错误计数
        # 获取图片信息备用，如需要显示信息就显示
        self.info_str, self.brief_info_str = get_exif_data(img_relpath, self.img_pil)
        # 在canvas中绘制图片（，并展示图片信息）
        self.draw_img(self.img_pil)
        # 更新窗口标题、状态栏
        rate_str = f"{self.current_index + 1}/{len(self.img_paths)}"
        self.status_bar.config(text=f"Image {rate_str}: {img_relpath}")
        self.master.title(f"{self.root_title} - {self.img_dir} - {img_relpath} [{rate_str}]")
        # self.print_check()

    def print_check(self):
        attr_log = f"Attributes:\n" + \
            f"Dir: {self.img_dir}\n" + \
            f"Paths Length: {len(self.img_paths)}\n" + \
            f"Current Index: {self.current_index}\n" + \
            f"Image Name: {self.img_name}\n" + \
            f"Show Info: {self.show_info}\n" + \
            f"Info: {self.brief_info_str}\n" + \
            f"Error Retry Count: {self.error_retry_count}\n" + \
            f"Fit Mode: {self.fit_mode}\n" + \
            f"Strech Small: {self.strech_small}\n"
        print(attr_log)

    def show_prev_img(self):
        if len(self.img_paths) == 0:
            return
        self.current_index = (self.current_index - 1) % len(self.img_paths)
        self.load_img(to_next=False)

    def show_next_img(self):
        if len(self.img_paths) == 0:
            return
        self.current_index = (self.current_index + 1) % len(self.img_paths)
        self.load_img(to_next=True)

    def show_first_img(self):
        if len(self.img_paths) == 0 or self.current_index == 0:
            return
        self.current_index = 0
        self.load_img(to_next=True)

    def show_last_img(self):
        if len(self.img_paths) == 0 or self.current_index == len(self.img_paths) - 1:
            return
        self.current_index = len(self.img_paths) - 1
        self.load_img(to_next=False)

    def delete_img(self):
        if len(self.img_paths) == 0:
            return
        img_relpath = self.img_paths[self.current_index]
        try:
            # 将图片移动到回收站
            send2trash.send2trash(img_relpath)
            self.status_bar.config(text=f"Image {img_relpath} has been moved to the recycle bin.")
            self.img_paths.pop(self.current_index)
            # 如果删除的是最后一张图片，则将索引减1，显示前一张图片
            if self.current_index >= len(self.img_paths):
                self.current_index -= 1
            self.load_img()
        except Exception as e:
            self.status_bar.config(text=f"Error: {e}, failed to delete {img_relpath}")

    def goto_img(self, index):
        if len(self.img_paths) == 0:
            return
        try:
            index = int(index)
        except ValueError:
            self.status_bar.config(text="Please input an integer.")
            return
        if index < 1 or index > len(self.img_paths):
            self.status_bar.config(text=f"Please input an integer between 1 and {len(self.img_paths)}.")
            return
        self.current_index = index - 1
        self.load_img()

    def reverse_img(self):
        if len(self.img_paths) == 0:
            return
        self.img_paths.reverse()
        self.load_img()

    def show_info_text(self):
        self.canvas.delete(self.text_tag)
        offsets = [(0, 0), (0, 2), (2, 2), (2, 0), (1, 1)]
        fills = ['black', 'black', 'black', 'black', 'white']
        for offset, fill in zip(offsets, fills):
            self.canvas.create_text(
                offset[0], offset[1], anchor='nw',
                text=self.info_str, font=("", 14, "bold"), fill=fill,
                tags=self.text_tag
            )

    def switch_show_info(self):
        """切换是否显示图片信息"""
        self.show_info = not self.show_info
        if self.show_info:
            self.show_info_text()
            # 更改按钮和右键菜单文字
            self.info_button.config(text="Hide Info")
            self.context_menu.entryconfig(11, label="Hide Info")
        else:
            self.canvas.delete(self.text_tag)
            # 更改按钮和右键菜单文字
            self.info_button.config(text="Show Info")
            self.context_menu.entryconfig(11, label="Show Info")

    def canvas_move_or_resize(self, _):
        """窗口移动时，移动画布上的图片与图片信息"""
        if self.img_pil:
            self.draw_img(self.img_pil)

    def hide_widgets(self):
        """隐藏所有控件"""
        for widget in self.master.winfo_children():
            if widget not in self.unhidden_widgets:
                # 如果组件是.!toplevel则跳过
                if str(widget).startswith(".!toplevel"):
                    continue
                # 保存控件的布局信息
                self.layout[widget] = widget.pack_info()
                widget.pack_forget()
        # 修改右键菜单中的名称和命令
        self.context_menu.entryconfig(12, label="Show Widgets", command=self.show_widgets)

    def show_widgets(self):
        """显示所有控件"""
        for widget in self.master.winfo_children():
            if widget not in self.unhidden_widgets:
                # 如果组件是.!toplevel则跳过
                if str(widget).startswith(".!toplevel"):
                    continue
                widget.pack(self.layout[widget])
        # 修改右键菜单中的名称和命令
        self.context_menu.entryconfig(12, label="Hide Widgets", command=self.hide_widgets)

    def show_context_menu(self, event):
        """显示右键菜单"""
        self.context_menu.post(event.x_root, event.y_root)

    def custom_bg_color(self):
        """自定义背景颜色"""
        color = colorchooser.askcolor()
        if color[1]:
            self.canvas.config(bg=str(color[1]))
        else:
            self.status_bar.config(text="No color selected.")

    def change_fit_mode(self, mode_addr):
        """更改图像适应模式"""
        print(f"Change fit mode to {mode_addr}")
        self.fit_mode = mode_addr
        self.load_img()

    def switch_strech_small(self):
        """切换是否拉伸小图"""
        self.strech_small = not self.strech_small
        self.load_img()

    def locate_file(self):
        """在文件资源管理器中定位文件"""
        if self.img_name:
            file_path = os.path.abspath(self.img_name)
            try:
                subprocess.run(['explorer', '/select,', os.path.normpath(file_path)])
            except Exception as e:
                self.status_bar.config(text=f"Error: {e}, failed to locate {self.img_name}")

    def rotate_img(self, angle):
        """旋转图片"""
        if self.img_pil:
            self.img_pil = self.img_pil.rotate(angle, expand=True)
            self.draw_img(self.img_pil)

    def flip_img(self, direction):
        """翻转图片"""
        if self.img_pil:
            if direction == "h":
                self.img_pil = self.img_pil.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            else:
                self.img_pil = self.img_pil.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            self.draw_img(self.img_pil)

    def invert_img(self):
        """反色"""
        if self.img_pil:
            self.img_pil = ImageOps.invert(self.img_pil)
            self.draw_img(self.img_pil)

    def maximize_restore(self):
        """最大化/还原窗口"""
        if self.master.state() == 'normal':
            self.master.state('zoomed')
        else:
            self.master.state('normal')
        self.master.attributes("-fullscreen", False)

    def fullscreen_restore(self):
        """全屏/还原窗口"""
        self.master.attributes("-fullscreen", not self.master.attributes("-fullscreen"))


if __name__ == '__main__':
    root = tk.Tk()
    root.title(Conf.PROJECT_NAME)
    app = ImageViewer(root)
    root.geometry(Conf.DEFAULT_WIN_SIZE)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    root.wm_iconbitmap(Conf.LOGO_ICON_PATH)
    root.minsize(400, 400)
    root.maxsize(1960, 1080)
    root.mainloop()
