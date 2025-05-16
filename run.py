#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
理财产品信息抓取工具入口脚本
"""

import sys
import os

# 添加源码目录到sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# 导入主程序
from src.main import main

if __name__ == "__main__":
    main()