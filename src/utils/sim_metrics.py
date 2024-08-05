#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import partial

import numpy as np
from PIL import Image
from imagehash import (
    phash, dhash, whash,
    average_hash as ahash,
    colorhash as chash,
)

HashFunc = {
    "ahash": ahash,
    "phash": phash,
    "dhash": dhash,
    "whash": whash,
    "chash": chash,
}


def img2hash(img_relpath, hash_size=8, hash_func="ahash"):
    """生成图片哈希指纹"""
    img_pil = Image.open(img_relpath)
    if img_pil.format == 'PNG':
        if img_pil.mode not in ("RGBA","RGB"):
            img_pil = img_pil.convert("RGBA")
    _func = HashFunc[hash_func]
    if hash_func != "chash":
        _func = partial(_func, hash_size=hash_size)
    img_hash = _func(img_pil)
    img_ratio = img_pil.width / img_pil.height
    return img_hash, img_ratio


def calc_hash_hammingdist(img_i_hash, img_j_hash):
    """计算两个图片哈希值的汉明距离"""
    return img_i_hash - img_j_hash


# noinspection PyUnresolvedReferences
def get_thumbnail(img_pil, size=(50, 50), greyscale=False):
    try:
        img = img_pil.resize(size, Image.ANTIALIAS)
    except AttributeError:
        img = img_pil.resize(size, Image.Resampling.LANCZOS)
    if greyscale:
        img = img.convert('L')
    return img


def img2normvec(img_relpath):
    """生成图片的标准化向量"""
    img_pil = Image.open(img_relpath)
    img_ratio = img_pil.width / img_pil.height
    img = get_thumbnail(img_pil)
    img_vec = []
    for pixel_tuple in img.getdata():
        img_vec.append(np.average(pixel_tuple))
    img_vec = np.array(img_vec, dtype=np.float64)
    # img_norm = np.linalg.norm(img_vec)
    img_normed_vec = img_vec / np.linalg.norm(img_vec)
    return img_normed_vec, img_ratio


def calc_cosine_similarity(img_i_normed_vec, img_j_normed_vec):
    """
    计算两个图片的余弦相似度
    $$\textrm{Cosine Similarity} = \frac{A \cdot B}{||A|| \cdot ||B||}$$
    """
    return np.dot(img_i_normed_vec, img_j_normed_vec)


def img2numpy(img_relpath):
    img_pil = Image.open(img_relpath).convert("L")
    img_ratio = img_pil.width / img_pil.height
    img = get_thumbnail(img_pil, size=(16, 16))
    img_arr = np.array(img)
    return img_arr, img_ratio


def mse(img_i_arr, img_j_arr):
    """
    计算两个图片的均方误差
    $$\textrm{MSE} = \frac{1}{n}\sum_{i=1}^{n}(x_i - y_i)^2$$
    """
    return np.mean((img_i_arr - img_j_arr) ** 2)
