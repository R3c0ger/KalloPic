#!usr/bin/env python
# -*- coding: utf-8 -*-

# noinspection PyProtectedMember
from cv2 import calcHist, cvtColor, COLOR_RGB2HSV
import numpy as np
from PIL import Image


def calc_saturation_mean(img_cv2_hsv):
    """
    计算饱和度平均值，返回饱和度平均值与最大值的比值。
    使用CV2库，用时比PIL库较短，筛选出的图片较多。
    """
    return img_cv2_hsv[:, :, 1].mean() / 255


def calc_saturation_hist(img_cv2_hsv, sat_threshold=10):
    """计算饱和度直方图，返回低饱和度像素所占的比例"""
    s = img_cv2_hsv[:, :, 1]
    # 计算饱和度值在hist_threshold之后的像素所占的比例
    sat_hist = calcHist([s], [0], None, [256], [0, 256])
    low_saturation_num = sat_hist[sat_threshold:]
    return sum(low_saturation_num) / sum(sat_hist)


def img2sat_ratio(_img_relpath, _sat_threshold):
    img_pil = Image.open(_img_relpath)
    # 先判断图片是否为黑白图片（L或者LA模式）
    if img_pil.mode in ("LA", "L"):
        return -1, -1
    # 如果图片不是RGB或RGBA模式，则转换为RGB模式（最好先删除所有gif图片！）
    if img_pil.mode not in ("RGBA", "RGB"):
        img_pil = img_pil.convert("RGBA")
    # 再转换为OpenCV格式的HSV图片
    img_hsv = cvtColor(np.asarray(img_pil), COLOR_RGB2HSV)
    return (
        calc_saturation_hist(img_hsv, _sat_threshold),
        calc_saturation_mean(img_hsv)
    )
