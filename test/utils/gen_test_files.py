#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成用于测试的文件，包括文件夹以及一系列图片。
图片内容使用词云随机生成。
"""

from typing import List
from random import shuffle
from wordcloud import WordCloud
import imageio.v3 as iio
import os


Abspath = "test/"
DeleteDir = "$DELETE/"


def gen_wordcloud(
        words: List[str],
        true_format: str, fake_format: str = None,
        prefix_filename: str = f"{Abspath}ciyun",
        width=800, height=600
):
    # 如果没有路径，则创建
    path = os.path.dirname(prefix_filename)
    if path is not None and not os.path.exists(path):
        os.mkdir(path)

    # 生成词云
    shuffle(words)  # 打乱词的顺序
    wc = WordCloud(
        width=width, height=height,
        background_color='white', max_words=len(words)
    )
    wc.generate(' '.join(words))  # 生成词云
    base_filename = f'{prefix_filename}_{true_format}'
    wc.to_file(f'{base_filename}.{true_format}')  # 保存

    # 重命名文件，伪装成其他格式，如果未指定其他格式，则默认与真实格式相同
    fake_format = fake_format or true_format
    new_filename = f'{base_filename}.{fake_format}'
    os.rename(f'{base_filename}.{true_format}', new_filename)
    return new_filename


def create_gif(words: List[str], prefix_filename: str = f"{Abspath}ciyun", frames: int = 5):
    # 如果没有路径，则创建
    path = os.path.dirname(prefix_filename)
    if path is not None and not os.path.exists(path):
        os.mkdir(path)

    filenames = []
    for i in range(frames):
        frame_filename = f'{path}/tmp_{i}'
        fullname = gen_wordcloud(words, 'png', prefix_filename=frame_filename)
        filenames.append(fullname)

    # 使用imageio创建GIF
    images = [iio.imread(fn) for fn in filenames]
    iio.imwrite(f'{prefix_filename}_gif.gif', images, duration=0.5)

    for fn in filenames:
        os.remove(fn)


def copy_files(file_list, target_dir, suffix=""):
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)
    for file in file_list:
        with open(f'{Abspath}{file}', 'rb') as f:
            content = f.read()
            basename, ext = os.path.splitext(file)
            with open(f'{target_dir}{basename}{suffix}{ext}', 'wb') as f1:
                f1.write(content)


def main():
    words = [
        'apple', 'banana', 'cherry', 'date', 'elderberry', 'fig', 'grape',
        'honeydew', 'indigo', 'jambu', 'kiwi', 'lemon', 'mango', 'nectarine',
        'orange', 'papaya', 'quince', 'raspberry', 'strawberry', 'tangerine',
        'ugli', 'violet', 'watermelon', 'xigua', 'yam', 'zucchini'
    ]

    # 生成各种格式的图片
    formats = ['png', 'jpg', 'webp', 'bmp']
    for fmt in formats:
        gen_wordcloud(words, fmt)
    # GIF需单独生成
    create_gif(words, frames=5)

    # 列出test目录下的所有图片
    file_list = []
    for root, dirs, files in os.walk(Abspath):
        for file in files:
            file_list.append(file)
    # 将所有图片复制一份，放到test目录下，重命名添加“副本”后缀
    copy_files(file_list, Abspath, suffix='_副本')
    # 将所有图片复制两份，放到test/dir1和test/dir2目录下
    dir1 = f'{Abspath}dir1/'
    copy_files(file_list, dir1)
    dir2 = f'{Abspath}dir2/'
    copy_files(file_list, dir2)
    dir3 = dir1 + DeleteDir
    dir4 = dir2 + DeleteDir
    dir5 = Abspath + DeleteDir
    for tgt_dir in [dir3, dir4, dir5]:
        copy_files(file_list, tgt_dir)


if __name__ == '__main__':
    main()
