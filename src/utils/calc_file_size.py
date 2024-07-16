#!usr/bin/env python
# -*- coding: utf-8 -*-

import os


def calc_file_size(file_path: str) -> str:
    """计算文件大小，选择合适的单位表达，返回数字+单位"""
    img_size = os.path.getsize(file_path)
    img_size_str = f"{img_size} B" if img_size < 1024 else \
        f"{round(img_size / 1024, 3)} KB" if img_size < 1024 ** 2 else \
        f"{round(img_size / 1024 ** 2, 3)} MB" if img_size < 1024 ** 3 else \
        f"{round(img_size / 1024 ** 3, 3)} GB"
    return img_size_str
