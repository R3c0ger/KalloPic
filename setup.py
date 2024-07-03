#!usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from setuptools import setup

from kallopic.constants import Constants


if sys.version_info[0] < 3 or sys.version_info[1] < 6:
    sys.exit("Python 3.6 or higher is required.")


def read_requirements(filename):
    with open(filename, 'r') as file:
        return file.read().splitlines()


def read_readme(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()


setup(
    name=Constants.PROJECT_NAME,
    version=Constants.VERSION,
    author=Constants.AUTHOR,
    description=Constants.DESCRIPTION,
    long_description=read_readme('README.md'),
    long_description_content_type='text/markdown',
    url=Constants.URL,
    packages=[Constants.PROJECT_NAME_LOWER],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=read_requirements('requirements.txt'),
    entry_points={
        'console_scripts': [
            f'{Constants.PROJECT_NAME_LOWER} = '
            f'{Constants.PROJECT_NAME_LOWER}.main:main'
        ]
    }
)
