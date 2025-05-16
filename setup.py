#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="financial_products_scraper",
    version="0.1.0",
    author="Jezeehu",
    author_email="zee_hu@qq.com",
    description="理财产品数据抓取工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zeehu/financial_products_scraper",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "financial-scraper=src.main:main",
        ],
    },
)