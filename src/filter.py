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
from tkinter import ttk, messagebox

from send2trash import send2trash

from src.config import Conf


class FilterConfig:
    delete_mode_list = ["trash", "extract"]  # 移动到回收站、移动到文件夹下的特殊文件夹
    delete_mode = delete_mode_list[1]
    delete_dir = "$$DELETE"  # 源文件夹下用于存储被删除文件的文件夹名称

    def __str__(self):
        return (f"All delete modes: {self.delete_mode_list}\n"
                f"Current delete mode: {self.delete_mode}\n"
                f"Delete directory: {self.delete_dir}")


class Filter:
    def __init__(self, master, dir_abspath, logger=None):
        self.master = master
        self.dir_abspath = dir_abspath
        self.safety = self.check_dir()  # 检查目录是否存在
        if not self.safety:
            self.master.destroy()
            return

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
        self.file_stat = self.count_files()
        self.stat_group = ttk.LabelFrame(
            master,
            text="Statistics of files in current folder (close and open again to refresh)"
        )
        self.stat_group.pack(anchor=tk.N, padx=5, pady=5, expand=1, fill=tk.X)
        self.firstline_frame = ttk.Frame(self.stat_group)
        self.firstline_frame.pack(anchor=tk.W, fill=tk.X, expand=1)
        # 所有文件统计信息标签
        self.count_files_label = ttk.Label(
            self.firstline_frame, text="All files statistics:"
        )
        self.count_files_label.pack(side=tk.LEFT, padx=5, pady=5,)
        # 打开文件夹
        self.open_dir_button = ttk.Button(
            self.firstline_frame, text="Open the folder",
            command=self.open_dir, width=20
        )
        self.open_dir_button.pack(side=tk.RIGHT, padx=5, pady=5)
        # 所有文件统计信息文本框
        self.count_files_rst = tk.Text(self.stat_group, height=4)
        self.count_files_rst.pack(padx=5, pady=5, expand=1, fill=tk.X)
        self.count_files_rst.insert(tk.END, self.file_stat[0])
        self.count_files_rst.config(state=tk.DISABLED, wrap=tk.NONE, relief=tk.FLAT)
        # 图片统计信息标签
        self.count_imgs_label = ttk.Label(
            self.stat_group, text="Image files statistics:"
        )
        self.count_imgs_label.pack(padx=5, pady=5, anchor=tk.W)
        # 图片统计信息文本框
        self.count_imgs_rst = tk.Text(self.stat_group, height=1)
        self.count_imgs_rst.pack(padx=5, pady=5, expand=1, fill=tk.X)
        self.count_imgs_rst.insert(tk.END, self.get_img_stat())
        self.count_imgs_rst.config(state=tk.DISABLED, wrap=tk.NONE, relief=tk.FLAT)

        # 附注，注明接下来下面给出的所有功能，所筛选的图片都不包括/delete_dir中的图片
        self.note_label = ttk.Label(
            master,
            text=("p.s. All the functions above are based"
                  " on the images in the source folder, "
                  "excluding those in the delete folder.")
        )
        self.note_label.pack(padx=5, pady=5, anchor=tk.CENTER)

        # 获取所有支持的图片的路径
        self.all_img_list = self.collect_img()

    def check_dir(self):
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

    def add_linefeed_to_str(self, raw_str):
        """根据窗口进行格式化（换行）"""
        line_maxlen = math.floor((math.floor((self.master.winfo_width() * 1.25) - 30) / 9))
        rst_str_with_linefeed = ""
        for i in range(0, len(raw_str), line_maxlen):
            if len(raw_str) - i > line_maxlen:
                rst_str_with_linefeed += f"{raw_str[i:i + line_maxlen]}\n"
            else:
                rst_str_with_linefeed += raw_str[i:]
        return rst_str_with_linefeed

    def count_files(self, recursive=True):
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
        rst_str = self.add_linefeed_to_str(rst_str)
        print(rst_str)
        return rst_str, file_types

    def get_img_stat(self):
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
        rst_str = self.add_linefeed_to_str(rst_str)
        print(rst_str)
        return rst_str

    def collect_img(self):
        """
        收集图片。返回图片列表，包含所有图片的相对于target的路径

        :return: 图片列表, list
        """
        source_dir = self.dir_abspath
        os.chdir(self.dir_abspath)  # 将工作目录切换到源文件夹

        img_list = []
        special_dirs = [self.dir_conf.delete_dir]  # 特殊文件夹需跳过
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

    @staticmethod
    def remove2trash(file_list):
        """将输入的文件列表中的所有文件移动到回收站"""
        send2trash(file_list)
        print(f"The following files have been moved to the recycle bin.")
        for file in file_list:
            print(file)

    @staticmethod
    def remove2newdir(file_list, delete_dir="$$DELETE"):
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
            print(f"File {file} moved to {delete_dir}.")

    @staticmethod
    def remove2newdir_in_batches(file_sets, delete_dir="$$DELETE"):
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
                    print(f"Move {file} to {new_path}.")
                except FileNotFoundError:
                    print(f"{file} not found.")
