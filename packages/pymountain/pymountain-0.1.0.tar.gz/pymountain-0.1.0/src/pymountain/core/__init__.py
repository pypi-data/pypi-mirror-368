"""
PyMountain核心模块 | PyMountain core module

包含数据结构和渲染器的基础定义 | Contains basic definitions for data structures and renderers
"""

# 核心模块导入 | Core module imports
from .data import BasePoint, MountainData
from .renderer import BaseRenderer

__all__ = [
    "BasePoint",
    "MountainData", 
    "BaseRenderer"
]