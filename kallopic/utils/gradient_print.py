#!usr/bin/env python
# -*- coding: utf-8 -*-
import os


def gen_gradient_textline(textline, start_color=None, end_color=None):
    """
    生成渐变颜色的一行文本

    :param textline: 文本内容
    :param start_color: 起始颜色，默认为(0, 120, 212)（蓝色）
    :param end_color: 结束颜色，默认为(255, 165, 0)（橙色）
    :return: 带颜色的文本
    """
    textline_rst = ""
    start_color = (0, 120, 212) if not start_color else start_color
    end_color = (255, 165, 0) if not end_color else end_color
    # 计算颜色变化的步长
    steps = len(textline)
    r_start, g_start, b_start = start_color
    r_end, g_end, b_end = end_color
    # 创建颜色渐变
    for i, char in enumerate(textline):
        # 计算当前字符的颜色
        r = int(r_start + (r_end - r_start) * i / steps)
        g = int(g_start + (g_end - g_start) * i / steps)
        b = int(b_start + (b_end - b_start) * i / steps)
        # 将RGB转换成ANSI颜色码
        color_code = f"\033[38;2;{r};{g};{b}m"
        # 输出带颜色的字符
        # sys.stdout.write(color_code + char)
        textline_rst += color_code + char
    # 重置颜色
    # sys.stdout.write('\033[0m')
    textline_rst += '\033[0m'
    return textline_rst


def print_gradient_text(text="", enable_print=True):
    text_rst = ""
    for line in text.splitlines():
        line_str = gen_gradient_textline(line)
        text_rst += line_str + '\n'
    if enable_print:
        print(text_rst)
    return text_rst
