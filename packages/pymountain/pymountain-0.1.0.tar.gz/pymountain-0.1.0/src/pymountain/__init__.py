"""
PyMountain - 功能强大、高度模块化的Python软件包，专注于山体地形数据的可视化

PyMountain is a powerful, highly modular Python package focused on mountain terrain data visualization.

主要功能 | Main Features:
- 山体地形数据的存储和管理 | Storage and management of mountain terrain data
- 多种渲染模式支持 | Multiple rendering mode support
- 实时数据更新和交互 | Real-time data updates and interaction
- 丰富的可视化参数配置 | Rich visualization parameter configuration
- 强扩展性的插件架构 | Highly extensible plugin architecture

基本使用示例 | Basic Usage Example:
    >>> from pymountain import MountainData, MatplotlibRenderer
    >>> # 创建山体数据 | Create mountain data
    >>> data = MountainData()
    >>> data.add_point(0, 0, 100)
    >>> data.add_point(1, 1, 200)
    >>> 
    >>> # 创建渲染器并可视化 | Create renderer and visualize
    >>> renderer = MatplotlibRenderer()
    >>> renderer.render(data)
"""

# 版本信息 | Version information
__version__ = "0.1.0"
__author__ = "PyMountain Team"
__email__ = "pymountain@example.com"
__license__ = "MIT"

# 核心模块导入 | Core module imports
from .core.data import BasePoint, MountainData
from .core.renderer import BaseRenderer
from .renderers.matplotlib_renderer import (
    MatplotlibRenderer,
    Matplotlib3DRenderer,
    MatplotlibContourRenderer,
)
from .utils.interpolation import (
    linear_interpolation,
    cubic_interpolation,
    rbf_interpolation,
)
from .utils.color_mapping import (
    ColorMapper,
    create_elevation_colormap,
    apply_color_mapping,
)

# 公共API | Public API
__all__ = [
    # 版本信息 | Version info
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    # 核心数据类 | Core data classes
    "BasePoint",
    "MountainData",
    # 渲染器基类 | Renderer base class
    "BaseRenderer",
    # Matplotlib渲染器 | Matplotlib renderers
    "MatplotlibRenderer",
    "Matplotlib3DRenderer",
    "MatplotlibContourRenderer",
    # 插值工具 | Interpolation utilities
    "linear_interpolation",
    "cubic_interpolation",
    "rbf_interpolation",
    # 颜色映射工具 | Color mapping utilities
    "ColorMapper",
    "create_elevation_colormap",
    "apply_color_mapping",
]

# 包级别配置 | Package-level configuration
class Config:
    """PyMountain全局配置类 | PyMountain global configuration class"""
    
    # 默认插值方法 | Default interpolation method
    DEFAULT_INTERPOLATION = "linear"
    
    # 默认颜色映射 | Default color mapping
    DEFAULT_COLORMAP = "terrain"
    
    # 默认渲染参数 | Default rendering parameters
    DEFAULT_FIGURE_SIZE = (10, 8)
    DEFAULT_DPI = 100
    DEFAULT_UPDATE_INTERVAL_MS = 100
    
    # 性能配置 | Performance configuration
    MAX_POINTS_FOR_REALTIME = 10000
    INTERPOLATION_GRID_SIZE = 100
    
    @classmethod
    def set_default_interpolation(cls, method: str) -> None:
        """设置默认插值方法 | Set default interpolation method"""
        if method not in ["linear", "cubic", "rbf"]:
            raise ValueError(f"Unsupported interpolation method: {method}")
        cls.DEFAULT_INTERPOLATION = method
    
    @classmethod
    def set_default_colormap(cls, colormap: str) -> None:
        """设置默认颜色映射 | Set default colormap"""
        cls.DEFAULT_COLORMAP = colormap
    
    @classmethod
    def set_performance_limits(cls, max_points: int, grid_size: int) -> None:
        """设置性能限制 | Set performance limits"""
        cls.MAX_POINTS_FOR_REALTIME = max_points
        cls.INTERPOLATION_GRID_SIZE = grid_size


# 全局配置实例 | Global configuration instance
config = Config()


def get_version() -> str:
    """获取PyMountain版本信息 | Get PyMountain version information"""
    return __version__


def get_info() -> dict:
    """获取PyMountain包信息 | Get PyMountain package information"""
    return {
        "name": "PyMountain",
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "license": __license__,
        "description": "功能强大、高度模块化的Python软件包，专注于山体地形数据的可视化",
        "homepage": "https://github.com/pymountain/pymountain",
    }


# 便捷函数 | Convenience functions
def quick_render(points, renderer_type="3d", **kwargs):
    """
    快速渲染山体数据的便捷函数 | Convenience function for quick mountain data rendering
    
    Args:
        points: 点数据列表，格式为[(x, y, z), ...] | Point data list in format [(x, y, z), ...]
        renderer_type: 渲染器类型 | Renderer type ("3d", "contour", "auto")
        **kwargs: 传递给渲染器的额外参数 | Additional parameters for renderer
    
    Returns:
        渲染器实例 | Renderer instance
    """
    # 创建数据对象 | Create data object
    data = MountainData()
    for x, y, z in points:
        data.add_point(x, y, z)
    
    # 准备渲染器配置 | Prepare renderer configuration
    config_dict = kwargs.copy()
    
    # 选择渲染器 | Select renderer
    if renderer_type == "3d":
        renderer = Matplotlib3DRenderer(config=config_dict)
    elif renderer_type == "contour":
        renderer = MatplotlibContourRenderer(config=config_dict)
    else:  # auto
        # 根据数据点数量自动选择 | Auto-select based on data point count
        if len(points) > 1000:
            renderer = MatplotlibContourRenderer(config=config_dict)
        else:
            renderer = Matplotlib3DRenderer(config=config_dict)
    
    # 渲染并返回 | Render and return
    renderer.render(data)
    return renderer