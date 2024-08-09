#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import font, ttk


palette = {  # 调色板
    "light": {
        "bottom_bg": "#EFF1F5",  # white
        "widget_bg": "#4582EC",  # blue
        "widget_text": "#EFF1F5",  # white
        "hover_widget_bg": "#FE640B",  # orange
        "disable_widget_bg": "#DCE0E8",  # light grey
        "disable_widget_text": "#6C6F85",  # grey
        "editable_entry_text": "#2C2F53",
        "readonly_entry_text": "#4C4F69",
        "editable_entry_bg": "#DCE0E8",
        "readonly_entry_bg": "#E6E9EF",
        "selected_row_bg": "#7287FD",  # lavender
        "progress_bar": "#40A02B",  # green
    }
}
col = palette["light"]


def apply_text_theme(text, editable=True):
    """应用 tk.Text 样式"""
    if editable:
        bg = col["editable_entry_bg"]
        fg = col["editable_entry_text"]
    else:
        bg = col["readonly_entry_bg"]
        fg = col["readonly_entry_text"]
    text.config(
        bg=bg,
        fg=fg,
        selectbackground=col["hover_widget_bg"],
        selectforeground=col["widget_text"],
        wrap=tk.WORD,
        undo=True, autoseparators=True, maxundo=-1,
        padx=5, pady=5,
    )


def apply_theme(root):
    # 字体样式
    default_font = font.nametofont("TkDefaultFont").cget("family")
    font_emphasis = (default_font, 10, "bold")

    # 创建样式
    style = ttk.Style(root)
    style.theme_create(
        "lattle",
        settings={
            "TFrame": {
                "configure": {
                    "background": col["bottom_bg"],
                }
            },
            "TButton": {  # 按钮
                "configure": {
                    "background": col["widget_bg"],
                    "foreground": col["widget_text"],
                    "focuscolor": col["widget_text"],  # 焦点颜色
                    "font": font_emphasis,
                    "relief": tk.FLAT,
                    "anchor": tk.CENTER,
                    "padding": (4, 0, 4, 2),
                },
                "map": {
                    "background": [
                        ("disabled", col["disable_widget_bg"]),
                        ("active", col["hover_widget_bg"]),
                    ],
                    "foreground": [
                        ("disabled", col["disable_widget_text"]),
                        ("active", col["bottom_bg"]),
                    ]
                }
            },
            "TLabel": {  # 标签
                "configure": {
                    "background": col["bottom_bg"],
                    "foreground": col["readonly_entry_text"],
                }
            },
            "TEntry": {  # 输入框
                "configure": {
                    "fieldbackground": col["editable_entry_bg"],
                    "background": col["editable_entry_bg"],
                    "foreground": col["editable_entry_text"],
                    "selectbackground": col["hover_widget_bg"],
                    "selectforeground": col["widget_text"],
                    "borderwidth": 0,
                    "relief": tk.FLAT,
                    "padding": (5, 5),
                },
                "map": {
                    "fieldbackground": [
                        ("disabled", col["disable_widget_bg"]),
                        ("readonly", col["disable_widget_bg"]),
                    ],
                    "background": [
                        ("disabled", col["disable_widget_bg"]),
                        ("readonly", col["disable_widget_bg"]),
                        ("active", col["hover_widget_bg"]),
                    ],
                    "foreground": [
                        ("disabled", col["disable_widget_text"]),
                        ("readonly", col["readonly_entry_text"]),
                        ("active", col["widget_text"]),
                    ]
                }
            },
            "TLabelframe": {  # 标签框
                "configure": {
                    "background": col["bottom_bg"],
                    "relief": tk.GROOVE,
                }
            },
            "TLabelframe.Label": {  # 标签框标题
                "configure": {
                    "background": col["bottom_bg"],
                    "foreground": col["readonly_entry_text"],
                    "font": font_emphasis,
                }
            },
            "Treeview": {  # 表格
                "configure": {
                    "background": col["bottom_bg"],
                    "foreground": col["readonly_entry_text"],
                    "fieldbackground": col["editable_entry_bg"],
                    "relief": tk.FLAT,
                    "borderwidth": 0,
                },
                "map": {
                    "background": [("selected", col["selected_row_bg"])],
                    "foreground": [("selected", col["disable_widget_bg"])],
                    "fieldbackground": [("selected", col["selected_row_bg"])],
                }
            },
            "Heading": {  # 表头
                "configure": {
                    "background": col["widget_bg"],
                    "foreground": col["widget_text"],
                    "relief": tk.FLAT
                }
            },
            "TCheckbutton": {  # 复选框
                "configure": {
                    "background": col["bottom_bg"],
                    "foreground": col["readonly_entry_text"],
                    "indicatorcolor": col["widget_bg"],
                    "indicatorrelief": tk.RIDGE,
                },
                "map": {
                    "background": [
                        ("disabled", col["disable_widget_bg"]),
                        ("active", col["hover_widget_bg"]),
                        ("!selected", col["bottom_bg"]),
                    ],
                    "foreground": [
                        ("disabled", col["disable_widget_text"]),
                        ("active", col["widget_text"]),
                    ],
                    "indicatorcolor": [
                        ("disabled", col["disable_widget_text"]),
                        ("selected", col["widget_bg"]),
                        ("!selected", col["editable_entry_bg"]),
                    ]
                }
            },
            "TRadiobutton": {  # 单选按钮
                "configure": {
                    "background": col["bottom_bg"],
                    "foreground": col["readonly_entry_text"],
                    "indicatorcolor": col["widget_bg"],
                    "indicatorrelief": tk.RIDGE,
                },
                "map": {
                    "background": [
                        ("disabled", col["disable_widget_bg"]),
                        ("active", col["hover_widget_bg"]),
                        ("!selected", col["bottom_bg"])
                    ],
                    "foreground": [
                        ("disabled", col["disable_widget_text"]),
                        ("active", col["widget_text"]),
                    ],
                    "indicatorcolor": [
                        ("disabled", col["disable_widget_text"]),
                        ("selected", col["widget_bg"]),
                        ("!selected", col["editable_entry_bg"])
                    ]
                }
            },
            "TSpinbox": {  # 数字输入框，数值范围控件
                "configure": {
                    "fieldbackground": col["editable_entry_bg"],
                    "background": col["editable_entry_bg"],
                    "foreground": col["editable_entry_text"],
                    "selectbackground": col["hover_widget_bg"],
                    "selectforeground": col["widget_text"],
                    "arrowcolor": col["widget_bg"],
                    "arrowsize": 15,
                    "borderwidth": 0,
                    "relief": tk.FLAT,
                    "padding": (5, 5),
                },
                "map": {
                    "fieldbackground": [
                        ("disabled", col["disable_widget_bg"]),
                        ("readonly", col["disable_widget_bg"])
                    ],
                    "background": [
                        ("disabled", col["disable_widget_bg"]),
                        ("active", col["hover_widget_bg"]),
                        ("readonly", col["disable_widget_bg"])
                    ],
                    "foreground": [
                        ("disabled", col["disable_widget_text"]),
                        ("readonly", col["readonly_entry_text"])
                    ]
                }
            },
            "TCombobox": {  # 下拉选择框
                "configure": {
                    "fieldbackground": col["editable_entry_bg"],
                    "background": col["editable_entry_bg"],
                    "foreground": col["editable_entry_text"],
                    "selectbackground": col["hover_widget_bg"],
                    "selectforeground": col["widget_text"],
                    "arrowcolor": col["widget_bg"],
                    "arrowsize": 15,
                    "borderwidth": 0,
                    "relief": tk.FLAT,
                    "padding": (5, 5),
                },
                "map": {
                    "fieldbackground": [
                        ("disabled", col["disable_widget_bg"]),
                        ("readonly", col["disable_widget_bg"])
                    ],
                    "background": [
                        ("disabled", col["disable_widget_bg"]),
                        ("active", col["hover_widget_bg"]),
                        ("readonly", col["disable_widget_bg"])
                    ],
                    "foreground": [
                        ("disabled", col["disable_widget_text"]),
                        ("readonly", col["readonly_entry_text"])
                    ],
                    "arrowcolor": [
                        ("disabled", col["disable_widget_text"]),
                        ("active", col["disable_widget_bg"]),
                        ("readonly", col["widget_bg"])
                    ]
                }
            },
            "Horizontal.TScrollbar": {  # 水平滚动条
                "configure": {
                    "background": col["widget_bg"],
                    "troughcolor": col["editable_entry_bg"],
                    "troughrelief": tk.FLAT,
                    "sliderrelief": tk.FLAT,
                    "arrowcolor": col["bottom_bg"],
                    "relief": tk.FLAT
                },
                "map": {
                    "background": [
                        ("disabled", col["disable_widget_bg"]),
                        ("active", col["hover_widget_bg"])
                    ]
                }
            },
            "Vertical.TScrollbar": {  # 竖直滚动条
                "configure": {
                    "background": col["widget_bg"],
                    "troughcolor": col["editable_entry_bg"],
                    "troughrelief": tk.FLAT,
                    "sliderrelief": tk.FLAT,
                    "arrowcolor": col["bottom_bg"],
                    "relief": tk.FLAT
                },
                "map": {
                    "background": [
                        ("disabled", col["disable_widget_bg"]),
                        ("active", col["hover_widget_bg"])
                    ]
                }
            },
            "Horizontal.TProgressbar": {  # 水平进度条
                "configure": {
                    "background": col["progress_bar"],
                    "troughcolor": col["editable_entry_bg"],
                    "troughrelief": tk.FLAT,
                    "pbarrelief": tk.FLAT
                }
            },
            "Vertical.TProgressbar": {  # 竖直进度条
                "configure": {
                    "background": col["progress_bar"],
                    "troughcolor": col["editable_entry_bg"],
                    "troughrelief": tk.FLAT,
                    "pbarrelief": tk.FLAT
                }
            },
        }
    )

    # 应用样式
    style.theme_use("lattle")
    # 左对齐按钮样式
    style.configure('LeftAligned.TButton', anchor=tk.W, padding=(4, 4))
