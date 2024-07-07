#!usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from setuptools import setup

from src.config import Conf


if sys.version_info[0] < 3 or sys.version_info[1] < 6:
    sys.exit("Python 3.6 or higher is required.")


def read_requirements(filename):
    with open(filename, 'r') as file:
        return file.read().splitlines()


def read_readme(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()


setup(
    name=Conf.PROJECT_NAME,
    version=Conf.VERSION,
    author=Conf.AUTHOR,
    description=Conf.DESCRIPTION,
    long_description=read_readme('README.md'),
    long_description_content_type='text/markdown',
    url=Conf.URL,
    packages=[Conf.PROJECT_NAME_LOWER],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=read_requirements('requirements.txt'),
    entry_points={
        'console_scripts': [
            f'{Conf.PROJECT_NAME_LOWER} = '
            f'{Conf.PROJECT_NAME_LOWER}.main:main'
        ]
    }
)
