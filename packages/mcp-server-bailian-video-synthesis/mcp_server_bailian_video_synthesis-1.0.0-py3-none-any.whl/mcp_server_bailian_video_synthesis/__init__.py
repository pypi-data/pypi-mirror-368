#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里云百炼-通义万相视频编辑统一模型MCP服务器包

本包实现了通义万相-通用视频编辑API的所有功能，包括：
- 多图参考视频生成
- 视频重绘
- 局部编辑
- 视频延展
- 视频画面扩展

官方文档：https://help.aliyun.com/zh/model-studio/wanx-vace-api-reference

Author: John Chen
"""

from .server import BailianVideoSynthesisServer, main

__version__ = "1.0.0"
__author__ = "John Chen"
__email__ = "john.chen@example.com"
__description__ = "阿里云百炼-通义万相视频编辑统一模型MCP服务器"

__all__ = [
    "BailianVideoSynthesisServer",
    "main",
    "__version__",
    "__author__",
    "__email__",
    "__description__",
]