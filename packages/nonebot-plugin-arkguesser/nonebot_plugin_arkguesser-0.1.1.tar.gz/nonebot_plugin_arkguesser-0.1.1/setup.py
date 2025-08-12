#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="nonebot-plugin-arkguesser",
    version="0.1.0",
    author="lizhiqi233-rgb",
    author_email="lizhiqi233-rgb@example.com",
    description="明日方舟猜干员游戏 - 支持多种游戏模式和题库设置",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lizhiqi233-rgb/nonebot-plugin-arkguesser",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: NoneBot",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications :: Chat",
        "Topic :: Games/Entertainment",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    include_package_data=True,
    zip_safe=False,
)
