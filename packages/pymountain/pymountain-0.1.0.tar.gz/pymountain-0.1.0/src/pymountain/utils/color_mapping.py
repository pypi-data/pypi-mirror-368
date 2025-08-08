"""
PyMountain颜色映射工具模块 | PyMountain color mapping utilities module

提供颜色映射功能用于山体地形数据的可视化 | Provides color mapping functionality for mountain terrain data visualization
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap, Normalize, ListedColormap
from typing import Dict, List, Tuple, Union, Optional, Any
import warnings


class ColorMapper:
    """
    颜色映射器类 | Color mapper class
    
    提供灵活的颜色映射功能，支持多种颜色映射方案 | Provides flexible color mapping functionality with support for various color mapping schemes
    
    Attributes:
        colormap: 颜色映射对象 | Colormap object
        normalizer: 数值标准化器 | Value normalizer
        name: 颜色映射名称 | Colormap name
    """
    
    def __init__(self, colormap: Union[str, LinearSegmentedColormap, ListedColormap] = 'terrain',
                 vmin: Optional[float] = None, vmax: Optional[float] = None,
                 name: Optional[str] = None):
        """
        初始化颜色映射器 | Initialize color mapper
        
        Args:
            colormap: 颜色映射名称或对象 | Colormap name or object
            vmin: 最小值 | Minimum value
            vmax: 最大值 | Maximum value
            name: 颜色映射名称 | Colormap name
        """
        self.name = name or str(colormap)
        
        # 设置颜色映射 | Set colormap
        if isinstance(colormap, str):
            try:
                self.colormap = plt.get_cmap(colormap)
            except ValueError:
                warnings.warn(f"Unknown colormap '{colormap}', using 'terrain' instead")
                self.colormap = plt.get_cmap('terrain')
        else:
            self.colormap = colormap
        
        # 设置标准化器 | Set normalizer
        self.normalizer = Normalize(vmin=vmin, vmax=vmax)
        
        # 缓存映射结果 | Cache mapping results
        self._cache = {}
    
    def map_values(self, values: np.ndarray, alpha: Optional[float] = None) -> np.ndarray:
        """
        将数值映射为颜色 | Map values to colors
        
        Args:
            values: 输入数值数组 | Input value array
            alpha: 透明度 | Alpha transparency
            
        Returns:
            RGBA颜色数组 | RGBA color array
        """
        # 标准化数值 | Normalize values
        normalized_values = self.normalizer(values)
        
        # 应用颜色映射 | Apply colormap
        colors = self.colormap(normalized_values)
        
        # 设置透明度 | Set alpha
        if alpha is not None:
            if colors.ndim == 1:
                colors = np.array(colors)
            colors[..., 3] = alpha
        
        return colors
    
    def get_color_at_value(self, value: float, alpha: Optional[float] = None) -> Tuple[float, float, float, float]:
        """
        获取特定数值对应的颜色 | Get color corresponding to specific value
        
        Args:
            value: 输入数值 | Input value
            alpha: 透明度 | Alpha transparency
            
        Returns:
            RGBA颜色元组 | RGBA color tuple
        """
        normalized_value = self.normalizer(value)
        color = self.colormap(normalized_value)
        
        if alpha is not None:
            color = (*color[:3], alpha)
        
        return color
    
    def update_range(self, vmin: float, vmax: float) -> None:
        """
        更新数值范围 | Update value range
        
        Args:
            vmin: 新的最小值 | New minimum value
            vmax: 新的最大值 | New maximum value
        """
        self.normalizer.vmin = vmin
        self.normalizer.vmax = vmax
        self._cache.clear()
    
    def auto_range(self, values: np.ndarray, percentile: Tuple[float, float] = (2, 98)) -> None:
        """
        自动设置数值范围 | Automatically set value range
        
        Args:
            values: 数值数组 | Value array
            percentile: 百分位数范围 | Percentile range
        """
        valid_values = values[~np.isnan(values)]
        if len(valid_values) == 0:
            return
        
        vmin = np.percentile(valid_values, percentile[0])
        vmax = np.percentile(valid_values, percentile[1])
        
        self.update_range(vmin, vmax)
    
    def create_colorbar(self, ax: plt.Axes, label: str = 'Elevation (m)', 
                       orientation: str = 'vertical', **kwargs) -> plt.colorbar:
        """
        创建颜色条 | Create colorbar
        
        Args:
            ax: 坐标轴对象 | Axes object
            label: 颜色条标签 | Colorbar label
            orientation: 方向 | Orientation
            **kwargs: 额外参数 | Additional parameters
            
        Returns:
            颜色条对象 | Colorbar object
        """
        # 创建ScalarMappable对象 | Create ScalarMappable object
        sm = plt.cm.ScalarMappable(cmap=self.colormap, norm=self.normalizer)
        sm.set_array([])
        
        # 创建颜色条 | Create colorbar
        cbar = plt.colorbar(sm, ax=ax, orientation=orientation, **kwargs)
        cbar.set_label(label)
        
        return cbar
    
    def get_discrete_colors(self, n_colors: int) -> List[Tuple[float, float, float, float]]:
        """
        获取离散颜色列表 | Get discrete color list
        
        Args:
            n_colors: 颜色数量 | Number of colors
            
        Returns:
            RGBA颜色列表 | RGBA color list
        """
        values = np.linspace(0, 1, n_colors)
        colors = self.colormap(values)
        return [tuple(color) for color in colors]
    
    def save_colormap(self, filepath: str, width: int = 256, height: int = 32) -> None:
        """
        保存颜色映射为图像 | Save colormap as image
        
        Args:
            filepath: 文件路径 | File path
            width: 图像宽度 | Image width
            height: 图像高度 | Image height
        """
        # 创建颜色条图像 | Create colorbar image
        gradient = np.linspace(0, 1, width).reshape(1, -1)
        gradient = np.vstack([gradient] * height)
        
        fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
        ax.imshow(gradient, aspect='auto', cmap=self.colormap)
        ax.set_xlim(0, width-1)
        ax.set_xticks([])
        ax.set_yticks([])
        
        plt.savefig(filepath, bbox_inches='tight', pad_inches=0, dpi=100)
        plt.close(fig)
    
    def __str__(self) -> str:
        return f"ColorMapper(name='{self.name}', range=({self.normalizer.vmin}, {self.normalizer.vmax}))"
    
    def __repr__(self) -> str:
        return self.__str__()


def create_elevation_colormap(colors: Optional[List[str]] = None, 
                             name: str = 'custom_elevation') -> LinearSegmentedColormap:
    """
    创建高程颜色映射 | Create elevation colormap
    
    Args:
        colors: 颜色列表 | Color list
        name: 颜色映射名称 | Colormap name
        
    Returns:
        线性分段颜色映射 | Linear segmented colormap
    """
    if colors is None:
        # 默认高程颜色：深蓝(海洋) -> 绿色(低地) -> 黄色(丘陵) -> 棕色(山地) -> 白色(雪峰)
        # Default elevation colors: deep blue (ocean) -> green (lowland) -> yellow (hills) -> brown (mountains) -> white (snow peaks)
        colors = [
            '#000080',  # 深蓝 | Deep blue
            '#0080FF',  # 蓝色 | Blue
            '#00FF80',  # 青绿 | Cyan green
            '#80FF00',  # 黄绿 | Yellow green
            '#FFFF00',  # 黄色 | Yellow
            '#FF8000',  # 橙色 | Orange
            '#FF0000',  # 红色 | Red
            '#800000',  # 深红 | Dark red
            '#FFFFFF'   # 白色 | White
        ]
    
    # 创建线性分段颜色映射 | Create linear segmented colormap
    cmap = LinearSegmentedColormap.from_list(name, colors)
    
    return cmap


def create_terrain_colormap(style: str = 'realistic') -> LinearSegmentedColormap:
    """
    创建地形颜色映射 | Create terrain colormap
    
    Args:
        style: 风格类型 | Style type ('realistic', 'artistic', 'scientific')
        
    Returns:
        地形颜色映射 | Terrain colormap
    """
    if style == 'realistic':
        # 真实地形颜色 | Realistic terrain colors
        colors = [
            '#1e3a8a',  # 深海蓝 | Deep ocean blue
            '#3b82f6',  # 海蓝 | Ocean blue
            '#06b6d4',  # 浅海蓝 | Shallow ocean blue
            '#10b981',  # 海岸绿 | Coastal green
            '#22c55e',  # 平原绿 | Plain green
            '#84cc16',  # 草地绿 | Grassland green
            '#eab308',  # 丘陵黄 | Hill yellow
            '#f59e0b',  # 山地橙 | Mountain orange
            '#dc2626',  # 高山红 | High mountain red
            '#7c2d12',  # 山峰棕 | Peak brown
            '#f3f4f6'   # 雪峰白 | Snow peak white
        ]
    elif style == 'artistic':
        # 艺术风格颜色 | Artistic style colors
        colors = [
            '#4c1d95',  # 紫色 | Purple
            '#7c3aed',  # 紫罗兰 | Violet
            '#2563eb',  # 蓝色 | Blue
            '#0891b2',  # 青色 | Cyan
            '#059669',  # 绿色 | Green
            '#ca8a04',  # 金色 | Gold
            '#ea580c',  # 橙色 | Orange
            '#dc2626',  # 红色 | Red
            '#fbbf24'   # 黄色 | Yellow
        ]
    elif style == 'scientific':
        # 科学可视化颜色 | Scientific visualization colors
        colors = [
            '#0f172a',  # 深色 | Dark
            '#1e293b',  # 深灰 | Dark gray
            '#334155',  # 灰色 | Gray
            '#475569',  # 中灰 | Medium gray
            '#64748b',  # 浅灰 | Light gray
            '#94a3b8',  # 很浅灰 | Very light gray
            '#cbd5e1',  # 极浅灰 | Extremely light gray
            '#e2e8f0',  # 近白 | Near white
            '#f1f5f9'   # 白色 | White
        ]
    else:
        raise ValueError(f"Unknown style: {style}. Supported styles: 'realistic', 'artistic', 'scientific'")
    
    return LinearSegmentedColormap.from_list(f'terrain_{style}', colors)


def apply_color_mapping(values: np.ndarray, 
                       colormap: Union[str, ColorMapper] = 'terrain',
                       vmin: Optional[float] = None, 
                       vmax: Optional[float] = None,
                       alpha: Optional[float] = None) -> np.ndarray:
    """
    应用颜色映射到数值数组 | Apply color mapping to value array
    
    Args:
        values: 输入数值数组 | Input value array
        colormap: 颜色映射 | Colormap
        vmin: 最小值 | Minimum value
        vmax: 最大值 | Maximum value
        alpha: 透明度 | Alpha transparency
        
    Returns:
        RGBA颜色数组 | RGBA color array
    """
    if isinstance(colormap, str):
        mapper = ColorMapper(colormap, vmin=vmin, vmax=vmax)
    elif isinstance(colormap, ColorMapper):
        mapper = colormap
        if vmin is not None or vmax is not None:
            mapper.update_range(vmin or mapper.normalizer.vmin, 
                              vmax or mapper.normalizer.vmax)
    else:
        raise TypeError("colormap must be a string or ColorMapper instance")
    
    return mapper.map_values(values, alpha=alpha)


def create_categorical_colormap(categories: List[str], 
                               colors: Optional[List[str]] = None,
                               name: str = 'categorical') -> Tuple[ListedColormap, Dict[str, int]]:
    """
    创建分类颜色映射 | Create categorical colormap
    
    Args:
        categories: 类别列表 | Category list
        colors: 颜色列表 | Color list
        name: 颜色映射名称 | Colormap name
        
    Returns:
        (颜色映射, 类别索引字典) | (Colormap, category index dictionary)
    """
    n_categories = len(categories)
    
    if colors is None:
        # 使用默认颜色序列 | Use default color sequence
        if n_categories <= 10:
            colors = plt.cm.tab10(np.linspace(0, 1, n_categories))
        elif n_categories <= 20:
            colors = plt.cm.tab20(np.linspace(0, 1, n_categories))
        else:
            # 对于更多类别，使用HSV颜色空间 | For more categories, use HSV color space
            hues = np.linspace(0, 1, n_categories, endpoint=False)
            colors = [mcolors.hsv_to_rgb([h, 0.8, 0.9]) for h in hues]
    
    # 创建颜色映射和索引字典 | Create colormap and index dictionary
    cmap = ListedColormap(colors, name=name)
    category_indices = {cat: i for i, cat in enumerate(categories)}
    
    return cmap, category_indices


def analyze_color_distribution(values: np.ndarray, 
                              colormap: Union[str, ColorMapper] = 'terrain',
                              n_bins: int = 50) -> Dict[str, Any]:
    """
    分析颜色分布 | Analyze color distribution
    
    Args:
        values: 数值数组 | Value array
        colormap: 颜色映射 | Colormap
        n_bins: 直方图箱数 | Number of histogram bins
        
    Returns:
        分析结果字典 | Analysis result dictionary
    """
    # 过滤有效值 | Filter valid values
    valid_values = values[~np.isnan(values)]
    
    if len(valid_values) == 0:
        return {'error': 'No valid values found'}
    
    # 基本统计 | Basic statistics
    stats = {
        'count': len(valid_values),
        'min': np.min(valid_values),
        'max': np.max(valid_values),
        'mean': np.mean(valid_values),
        'std': np.std(valid_values),
        'median': np.median(valid_values),
        'q25': np.percentile(valid_values, 25),
        'q75': np.percentile(valid_values, 75)
    }
    
    # 直方图分析 | Histogram analysis
    hist, bin_edges = np.histogram(valid_values, bins=n_bins)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    # 颜色映射分析 | Colormap analysis
    if isinstance(colormap, str):
        mapper = ColorMapper(colormap)
    else:
        mapper = colormap
    
    mapper.auto_range(valid_values)
    colors = mapper.map_values(bin_centers)
    
    return {
        'statistics': stats,
        'histogram': {
            'counts': hist,
            'bin_edges': bin_edges,
            'bin_centers': bin_centers,
            'colors': colors
        },
        'colormap_info': {
            'name': mapper.name,
            'vmin': mapper.normalizer.vmin,
            'vmax': mapper.normalizer.vmax
        }
    }


def create_elevation_zones_colormap(zone_elevations: List[float], 
                                   zone_colors: Optional[List[str]] = None,
                                   name: str = 'elevation_zones') -> Tuple[ListedColormap, List[float]]:
    """
    创建高程分带颜色映射 | Create elevation zones colormap
    
    Args:
        zone_elevations: 高程分带边界 | Elevation zone boundaries
        zone_colors: 分带颜色 | Zone colors
        name: 颜色映射名称 | Colormap name
        
    Returns:
        (颜色映射, 分带边界) | (Colormap, zone boundaries)
    """
    n_zones = len(zone_elevations) - 1
    
    if zone_colors is None:
        # 默认高程分带颜色 | Default elevation zone colors
        zone_colors = [
            '#0066CC',  # 水体 | Water
            '#00AA00',  # 低地 | Lowland
            '#66CC00',  # 丘陵 | Hills
            '#CCCC00',  # 低山 | Low mountains
            '#CC6600',  # 中山 | Medium mountains
            '#CC0000',  # 高山 | High mountains
            '#FFFFFF'   # 极高山 | Very high mountains
        ][:n_zones]
    
    if len(zone_colors) != n_zones:
        raise ValueError(f"Number of colors ({len(zone_colors)}) must match number of zones ({n_zones})")
    
    # 创建分带颜色映射 | Create zoned colormap
    cmap = ListedColormap(zone_colors, name=name)
    
    return cmap, zone_elevations


def blend_colormaps(cmap1: Union[str, LinearSegmentedColormap], 
                   cmap2: Union[str, LinearSegmentedColormap],
                   ratio: float = 0.5,
                   name: str = 'blended') -> LinearSegmentedColormap:
    """
    混合两个颜色映射 | Blend two colormaps
    
    Args:
        cmap1: 第一个颜色映射 | First colormap
        cmap2: 第二个颜色映射 | Second colormap
        ratio: 混合比例 | Blend ratio (0=cmap1, 1=cmap2)
        name: 新颜色映射名称 | New colormap name
        
    Returns:
        混合后的颜色映射 | Blended colormap
    """
    # 获取颜色映射对象 | Get colormap objects
    if isinstance(cmap1, str):
        cmap1 = plt.get_cmap(cmap1)
    if isinstance(cmap2, str):
        cmap2 = plt.get_cmap(cmap2)
    
    # 生成混合颜色 | Generate blended colors
    n_colors = 256
    x = np.linspace(0, 1, n_colors)
    
    colors1 = cmap1(x)
    colors2 = cmap2(x)
    
    # 线性混合 | Linear blending
    blended_colors = (1 - ratio) * colors1 + ratio * colors2
    
    # 创建新的颜色映射 | Create new colormap
    return LinearSegmentedColormap.from_list(name, blended_colors)