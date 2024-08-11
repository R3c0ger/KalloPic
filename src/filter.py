#!/usr/bin/env python
# -*- coding: utf-8 -*-

import errno
import functools
import itertools
import math
import os
import shutil
import string
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool
from time import strftime, localtime
from tkinter import ttk, messagebox, filedialog

from PIL import Image
from send2trash import send2trash

from src.config import Conf
from src.theme import apply_text_theme
from src.utils.calc_file_size import calc_file_size
from src.utils.logger import Logger
from src.utils.path_set_list import merge_intersecting_sets
from src.utils.saturation import img2sat_ratio
from src.utils.sim_metrics import (
    HashFunc, img2hash, calc_hash_hammingdist,
    img2normvec, calc_cosine_similarity,
    img2numpy, mse
)


class Filter:
    def __init__(self, master, dir_abspath):
        self.master = master
        self.dir_abspath = dir_abspath.replace("/", "\\")
        self.safety = self._check_dir()  # 检查目录是否存在
        if not self.safety:
            self.master.destroy()
            return
        # 默认值
        self.delete_dir = "$$DELETE"  # 默认的删除图片所存放的文件夹
        self.delete_mode_list = ["trash", "extract"]  # 两种删除模式
        self.min_size_kb = 80.0  # 图片大小阈值，单位KB
        self.min_size_pixel = 800  # 图片分辨率阈值，单位像素
        self.max_height = 3000  # 图片最大高度
        self.max_res_ratio = 2.0  # 图片最大分辨率比例
        self.keep_largest = False  # 是否保留最大的图片
        self.multitask_method = "thread"  # 多任务处理方法，串行、多线程、多进程
        self.runner_num = 8  # 多任务处理的线程/进程数
        self.mean_refine = True  # 是否计算直方图均值来细化过滤
        self.max_sat_ratio_hist = 0.2850  # 饱和度比例系数的阈值（直方图）
        self.max_sat_ratio_mean = 0.0650  # 饱和度比例系数的阈值（均值）
        self.sat_threshold = 10  # 饱和度直方图中的最高饱和度阈值
        self.max_hash_dist = 3  # 哈希距离阈值
        self.hash_func = "ahash"  # 使用哈希比较图片时选用的哈希函数
        self.hash_size = 8  # 使用哈希比较图片时的哈希大小
        self.min_cos_dist = 0.996  # 余弦相似度阈值
        self.max_mse = 48.0  # 均方误差阈值

        # 初始化窗口
        self.title = "Filter"
        self.master.title(f"{self.title} - {self.dir_abspath}")
        self.master.geometry("1000x725")
        self.master.resizable(False, False)

        # 统计信息
        self.file_stat = self._count_files()
        self.stat_group = ttk.LabelFrame(
            master,
            text=" File statistics of current folder (close and open again to refresh) "
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
            command=lambda: os.startfile(self.dir_abspath), width=20
        )
        self.open_dir_button.pack(side=tk.RIGHT, padx=5)
        # 所有文件统计信息文本框
        self.count_files_rst = tk.Text(self.stat_group, height=3)
        self.count_files_rst.pack(padx=5, pady=5, expand=1, fill=tk.X)
        self.count_files_rst.insert(tk.END, self.file_stat[0])
        self.count_files_rst.config(state=tk.DISABLED, relief=tk.FLAT)
        apply_text_theme(self.count_files_rst, editable=False)
        # 图片统计信息标签
        self.count_imgs_label = ttk.Label(self.stat_group, text="Image files statistics:")
        self.count_imgs_label.pack(padx=5, anchor=tk.W)
        # 图片统计信息文本框
        self.count_imgs_rst = tk.Text(self.stat_group, height=1)
        self.count_imgs_rst.pack(padx=5, pady=5, expand=1, fill=tk.X)
        self.count_imgs_rst.insert(tk.END, self._get_img_stat())
        self.count_imgs_rst.config(state=tk.DISABLED, relief=tk.FLAT)
        apply_text_theme(self.count_imgs_rst, editable=False)

        # 过滤功能组件，三栏，最左边一栏为功能按钮，中间一栏为功能参数配置，最右边一栏为输出结果文本框
        self.filter_group = ttk.LabelFrame(master, text=" Filter functions ")
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
        self.result_box.pack(side=tk.LEFT, anchor=tk.N, expand=1, fill=tk.BOTH)
        self.result_box.insert(tk.END, "Response will be shown here.")
        self.result_box.config(relief=tk.SUNKEN)
        apply_text_theme(self.result_box)
        # 输出结果框的滚动条
        self.scrollbar = ttk.Scrollbar(self.filter_group, command=self.result_box.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_box.config(yscrollcommand=self.scrollbar.set)

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
        self.sep.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        # 为各函数的参数配置留空
        self.particular_frame = ttk.Frame(self.param_frame)
        self.particular_frame.pack(side=tk.TOP, anchor=tk.W)

        # 各个功能按钮
        # 1. 计算各文件夹图片数量
        self.count_img_btn = ttk.Button(
            self.func_frame, text="Count images",
            command=self.count_img_in_dir
        )
        self.count_img_btn.pack(side=tk.TOP, padx=5, pady=1)
        # 2. 提取图片
        self.extract_img_btn = ttk.Button(
            self.func_frame, text="Extract images >",
            command=self._show_extract_img_param
        )
        self.extract_img_btn.pack(side=tk.TOP, padx=5, pady=1)
        # 3. 清理当前文件夹下所有空文件夹
        self.clean_empty_dirs_btn = ttk.Button(
            self.func_frame, text="Clean empty folders",
            command=self.clean_empty_dirs
        )
        self.clean_empty_dirs_btn.pack(side=tk.TOP, padx=5, pady=1)
        # 4. 过滤GIF图片
        self.filter_gif_btn = ttk.Button(
            self.func_frame, text="Filter GIF images",
            command=self.filter_gif
        )
        self.filter_gif_btn.pack(side=tk.TOP, padx=5, pady=1)
        # 5. 删除文件大小较小图片
        self.filter_small_imgs_btn = ttk.Button(
            self.func_frame, text="Filter small images >",
            command=self._show_filter_small_imgs_param
        )
        self.filter_small_imgs_btn.pack(side=tk.TOP, padx=5, pady=1)
        # 6. 删除分辨率较小图片
        self.filter_low_size_imgs_btn = ttk.Button(
            self.func_frame, text="Filter low size images >",
            command=self._show_filter_low_size_imgs_param
        )
        self.filter_low_size_imgs_btn.pack(side=tk.TOP, padx=5, pady=1)
        # 7. 删除过高图片
        self.filter_high_imgs_btn = ttk.Button(
            self.func_frame, text="Filter high images >",
            command=self._show_filter_high_imgs_param
        )
        self.filter_high_imgs_btn.pack(side=tk.TOP, padx=5, pady=1)
        # 8. 删除长图
        self.filter_long_imgs_btn = ttk.Button(
            self.func_frame, text="Filter long images >",
            command=self._show_filter_long_imgs_param
        )
        self.filter_long_imgs_btn.pack(side=tk.TOP, padx=5, pady=1)
        # 9. 删除文件名相同的图片
        self.filter_samename_btn = ttk.Button(
            self.func_frame, text="Filter same name images >",
            command=self._show_filter_samename_param
        )
        self.filter_samename_btn.pack(side=tk.TOP, padx=5, pady=1)
        # 10. 删除低饱和度图片
        self.filter_low_saturation_btn = ttk.Button(
            self.func_frame, text="Filter low saturation images >",
            command=self._show_filter_low_saturation_param
        )
        self.filter_low_saturation_btn.pack(side=tk.TOP, padx=5, pady=1)
        # 11. 删除相似图片（哈希）
        self.filter_similar_imgs_hash_btn = ttk.Button(
            self.func_frame, text="Filter similar images (Hash) >",
            command=self._show_filter_similar_imgs_hash_param
        )
        self.filter_similar_imgs_hash_btn.pack(side=tk.TOP, padx=5, pady=1)
        # 12. 删除相似图片（余弦相似度）
        self.filter_similar_imgs_cos_btn = ttk.Button(
            self.func_frame, text="Filter similar images (Cosine) >",
            command=self._show_filter_similar_imgs_cos_param
        )
        self.filter_similar_imgs_cos_btn.pack(side=tk.TOP, padx=5, pady=1)
        # 13. 删除相似图片（均方误差）
        self.filter_similar_imgs_mse_btn = ttk.Button(
            self.func_frame, text="Filter similar images (MSE) >",
            command=self._show_filter_similar_imgs_mse_param
        )
        self.filter_similar_imgs_mse_btn.pack(side=tk.TOP, padx=5, pady=1)
        # 设置所有的功能按钮的宽度一致，文字左对齐
        child: ttk.Button
        for child in self.func_frame.winfo_children():
            child.config(width=28, style='LeftAligned.TButton')

    def _check_dir(self):
        Logger.debug("Directory: " + self.dir_abspath)
        if not os.path.isdir(self.dir_abspath):
            msg = (f"The directory\n{self.dir_abspath}\ndoes not exist!"
                   if self.dir_abspath else "Please input a directory!")
            messagebox.showerror("Error", msg)
            return False
        else:
            return True

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
        Logger.debug(f"Found {len(all_files)} files.")

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
        Logger.debug(rst_str)
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
        Logger.debug(rst_str)
        return rst_str

    def _collect_img(self, source_dir=None):
        """
        收集图片。返回图片列表，包含所有图片的相对于target的路径

        :return: 图片列表, list
        """
        source_dir = self.dir_abspath if not source_dir else source_dir
        os.chdir(source_dir)  # 将工作目录切换到源文件夹

        img_list = []
        special_dirs = [self.delete_dir_var.get()]  # 特殊文件夹需跳过
        for root, dirs, files in os.walk(source_dir):
            # 如果dir_abspath本身即为特殊文件夹，则不能跳过
            if root.split('\\')[-1] in special_dirs and root != source_dir:
                continue
            # 遍历当前文件夹下所有文件
            for file in files:
                if os.path.splitext(file)[1] in Conf.IMG_SUFFIX:
                    img_list.append(
                        os.path.relpath(
                            str(os.path.join(root, file)), source_dir
                        )
                    )
        return img_list

    def _print_rst(self, msg):
        self.result_box.insert(tk.END, msg + "\n")
        Logger.debug(msg)

    def _start_fn(self, collect_img=True):
        self.result_box.delete(1.0, tk.END)
        if collect_img:
            img_list = self._collect_img()
            return img_list

    def count_img_in_dir(self):
        """显示当前文件夹下，所有文件夹中有图片的文件夹的图片数量，按降序排序打印"""
        self._start_fn(collect_img=False)

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
            entry.insert(0, dir_path.replace("/", "\\"))
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
        img_list = self._collect_img(source_abspath)
        self._print_rst(f"Moving images from {source_abspath} to {dest_abspath}...")
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
            self.particular_frame, text="Select folder",
            command=lambda: self.input_dir(self.src_dir_entry)
        )
        self.src_dir_label.pack(side=tk.TOP, anchor=tk.W, padx=5)
        self.open_src_dir_btn.pack(side=tk.TOP, anchor=tk.W, padx=5, fill=tk.X)
        self.src_dir_entry.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5)
        self.src_dir_entry.insert(0, self.dir_abspath)
        # 目的文件夹
        self.dest_dir_label = ttk.Label(self.particular_frame, text="Destination directory:")
        self.dest_dir_entry = ttk.Entry(self.particular_frame)
        self.open_dest_dir_btn = ttk.Button(
            self.particular_frame, text="Select folder",
            command=lambda: self.input_dir(self.dest_dir_entry)
        )
        self.dest_dir_label.pack(side=tk.TOP, anchor=tk.W, padx=5)
        self.open_dest_dir_btn.pack(side=tk.TOP, anchor=tk.W, padx=5, fill=tk.X)
        self.dest_dir_entry.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5)
        self.dest_dir_entry.insert(0, self.dir_abspath)
        # 提取图片按钮
        self.start_btn = ttk.Button(
            self.particular_frame, text="Start Extracting",
            command=lambda: self.extract_img(
                self.dest_dir_entry.get(), self.src_dir_entry.get()
            )
        )
        self.start_btn.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5, fill=tk.X)

    def clean_empty_dirs(self):
        """清理空文件夹"""
        self._start_fn(collect_img=False)
        # 注明：这个函数只会清理最底层的空文件夹，无法递归清理在清理完后为空的文件夹
        self._print_rst("Notice: This function only cleans the bottom-level "
                        "empty folders. You may have to run it for several "
                        "times to clean all empty folders.")
        if not os.path.exists(self.dir_abspath):
            self._print_rst(f"Directory not found: {self.dir_abspath}")
            return
        empty_dir_list = []
        for root, dirs, files in os.walk(self.dir_abspath, topdown=False):
            if root == self.dir_abspath:  # 源文件夹本身不应被清理
                continue
            if not dirs and not files:
                self._print_rst(f"{root} is an empty directory.")
                empty_dir_list.append(root)
        try:
            send2trash(empty_dir_list)
        except Exception as e:
            self._print_rst(str(e))
        self._print_rst(f"Removed {len(empty_dir_list)} empty directories.")

    def remove2trash(self, file_list):
        """将输入的文件列表中的所有文件移动到回收站"""
        try:
            send2trash(file_list)
        except Exception as e:
            self._print_rst(str(e))
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
            try:
                shutil.move(file, os.path.join(delete_dir, file_fullname))
            except Exception as e:
                self._print_rst(str(e))
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
        img_list = self._start_fn()
        gif_imgs = []
        for img_relpath in img_list:
            with open(img_relpath, 'rb') as f:
                if f.read(3) == b'GIF':
                    self._print_rst(f"File {img_relpath} is gif.")
                    gif_imgs.append(img_relpath)
        self.delete(gif_imgs)

    def filter_small_imgs(self, min_size_kb: float = None):
        """删除小于指定大小的所有图片。应优先执行，以删掉无法打开的图片"""
        img_list = self._start_fn()
        small_imgs = []
        for img_relpath in img_list:
            img_size = os.path.getsize(img_relpath) / 1024
            if img_size < min_size_kb:
                self._print_rst(f"{img_relpath} is too small ({img_size:.2f} KB).")
                small_imgs.append(img_relpath)
        self.delete(small_imgs)
        return small_imgs

    def _show_filter_small_imgs_param(self):
        """显示过滤小图片的参数配置"""
        self._clear_particular_frame()
        # 最小文件大小
        self.min_size_label = ttk.Label(self.particular_frame, text="Minimum size(KB):")
        self.min_size_spinbox = ttk.Spinbox(
            self.particular_frame,
            from_=0, to=1000000000, increment=1, width=18
        )
        self.min_size_label.pack(side=tk.TOP, anchor=tk.W, padx=5)
        self.min_size_spinbox.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5, fill=tk.X)
        self.min_size_spinbox.insert(0, str(self.min_size_kb))
        # 过滤小图片按钮
        self.start_btn = ttk.Button(
            self.particular_frame, text="Start Filter",
            command=lambda: self.filter_small_imgs(float(self.min_size_spinbox.get()))
        )
        self.start_btn.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5, fill=tk.X)

    def filter_low_size_imgs(self, min_size_pixel: int = None):
        """删除垂直和水平分辨率均低于预设值的图片"""
        img_list = self._start_fn()
        low_size_imgs = []
        for img_relpath in img_list:
            img = Image.open(img_relpath)
            img_size = img.size
            if img_size[0] < min_size_pixel and img_size[1] < min_size_pixel:
                self._print_rst(f"Size of {img_relpath}: {img_size}\tLow size image.")
                low_size_imgs.append(img_relpath)
        self.delete(low_size_imgs)
        return low_size_imgs

    def _show_filter_low_size_imgs_param(self):
        """显示过滤低分辨率图片的参数配置"""
        self._clear_particular_frame()
        # 最小分辨率
        self.min_size_label = ttk.Label(self.particular_frame, text="Minimum size(pixel):")
        self.min_size_spinbox = ttk.Spinbox(
            self.particular_frame,
            from_=0, to=10000, increment=1, width=18
        )
        self.min_size_label.pack(side=tk.TOP, anchor=tk.W, padx=5)
        self.min_size_spinbox.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5, fill=tk.X)
        self.min_size_spinbox.insert(0, str(self.min_size_pixel))
        # 过滤低分辨率图片按钮
        self.start_btn = ttk.Button(
            self.particular_frame, text="Start Filter",
            command=lambda: self.filter_low_size_imgs(int(self.min_size_spinbox.get()))
        )
        self.start_btn.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5, fill=tk.X)

    def filter_high_imgs(self, max_height: int = None):
        """删除图片高度超过预设值的图片"""
        img_list = self._start_fn()
        high_imgs = []  # 高度超过预设值的图片列表
        for img_relpath in img_list:
            img = Image.open(img_relpath)
            img_height = img.size[1]
            if img_height > max_height:
                self._print_rst(f"Height of {img_relpath}: {img_height}\tHigh image.")
                high_imgs.append(img_relpath)
        self.delete(high_imgs)
        return high_imgs

    def _show_filter_high_imgs_param(self):
        """显示过滤高图片的参数配置"""
        self._clear_particular_frame()
        # 最大高度
        self.max_height_label = ttk.Label(self.particular_frame, text="Maximum height(pixel):")
        self.max_height_spinbox = ttk.Spinbox(
            self.particular_frame,
            from_=0, to=10000, increment=1, width=18
        )
        self.max_height_label.pack(side=tk.TOP, anchor=tk.W, padx=5)
        self.max_height_spinbox.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5, fill=tk.X)
        self.max_height_spinbox.insert(0, str(self.max_height))
        # 过滤高图片按钮
        self.start_btn = ttk.Button(
            self.particular_frame, text="Start Filter",
            command=lambda: self.filter_high_imgs(int(self.max_height_spinbox.get()))
        )
        self.start_btn.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5, fill=tk.X)

    def filter_long_imgs(self, max_res_ratio: float = None):
        """删除长图，即长宽比超过预设值的图片"""
        img_list = self._start_fn()
        long_imgs = []
        for img_relpath in img_list:
            img = Image.open(img_relpath)
            img_width, img_height = img.size
            ratio_h2w = img_height / img_width
            if ratio_h2w >= max_res_ratio:
                self._print_rst(f"Ratio(h/w) of {img_relpath}: "
                                f"{ratio_h2w:.9f}\tLong image.")
                long_imgs.append(img_relpath)
                continue
            ratio_w2h = img_width / img_height
            if ratio_w2h >= max_res_ratio:
                self._print_rst(f"Ratio(w/h) of {img_relpath}: "
                                f"{ratio_w2h:.9f}\tLong image.")
                long_imgs.append(img_relpath)
        self.delete(long_imgs)
        return long_imgs

    def _show_filter_long_imgs_param(self):
        """显示过滤长图的参数配置"""
        self._clear_particular_frame()
        # 最大分辨率比例
        self.max_res_ratio_label = ttk.Label(self.particular_frame, text="Maximum ratio:")
        self.max_res_ratio_spinbox = ttk.Spinbox(
            self.particular_frame,
            from_=0, to=100, increment=0.1, width=18
        )
        self.max_res_ratio_label.pack(side=tk.TOP, anchor=tk.W, padx=5)
        self.max_res_ratio_spinbox.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5, fill=tk.X)
        self.max_res_ratio_spinbox.insert(0, str(self.max_res_ratio))
        # 过滤长图按钮
        self.start_btn = ttk.Button(
            self.particular_frame, text="Start Filter",
            command=lambda: self.filter_long_imgs(float(self.max_res_ratio_spinbox.get()))
        )
        self.start_btn.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5, fill=tk.X)

    def filter_samename(self, keep_largest: bool = None):
        """删去无扩展名时文件名重复或者文件名之间相差"_tmb"的图片"""
        img_list = self._start_fn()  # 临时的图片列表
        similar_lists_2d = []  # 二维列表，每个元素为一组文件名相似的图片
        similar_group_num = 0  # 文件名相似的图片组数

        # 找出无扩展名时文件名重复或“部分”重复的图片
        for img_i in img_list:
            img_i_name = os.path.splitext(os.path.basename(img_i))[0]
            img_similar_list = [img_i]  # 与img_i文件名相似的图片列表
            # 存在文件名和其他某个文件相同，但扩展名前多了"_tmb"的图片
            if "_tmb" in img_i_name:
                img_i_name = img_i_name.replace("_tmb", "")
            # 如果有多个图片，其文件名大幅度重合，则说明这些图片是重复的
            for img_j in img_list:
                if img_i_name in img_j and img_i != img_j:
                    img_similar_list.append(img_j)

            # 如果文件名相似图片组中有多于1张图片，则说明对当前img_i有重复图片
            if len(img_similar_list) > 1:
                similar_group_num += 1
                self._print_rst(f"Group {similar_group_num}: "
                                f"{len(img_similar_list)} similar images:")
                for img in img_similar_list:
                    tab = (2 - ('_tmb' in img)) * "\t"
                    img_size = calc_file_size(img)
                    self._print_rst(f"\t{img}{tab}{img_size}")
                    # 将图片所在位置的字符串改成不可能出现在文件名中的字符
                    img_list[img_list.index(img)] = "*"

                # 如果keep_largest为真，则仅保留一张文件大小最大的图片
                if keep_largest:
                    img_similar_list.remove(
                        max(img_similar_list, key=os.path.getsize)
                    )
                similar_lists_2d.append(img_similar_list)

        # 展平二维列表，得到所有文件名相似图片的列表
        similar_list = list(itertools.chain(*similar_lists_2d))
        self._print_rst(f"\nTotal {len(similar_list)} similar images.\n")
        self.delete(similar_list)
        return similar_list

    def _show_filter_samename_param(self):
        """显示过滤重名图片的参数配置"""
        self._clear_particular_frame()
        # 保留最大文件
        self.keep_largest_var = tk.BooleanVar()
        self.keep_largest_var.set(self.keep_largest)
        self.keep_largest_checkbtn = ttk.Checkbutton(
            self.particular_frame, text="Keep the largest file",
            variable=self.keep_largest_var
        )
        self.keep_largest_checkbtn.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5)
        # 过滤重名图片按钮
        self.start_btn = ttk.Button(
            self.particular_frame, text="Start Filter",
            command=lambda: self.filter_samename(self.keep_largest_var.get())
        )
        self.start_btn.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5, fill=tk.X)

    def _multitask_gen_imgdict(
        self,
        func: callable,
        img_list: list[str],
        multitask_method: str = "serial",
        runner_num: int = 8,
    ) -> dict[str, tuple[list, float]]:
        img_dict = {}
        if multitask_method == "serial":
            self._print_rst(f"Calculating serially...")
            for img_path in img_list:
                img_dict[img_path] = func(img_path)
        elif multitask_method == "thread":
            self._print_rst(f"Calculating while using threading...")
            with ThreadPoolExecutor(max_workers=runner_num) as executor:
                img_zip = zip(img_list, executor.map(func, img_list))
                img_dict = dict(img_zip)
        elif multitask_method == "multiprocess":
            self._print_rst(f"Calculating while using multiprocessing...")
            with Pool(processes=runner_num) as pool:
                img_zip = zip(img_list, pool.map(func, img_list))
                img_dict = dict(img_zip)
        return img_dict

    def _show_multitask_config(self):
        """显示多任务配置组件"""
        # 多任务
        self.multitask_method_label = ttk.Label(self.particular_frame, text="Multitask method:")
        self.multitask_method_combobox = ttk.Combobox(
            self.particular_frame, values=["serial", "thread", "multiprocess"], width=15
        )
        self.multitask_method_label.pack(side=tk.TOP, anchor=tk.W, padx=5)
        self.multitask_method_combobox.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5, fill=tk.X)
        self.multitask_method_combobox.set(self.multitask_method)
        # 运行线程数
        self.runner_num_label = ttk.Label(self.particular_frame, text="Runner number:")
        self.runner_num_spinbox = ttk.Spinbox(
            self.particular_frame,
            from_=1, to=16, increment=1, width=18
        )
        self.runner_num_label.pack(side=tk.TOP, anchor=tk.W, padx=5)
        self.runner_num_spinbox.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5, fill=tk.X)
        self.runner_num_spinbox.insert(0, str(self.runner_num))

    def filter_low_saturation(
        self,
        mean_refine: bool = None,
        max_sat_ratio_hist: float = None,
        max_sat_ratio_mean: float = None,
        sat_threshold: float = None,
        multitask_method: str = None,
        runner_num: int = None,
    ) -> list[str]:
        """删除黑白图片"""
        img_list = self._start_fn()  # 临时的图片列表
        low_saturation_imgs = []  # 低饱和度图片列表

        calc_func = functools.partial(img2sat_ratio, _sat_threshold=sat_threshold)
        img_dict: dict[str, tuple] = self._multitask_gen_imgdict(
            calc_func, img_list, multitask_method, runner_num,
        )

        for img_relpath, (hist_ratio, mean_ratio) in img_dict.items():
            # 如果hist_ratio为-1，则说明图片是L或LA模式的黑白图片
            if hist_ratio == -1 and mean_ratio == -1:
                self._print_rst(f"File {img_relpath} is a black and "
                                f"white image which is L or LA mode.")
                low_saturation_imgs.append(img_relpath)
                continue
            # 如果hist_ratio小于max_sat_ratio_hist，则说明图片是低饱和度图片
            if hist_ratio < max_sat_ratio_hist:
                # 如果mean_refine为真，则再用均值法判断是否为低饱和度图片
                if mean_refine and mean_ratio > max_sat_ratio_mean:
                    continue
                self._print_rst(f"Saturation ratio of {img_relpath}: "
                                f"{hist_ratio[0]:.9f}\tLow saturation image.")
                low_saturation_imgs.append(img_relpath)

        self._print_rst(f"\nTotal {len(low_saturation_imgs)} low saturation images.")
        self.delete(low_saturation_imgs)
        return low_saturation_imgs

    def _show_filter_low_saturation_param(self):
        """显示过滤低饱和度图片的参数配置"""
        self._clear_particular_frame()
        # 直方图饱和度比例
        self.max_sat_ratio_hist_label = ttk.Label(self.particular_frame, text="Maximum hist ratio:")
        self.max_sat_ratio_hist_spinbox = ttk.Spinbox(
            self.particular_frame,
            from_=0, to=1, increment=0.01, width=18
        )
        self.max_sat_ratio_hist_label.pack(side=tk.TOP, anchor=tk.W, padx=5)
        self.max_sat_ratio_hist_spinbox.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5, fill=tk.X)
        self.max_sat_ratio_hist_spinbox.insert(0, str(self.max_sat_ratio_hist))
        # 均值饱和度比例
        self.max_sat_ratio_mean_label = ttk.Label(self.particular_frame, text="Maximum mean ratio:")
        self.max_sat_ratio_mean_spinbox = ttk.Spinbox(
            self.particular_frame,
            from_=0, to=1, increment=0.01, width=18
        )
        self.max_sat_ratio_mean_label.pack(side=tk.TOP, anchor=tk.W, padx=5)
        self.max_sat_ratio_mean_spinbox.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5, fill=tk.X)
        self.max_sat_ratio_mean_spinbox.insert(0, str(self.max_sat_ratio_mean))
        # 饱和度阈值
        self.sat_threshold_label = ttk.Label(self.particular_frame, text="Saturation threshold:")
        self.sat_threshold_spinbox = ttk.Spinbox(
            self.particular_frame,
            from_=0, to=10, increment=1, width=18
        )
        self.sat_threshold_label.pack(side=tk.TOP, anchor=tk.W, padx=5)
        self.sat_threshold_spinbox.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5, fill=tk.X)
        self.sat_threshold_spinbox.insert(0, str(self.sat_threshold))
        # 均值修正
        self.mean_refine_var = tk.BooleanVar()
        self.mean_refine_var.set(self.mean_refine)
        self.mean_refine_checkbtn = ttk.Checkbutton(
            self.particular_frame, text="Refine by mean ratio",
            variable=self.mean_refine_var
        )
        self.mean_refine_checkbtn.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5)
        # 多任务配置
        self._show_multitask_config()
        # 过滤低饱和度图片按钮
        self.start_btn = ttk.Button(
            self.particular_frame, text="Start Filter",
            command=lambda: self.filter_low_saturation(
                self.mean_refine_var.get(),
                float(self.max_sat_ratio_hist_spinbox.get()),
                float(self.max_sat_ratio_mean_spinbox.get()),
                int(self.sat_threshold_spinbox.get()),
                multitask_method=self.multitask_method_combobox.get(),
                runner_num=int(self.runner_num_spinbox.get())
            )
        )
        self.start_btn.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5, fill=tk.X)

    def _filter_similar_imgs(
        self,
        gen_func: callable,  # 生成字典的函数
        calc_func: callable,  # 计算相似度的函数
        condition: callable,  # 判断相似的条件
        multitask_method: str = "thread",
        runner_num: int = 8,
    ) -> list[set[str]]:
        """删除重复图片。最好先过滤出低饱和度图片"""
        img_list = self._start_fn()
        # (1) 生成图片特征和长宽比值
        # 图片特征字典，键为图片路径，值为参与比较图片相似度的参数（如哈希、直方图）和长宽比值
        img_dict: dict[str, tuple[any, float]] = self._multitask_gen_imgdict(
            gen_func, img_list, multitask_method, runner_num,
        )
        self._print_rst(f"Image feature calculation completed.\n")

        # (2) 所有图片两两比较，计算相似度（距离或指标）
        img_pairs = itertools.combinations(img_list, 2)
        similar_img_sets = []
        for img_pair in img_pairs:
            img_i_path, img_j_path = img_pair
            # 若img_i和img_j的长宽比值差异较大，则认为不是相似图片
            if abs(img_dict[img_i_path][1] - img_dict[img_j_path][1]) > 0.05:
                continue
            # 否则计算相似度，函数calc_func的参数为待比较图片的特征
            dist = calc_func(img_dict[img_i_path][0], img_dict[img_j_path][0])
            # 与阈值比较
            if condition(dist):
                self._print_rst(f"Similarity between {img_i_path} and {img_j_path}: {dist}")
                similar_img_sets.append({img_i_path, img_j_path})

        # (3) 将所有相似图片对去重，同一组相似图片合并在一个集合中
        merged_sets = merge_intersecting_sets(similar_img_sets)
        # 统计合并后的集合数量与筛选出来的图片数量
        self._print_rst(f"Total {len(merged_sets)} sets.")
        total_imgs = 0
        for img_set in merged_sets:
            total_imgs += len(img_set)
        self._print_rst(f"Total {total_imgs} similar images.")
        # 删除并返回结果
        self.delete(merged_sets)
        return merged_sets

    def filter_similar_imgs_hash(
        self,
        max_hash_dist: int = None,
        hash_func: str = None,
        hash_size: int = None,
        multitask_method: str = None,
        runner_num: int = None,
    ) -> list[set[str]]:
        """删除重复图片，方法为哈希算法"""
        if hash_func not in HashFunc:
            raise ValueError(f"Unsupported hash function: {hash_func}")

        self._print_rst(f"Filtering similar images using {hash_func}...")
        return self._filter_similar_imgs(
            gen_func=functools.partial(
                img2hash,
                hash_size=hash_size,
                hash_func=hash_func,
            ),
            calc_func=calc_hash_hammingdist,
            condition=lambda dist: dist <= max_hash_dist,
            multitask_method=multitask_method,
            runner_num=runner_num,
        )

    def _show_filter_similar_imgs_hash_param(self):
        """显示过滤相似图片的参数配置"""
        self._clear_particular_frame()
        # 最大汉明距离
        self.max_hash_dist_label = ttk.Label(self.particular_frame, text="Maximum hash distance:")
        self.max_hash_dist_spinbox = ttk.Spinbox(
            self.particular_frame,
            from_=0, to=100, increment=1, width=18
        )
        self.max_hash_dist_label.pack(side=tk.TOP, anchor=tk.W, padx=5)
        self.max_hash_dist_spinbox.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5, fill=tk.X)
        self.max_hash_dist_spinbox.insert(0, str(self.max_hash_dist))
        # 哈希函数
        self.hash_func_label = ttk.Label(self.particular_frame, text="Hash function:")
        self.hash_func_combobox = ttk.Combobox(
            self.particular_frame, values=list(HashFunc), width=15
        )
        self.hash_func_label.pack(side=tk.TOP, anchor=tk.W, padx=5)
        self.hash_func_combobox.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5, fill=tk.X)
        self.hash_func_combobox.set(self.hash_func)
        # 哈希大小
        self.hash_size_label = ttk.Label(self.particular_frame, text="Hash size:")
        self.hash_size_spinbox = ttk.Spinbox(
            self.particular_frame,
            from_=1, to=64, increment=1, width=18
        )
        self.hash_size_label.pack(side=tk.TOP, anchor=tk.W, padx=5)
        self.hash_size_spinbox.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5, fill=tk.X)
        self.hash_size_spinbox.insert(0, str(self.hash_size))
        # 多任务配置
        self._show_multitask_config()
        # 过滤相似图片按钮
        self.start_btn = ttk.Button(
            self.particular_frame, text="Start Filter",
            command=lambda: self.filter_similar_imgs_hash(
                int(self.max_hash_dist_spinbox.get()),
                self.hash_func_combobox.get(),
                int(self.hash_size_spinbox.get()),
                self.multitask_method_combobox.get(),
                int(self.runner_num_spinbox.get())
            )
        )
        self.start_btn.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5, fill=tk.X)

    def filter_similar_imgs_cos(
        self,
        min_cos_dist: float = None,
        multitask_method: str = None,
        runner_num: int = None,
    ) -> list[set[str]]:
        """删除重复图片，方法为余弦相似度，耗时约为哈希算法的4倍"""
        self._print_rst(f"Filtering similar images using cosine similarity...")
        return self._filter_similar_imgs(
            gen_func=img2normvec,
            calc_func=calc_cosine_similarity,
            condition=lambda dist: dist >= min_cos_dist,
            multitask_method=multitask_method,
            runner_num=runner_num,
        )

    def _show_filter_similar_imgs_cos_param(self):
        """显示过滤相似图片的参数配置"""
        self._clear_particular_frame()
        # 最小余弦距离
        self.min_cos_dist_label = ttk.Label(self.particular_frame, text="Minimum cosine distance:")
        self.min_cos_dist_spinbox = ttk.Spinbox(
            self.particular_frame,
            from_=0, to=1, increment=0.01, width=18
        )
        self.min_cos_dist_label.pack(side=tk.TOP, anchor=tk.W, padx=5)
        self.min_cos_dist_spinbox.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5, fill=tk.X)
        self.min_cos_dist_spinbox.insert(0, str(self.min_cos_dist))
        # 多任务配置
        self._show_multitask_config()
        # 过滤相似图片按钮
        self.start_btn = ttk.Button(
            self.particular_frame, text="Start Filter",
            command=lambda: self.filter_similar_imgs_cos(
                float(self.min_cos_dist_spinbox.get()),
                self.multitask_method_combobox.get(),
                int(self.runner_num_spinbox.get())
            )
        )
        self.start_btn.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5, fill=tk.X)

    def filter_similar_imgs_mse(
        self,
        max_mse: float = None,
        multitask_method: str = None,
        runner_num: int = None,
    ) -> list[set[str]]:
        """删除重复图片，方法为均方误差"""
        self._print_rst(f"Filtering similar images using mean squared error...")
        return self._filter_similar_imgs(
            gen_func=img2numpy,
            calc_func=mse,
            condition=lambda dist: dist <= max_mse,
            multitask_method=multitask_method,
            runner_num=runner_num,
        )

    def _show_filter_similar_imgs_mse_param(self):
        """显示过滤相似图片的参数配置"""
        self._clear_particular_frame()
        # 最大均方误差
        self.max_mse_label = ttk.Label(self.particular_frame, text="Maximum MSE:")
        self.max_mse_spinbox = ttk.Spinbox(
            self.particular_frame,
            from_=0, to=10000, increment=1, width=18
        )
        self.max_mse_label.pack(side=tk.TOP, anchor=tk.W, padx=5)
        self.max_mse_spinbox.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5, fill=tk.X)
        self.max_mse_spinbox.insert(0, str(self.max_mse))
        # 多任务配置
        self._show_multitask_config()
        # 过滤相似图片按钮
        self.start_btn = ttk.Button(
            self.particular_frame, text="Start Filter",
            command=lambda: self.filter_similar_imgs_mse(
                float(self.max_mse_spinbox.get()),
                self.multitask_method_combobox.get(),
                int(self.runner_num_spinbox.get())
            )
        )
        self.start_btn.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5, fill=tk.X)
