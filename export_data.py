#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
理财产品数据导出工具入口脚本

该脚本用于将数据库中的理财产品和净值数据导出为CSV或Excel格式，
支持指定导出格式和输出目录。

使用方法:
    python export_data.py --format csv
    python export_data.py --format excel
    python export_data.py --format all --output-dir ./my_data
"""

import sys
import os

# 添加源码目录到sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# 导入导出工具
from src.utils.export_data import main

if __name__ == "__main__":
    main() 