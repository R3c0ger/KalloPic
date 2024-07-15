#!usr/bin/env python
# -*- coding: utf-8 -*-

import errno
import itertools
import math
import os
import shutil
import string
import tkinter as tk
from time import strftime, localtime
from tkinter import ttk, messagebox, filedialog

from send2trash import send2trash

from src.config import Conf


class FilterConfig:
    delete_mode_list = ["trash", "extract"]  # 移动到回收站、移动到文件夹下的特殊文件夹
    delete_dir = "$$DELETE"  # 源文件夹下用于存储被删除文件的文件夹名称

    def __str__(self):
        return (f"All delete modes: {self.delete_mode_list}\n"
                f"Delete directory: {self.delete_dir}")


class Filter:
    def __init__(self, master, dir_abspath, logger=None):
        self.master = master
        self.dir_abspath = dir_abspath.replace("/", "\\")
        self.safety = self._check_dir()  # 检查目录是否存在
        if not self.safety:
            self.master.destroy()
            return
        # 默认值
        self.delete_dir = "$$DELETE"
        self.delete_mode_list = ["trash", "extract"]

        # 初始化过滤器配置
        self.dir_conf = FilterConfig()
        self.delete_dir_abspath = os.path.join(self.dir_abspath, self.dir_conf.delete_dir)
        print(self.dir_conf, "\n\t", self.delete_dir_abspath)
        # 初始化窗口
        self.title = "Filter"
        self.master.title(f"{self.title} - {self.dir_abspath}")
        self.master.geometry("1000x600")
        self.master.resizable(False, False)

        # 统计信息
        self.file_stat = self._count_files()
        self.stat_group = ttk.LabelFrame(
            master,
            text="File statistics of current folder (close and open again to refresh)"
        )
        self.stat_group.pack(side=tk.TOP, padx=5, pady=5, expand=0, fill=tk.X)
        self.firstline_frame = ttk.Frame(self.stat_group)
        self.firstline_frame.pack(anchor=tk.W, fill=tk.X, expand=1)
        # 所有文件统计信息标签
        self.count_files_label = ttk.Label(self.firstline_frame, text="All files statistics:")
        self.count_files_label.pack(side=tk.LEFT, padx=5)
        # 打开文件夹
        self.open_dir_button = ttk.Button(
            self.firstline_frame, text="Open the folder",
            command=self.open_dir, width=20
        )
        self.open_dir_button.pack(side=tk.RIGHT, padx=5)
        # 所有文件统计信息文本框
        self.count_files_rst = tk.Text(self.stat_group, height=3)
        self.count_files_rst.pack(padx=5, pady=5, expand=1, fill=tk.X)
        self.count_files_rst.insert(tk.END, self.file_stat[0])
        self.count_files_rst.config(state=tk.DISABLED, wrap=tk.NONE, relief=tk.FLAT)
        # 图片统计信息标签
        self.count_imgs_label = ttk.Label(self.stat_group, text="Image files statistics:")
        self.count_imgs_label.pack(padx=5, anchor=tk.W)
        # 图片统计信息文本框
        self.count_imgs_rst = tk.Text(self.stat_group, height=1)
        self.count_imgs_rst.pack(padx=5, pady=5, expand=1, fill=tk.X)
        self.count_imgs_rst.insert(tk.END, self._get_img_stat())
        self.count_imgs_rst.config(state=tk.DISABLED, wrap=tk.NONE, relief=tk.FLAT)

        # 过滤功能组件，三栏，最左边一栏为功能按钮，中间一栏为功能参数配置，最右边一栏为输出结果文本框
        self.filter_group = ttk.LabelFrame(master, text="Filter functions")
        self.filter_group.pack(side=tk.TOP, padx=5, pady=5, expand=1, fill=tk.BOTH)
        # 附注，注明接下来下面给出的所有功能，所筛选的图片都不包括/delete_dir中的图片
        self.note_label = ttk.Label(
            self.filter_group,
            text=("p.s. The functions below are based on all the images found "
                  "recursively in the source folder, excluding those in the delete folder.")
        )
        self.note_label.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5)
        # 功能按钮栏
        self.func_frame = ttk.Frame(self.filter_group)
        self.func_frame.pack(side=tk.LEFT, anchor=tk.N, expand=0, fill=tk.Y)
        # 参数配置栏
        self.param_frame = ttk.Frame(self.filter_group)
        self.param_frame.pack(side=tk.LEFT, anchor=tk.N, expand=0, fill=tk.Y)
        # 输出结果框
        self.result_box = tk.Text(self.filter_group)
        self.result_box.pack(side=tk.RIGHT, anchor=tk.N, expand=1, fill=tk.BOTH)
        self.result_box.insert(tk.END, "Response will be shown here.")
        self.result_box.config(relief=tk.SUNKEN)

        # 通用参数配置选项
        # 删除模式
        self.delete_mode_var = tk.StringVar()
        self.delete_mode_var.set(self.delete_mode_list[1])
        self.delete_mode_label = ttk.Label(self.param_frame, text="Delete mode:")
        self.delete_mode_label.pack(side=tk.TOP, anchor=tk.W, padx=5)
        self.delete_mode_trash = ttk.Radiobutton(
            self.param_frame, text="Move to recycle bin",
            variable=self.delete_mode_var, value="trash"
        )
        self.delete_mode_trash.pack(side=tk.TOP, anchor=tk.W, padx=5)
        self.delete_mode_extract = ttk.Radiobutton(
            self.param_frame, text="Move to special folder",
            variable=self.delete_mode_var, value="extract"
        )
        self.delete_mode_extract.pack(side=tk.TOP, anchor=tk.W, padx=5)
        # 删除文件夹
        self.delete_dir_var = tk.StringVar()
        self.delete_dir_var.set(self.delete_dir)
        self.delete_dir_label = ttk.Label(self.param_frame, text="Delete directory:")
        self.delete_dir_label.pack(side=tk.TOP, anchor=tk.W, padx=5)
        self.delete_dir_entry = ttk.Entry(self.param_frame, textvariable=self.delete_dir_var)
        self.delete_dir_entry.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5)
        # 分割线
        self.sep = ttk.Separator(self.param_frame, orient=tk.HORIZONTAL)
        # 为各函数的参数配置留空
        self.particular_frame = ttk.Frame(self.param_frame)
        self.particular_frame.pack(side=tk.TOP, anchor=tk.W)

        # 各个功能按钮
        # 1. 计算各文件夹图片数量
        self.count_img_btn = ttk.Button(
            self.func_frame, text="Count images",
            command=self.count_img_in_dir
        )
        self.count_img_btn.pack(side=tk.TOP, anchor=tk.W)
        # 2. 提取图片
        self.extract_img_btn = ttk.Button(
            self.func_frame, text="Extract images >",
            command=self._show_extract_img_param
        )
        self.extract_img_btn.pack(side=tk.TOP, anchor=tk.W)
        # 3. 清理当前文件夹下所有空文件夹
        self.clean_empty_dirs_btn = ttk.Button(
            self.func_frame, text="Clean empty folders",
            command=self.clean_empty_dirs
        )
        self.clean_empty_dirs_btn.pack(side=tk.TOP, anchor=tk.W)
        # 4. 过滤GIF图片
        self.filter_gif_btn = ttk.Button(
            self.func_frame, text="Filter GIF images",
            command=self.filter_gif
        )
        self.filter_gif_btn.pack(side=tk.TOP, anchor=tk.W)

    def _check_dir(self):
        print("Directory:", self.dir_abspath)
        if not os.path.isdir(self.dir_abspath):
            msg = (f"The directory\n{self.dir_abspath}\ndoes not exist!"
                   if self.dir_abspath else "Please input a directory!")
            messagebox.showerror("Error", msg)
            return False
        else:
            return True

    def open_dir(self):
        os.startfile(self.dir_abspath)

    def _add_linefeed_to_str(self, raw_str):
        """根据窗口进行格式化（换行）"""
        line_maxlen = math.floor((math.floor((self.master.winfo_width() * 1.25) - 30) / 9))
        rst_str_with_linefeed = ""
        for i in range(0, len(raw_str), line_maxlen):
            if len(raw_str) - i > line_maxlen:
                rst_str_with_linefeed += f"{raw_str[i:i + line_maxlen]}\n"
            else:
                rst_str_with_linefeed += raw_str[i:]
        return rst_str_with_linefeed

    def _count_files(self, recursive=True):
        """统计当前文件夹下所有文件数、文件类型及各自的数量"""
        if not recursive:
            all_files = os.listdir(self.dir_abspath)
        else:  # 递归获取
            all_files = []
            for root, dirs, files in os.walk(self.dir_abspath):
                for file in files:
                    all_files.append(
                        os.path.relpath(
                            str(os.path.join(root, file)),
                            self.dir_abspath
                        )
                    )
        print(f"Found {len(all_files)} files.")

        # 统计文件类型
        file_types = {}
        for file in all_files:
            file_suffix = os.path.splitext(file)[1]
            if file_suffix in file_types:
                file_types[file_suffix] += 1
            else:
                file_types[file_suffix] = 1
        # 从多到少排序
        file_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)
        # 打印文件类型及数量
        rst_str = ""
        for file_type in file_types:
            file_suffix = " (No suffix)" if not file_type[0] else file_type[0]
            line = f"{file_type[1]} {file_suffix[1:]}; "
            rst_str += line
        rst_str = self._add_linefeed_to_str(rst_str)
        print(rst_str)
        return rst_str, file_types

    def _get_img_stat(self):
        img_types = {}
        for k, v in self.file_stat[1]:
            if k in Conf.IMG_SUFFIX:
                img_types[k] = v
        # 排序
        img_types = sorted(img_types.items(), key=lambda x: x[1], reverse=True)
        # 打印图片类型及数量
        rst_str = ""
        for img_type in img_types:
            line = f"{img_type[1]} {img_type[0][1:]}; "
            rst_str += line
        rst_str = self._add_linefeed_to_str(rst_str)
        print(rst_str)
        return rst_str

    def _collect_img(self):
        """
        收集图片。返回图片列表，包含所有图片的相对于target的路径

        :return: 图片列表, list
        """
        source_dir = self.dir_abspath
        os.chdir(self.dir_abspath)  # 将工作目录切换到源文件夹

        img_list = []
        special_dirs = [self.delete_dir_var.get()]  # 特殊文件夹需跳过
        for root, dirs, files in os.walk(self.dir_abspath):
            # 如果dir_abspath本身即为特殊文件夹，则不能跳过
            if root.split('\\')[-1] in special_dirs and root != source_dir:
                continue
            # 遍历当前文件夹下所有文件
            for file in files:
                if os.path.splitext(file)[1] in Conf.IMG_SUFFIX:
                    img_list.append(
                        os.path.relpath(
                            str(os.path.join(root, file)),
                            self.dir_abspath
                        )
                    )
        return img_list

    def _print_rst(self, msg):
        self.result_box.insert(tk.END, msg + "\n")
        print(msg)

    def count_img_in_dir(self):
        """显示当前文件夹下，所有文件夹中有图片的文件夹的图片数量，按降序排序打印"""
        self.result_box.delete(1.0, tk.END)

        img_num_dict = {}
        for root, dirs, files in os.walk(self.dir_abspath):
            img_num = len([f for f in files if os.path.splitext(f)[1] in Conf.IMG_SUFFIX])
            if img_num:
                img_num_dict[root] = img_num
        img_num_dict = dict(sorted(img_num_dict.items(), key=lambda x: x[1], reverse=True))
        for k, v in img_num_dict.items():
            relative_path = os.path.relpath(k, self.dir_abspath)
            self._print_rst(f"{relative_path}: {v} images.")

    def _clear_particular_frame(self):
        self.particular_frame.destroy()
        self.particular_frame = ttk.Frame(self.param_frame)
        self.particular_frame.pack(side=tk.TOP, anchor=tk.W)

    @staticmethod
    def input_dir(entry):
        dir_path = filedialog.askdirectory()
        if dir_path:
            entry.delete(0, tk.END)
            entry.insert(0, dir_path)
        entry.focus()

    def extract_img(self, dest_abspath=None, source_abspath=None):
        """将原目录下的所有图片移动到目的目录"""
        # 默认原目录和目的目录均为当前目录
        if source_abspath is None:
            source_abspath = self.dir_abspath
        if dest_abspath is None:
            dest_abspath = self.dir_abspath
        if not os.path.isdir(dest_abspath) or not os.path.isdir(source_abspath):
            raise ValueError("Invalid source or destination directory.")
        self.result_box.delete(1.0, tk.END)
        self._print_rst(f"Moving images from {source_abspath} to {dest_abspath}...")

        img_list = self._collect_img()
        for img in img_list:
            img_name = img.split('\\')[-1]
            source = os.path.join(source_abspath, img)
            dest = os.path.join(dest_abspath, img_name)
            shutil.move(source, dest)
            self._print_rst(f"Moved {img_name} to {dest}.")

    def _show_extract_img_param(self):
        """显示提取图片功能的参数配置"""
        self._clear_particular_frame()
        # 源文件夹
        self.src_dir_label = ttk.Label(self.particular_frame, text="Source directory:")
        self.src_dir_entry = ttk.Entry(self.particular_frame)
        self.open_src_dir_btn = ttk.Button(
            self.particular_frame, text="Select folder", width=20,
            command=lambda: self.input_dir(self.src_dir_entry)
        )
        self.src_dir_label.pack(side=tk.TOP, anchor=tk.W, padx=5)
        self.open_src_dir_btn.pack(side=tk.TOP, anchor=tk.W, padx=5)
        self.src_dir_entry.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5)
        self.src_dir_entry.insert(0, self.dir_abspath)
        # 目的文件夹
        self.dest_dir_label = ttk.Label(self.particular_frame, text="Destination directory:")
        self.dest_dir_entry = ttk.Entry(self.particular_frame)
        self.open_dest_dir_btn = ttk.Button(
            self.particular_frame, text="Select folder", width=20,
            command=lambda: self.input_dir(self.dest_dir_entry)
        )
        self.dest_dir_label.pack(side=tk.TOP, anchor=tk.W, padx=5)
        self.open_dest_dir_btn.pack(side=tk.TOP, anchor=tk.W, padx=5)
        self.dest_dir_entry.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5)
        self.dest_dir_entry.insert(0, self.dir_abspath)
        # 提取图片按钮
        self.extract_img_btn = ttk.Button(
            self.particular_frame, text="Extract images",
            command=lambda: self.extract_img(
                self.dest_dir_entry.get(), self.src_dir_entry.get()
            )
        )
        self.extract_img_btn.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5)

    def clean_empty_dirs(self):
        """清理空文件夹"""
        self.result_box.delete(1.0, tk.END)
        # 注明：这个函数只会清理最底层的空文件夹，无法递归清理在清理完后为空的文件夹
        self._print_rst("Notice: This function only cleans the bottom-level "
                        "empty folders. You may have to run it for several "
                        "times to clean all empty folders.")
        if not os.path.exists(self.dir_abspath):
            self._print_rst(f"Directory not found: {self.dir_abspath}")
            return
        empty_dir_list = []
        for root, dirs, files in os.walk(self.dir_abspath, topdown=False):
            if not dirs and not files:
                self._print_rst(f"{root} is an empty directory.")
                empty_dir_list.append(root)
        send2trash(empty_dir_list)
        self._print_rst(f"Removed {len(empty_dir_list)} empty directories.")

    def remove2trash(self, file_list):
        """将输入的文件列表中的所有文件移动到回收站"""
        send2trash(file_list)
        self._print_rst(f"The following files have been moved to the recycle bin.")
        for file in file_list:
            self._print_rst(file)

    def remove2newdir(self, file_list, delete_dir="$$DELETE"):
        """将输入的文件列表中的所有文件移动到指定的特殊文件夹"""
        # 检查并创建指定文件夹
        if not os.path.exists(delete_dir) and len(file_list) > 0:
            os.makedirs(delete_dir)
        # 移动到指定文件夹
        for file in file_list:
            # 检查文件是否存在
            if not os.path.exists(file):
                raise FileNotFoundError(errno.ENOENT, f"File not found: {file}")
            file_fullname = os.path.basename(file)
            shutil.move(file, os.path.join(delete_dir, file_fullname))
            self._print_rst(f"File {file} moved to {delete_dir}.")

    def remove2newdir_in_batches(self, file_sets, delete_dir="$$DELETE"):
        """将文件移动到新文件夹，分批次移动文件，为每个批次创建一个文件夹"""
        # 检查并创建指定文件夹
        if not os.path.exists(delete_dir) and len(file_sets) > 0:
            os.makedirs(delete_dir)

        # 为每个文件夹生成不同的名称，形如aa,ab,ac...az,ba,bb...
        char = string.ascii_lowercase
        power = math.ceil(math.log(len(file_sets), len(char)))
        name_iter = itertools.product(char, repeat=power)
        # 生成一个时间戳字符串作为每个文件夹名的前缀，防止重名
        stamp_num = int(strftime("%Y%m%d%H%M%S", localtime())[2:])
        # 对stamp_num进行base62，以缩小文件名长度
        charset = string.digits + string.ascii_letters
        prefix = ""
        while stamp_num:
            stamp_num, remainder = divmod(stamp_num, 62)
            prefix += charset[remainder]
        print(prefix)

        # 使用生成器生成文件夹名，创建并移动文件
        dirname_iter = (''.join(chars) for chars in name_iter)
        for file_set in file_sets:
            dirname = prefix + "_" + next(dirname_iter)
            new_path = os.path.join(delete_dir, dirname)
            if not os.path.exists(new_path):
                os.makedirs(new_path)
            for file in file_set:
                try:
                    shutil.move(file, os.path.join(new_path))
                    self._print_rst(f"Move {file} to {new_path}.")
                except FileNotFoundError:
                    self._print_rst(f"{file} not found.")

    def delete(self, file_list):
        # 若file_list仅为一条字符串，则将file_list转换为列表
        if isinstance(file_list, str):
            file_list = [file_list]
        # 若file_list为空则返回
        if len(file_list) == 0:
            self._print_rst("No file to delete.")
            return file_list

        # file_list为list[set[str]]或list[str]时，有各自的删除方式
        is_setlist = isinstance(file_list[0], set)
        if is_setlist:
            self.remove2newdir_in_batches(file_list, self.delete_dir_var.get())
        else:
            if self.delete_mode_var.get() == "trash":
                self.remove2trash(file_list)
            elif self.delete_mode_var.get() == "extract":
                self.remove2newdir(file_list, self.delete_dir_var.get())
        return file_list

    def filter_gif(self):
        """读取所有图片的前3个字节（GIF89...），判断是否为gif"""
        self.result_box.delete(1.0, tk.END)
        img_list = self._collect_img()
        gif_imgs = []
        for img_relpath in img_list:
            with open(img_relpath, 'rb') as f:
                if f.read(3) == b'GIF':
                    self._print_rst(f"File {img_relpath} is gif.")
                    gif_imgs.append(img_relpath)
        self.delete(gif_imgs)
