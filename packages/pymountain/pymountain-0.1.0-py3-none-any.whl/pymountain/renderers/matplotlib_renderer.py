"""
PyMountain Matplotlib渲染器模块 | PyMountain Matplotlib renderer module

基于Matplotlib的山体地形数据渲染器实现 | Matplotlib-based mountain terrain data renderer implementations
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import Normalize
from mpl_toolkits.mplot3d import Axes3D
from typing import Dict, Any, Optional, Tuple, Union
import warnings

from ..core.renderer import BaseRenderer, RenderingError
from ..core.data import MountainData


class MatplotlibRenderer(BaseRenderer):
    """
    Matplotlib基础渲染器 | Matplotlib base renderer
    
    提供基于Matplotlib的通用渲染功能 | Provides common rendering functionality based on Matplotlib
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, 
                 is_interactive: bool = False, 
                 update_interval_ms: int = 100):
        """初始化Matplotlib渲染器 | Initialize Matplotlib renderer"""
        super().__init__(config, is_interactive, update_interval_ms)
        
        # Matplotlib特定配置 | Matplotlib-specific configuration
        self._set_matplotlib_defaults()
        
        # 图形对象 | Figure objects
        self._fig = None
        self._ax = None
        
        # 渲染对象缓存 | Rendering object cache
        self._plot_objects = []
        self._colorbar = None
    
    def _set_matplotlib_defaults(self) -> None:
        """设置Matplotlib特定的默认配置 | Set Matplotlib-specific default configuration"""
        matplotlib_defaults = {
            'style': 'default',
            'tight_layout': True,
            'show_axes': True,
            'show_grid': True,
            'grid_alpha': 0.3,
            'colorbar_shrink': 0.8,
            'colorbar_aspect': 20,
            'colorbar_pad': 0.1,
        }
        
        for key, value in matplotlib_defaults.items():
            if key not in self.config:
                self.config[key] = value
    
    def _setup_figure(self, projection: Optional[str] = None) -> Tuple[plt.Figure, plt.Axes]:
        """
        设置图形和坐标轴 | Setup figure and axes
        
        Args:
            projection: 投影类型 | Projection type
            
        Returns:
            (figure, axes)元组 | (figure, axes) tuple
        """
        # 创建图形 | Create figure
        fig_size = self.config.get('figure_size', (10, 8))
        dpi = self.config.get('dpi', 100)
        
        self._fig = plt.figure(figsize=fig_size, dpi=dpi)
        
        # 创建坐标轴 | Create axes
        if projection:
            self._ax = self._fig.add_subplot(111, projection=projection)
        else:
            self._ax = self._fig.add_subplot(111)
        
        # 设置样式 | Set style
        if self.config.get('style') != 'default':
            plt.style.use(self.config['style'])
        
        # 设置背景色 | Set background color
        bg_color = self.config.get('background_color', 'white')
        self._fig.patch.set_facecolor(bg_color)
        self._ax.set_facecolor(bg_color)
        
        return self._fig, self._ax
    
    def _setup_labels_and_title(self) -> None:
        """设置标签和标题 | Setup labels and title"""
        font_size = self.config.get('font_size', 12)
        
        # 设置标题 | Set title
        title = self.config.get('title', 'Mountain Terrain Visualization')
        self._ax.set_title(title, fontsize=font_size + 2, fontweight='bold')
        
        # 设置坐标轴标签 | Set axis labels
        xlabel = self.config.get('xlabel', 'X Coordinate')
        ylabel = self.config.get('ylabel', 'Y Coordinate')
        
        self._ax.set_xlabel(xlabel, fontsize=font_size)
        self._ax.set_ylabel(ylabel, fontsize=font_size)
        
        # 3D图形的Z轴标签 | Z-axis label for 3D plots
        if hasattr(self._ax, 'set_zlabel'):
            zlabel = self.config.get('zlabel', 'Elevation (m)')
            self._ax.set_zlabel(zlabel, fontsize=font_size)
    
    def _setup_grid(self) -> None:
        """设置网格 | Setup grid"""
        if self.config.get('show_grid', True):
            grid_alpha = self.config.get('grid_alpha', 0.3)
            self._ax.grid(True, alpha=grid_alpha)
    
    def _add_colorbar(self, mappable, label: str = 'Elevation (m)') -> None:
        """
        添加颜色条 | Add colorbar
        
        Args:
            mappable: 可映射对象 | Mappable object
            label: 颜色条标签 | Colorbar label
        """
        if self.config.get('show_colorbar', True):
            shrink = self.config.get('colorbar_shrink', 0.8)
            aspect = self.config.get('colorbar_aspect', 20)
            pad = self.config.get('colorbar_pad', 0.1)
            
            self._colorbar = self._fig.colorbar(
                mappable, ax=self._ax, shrink=shrink, aspect=aspect, pad=pad
            )
            self._colorbar.set_label(label, fontsize=self.config.get('font_size', 12))
    
    def render(self, data: MountainData, **kwargs) -> plt.Figure:
        """
        渲染山体数据 | Render mountain data
        
        Args:
            data: 山体数据对象 | Mountain data object
            **kwargs: 额外的渲染参数 | Additional rendering parameters
            
        Returns:
            Matplotlib图形对象 | Matplotlib figure object
        """
        # 更新配置 | Update configuration
        if kwargs:
            self.set_config(**kwargs)
        
        # 准备数据 | Prepare data
        try:
            x, y, z = self._prepare_data_for_rendering(data)
        except ValueError as e:
            raise RenderingError(f"Data preparation failed: {e}")
        
        # 存储当前数据 | Store current data
        self._current_data = data
        
        # 子类实现具体渲染逻辑 | Subclass implements specific rendering logic
        return self._render_implementation(x, y, z)
    
    def _render_implementation(self, x: np.ndarray, y: np.ndarray, z: np.ndarray) -> plt.Figure:
        """
        具体的渲染实现（由子类重写） | Specific rendering implementation (overridden by subclasses)
        
        Args:
            x: X坐标数组 | X coordinate array
            y: Y坐标数组 | Y coordinate array
            z: Z坐标数组 | Z coordinate array
            
        Returns:
            Matplotlib图形对象 | Matplotlib figure object
        """
        raise NotImplementedError("Subclass must implement _render_implementation")
    
    def update(self, data: MountainData, **kwargs) -> None:
        """
        更新渲染内容 | Update rendered content
        
        Args:
            data: 新的山体数据 | New mountain data
            **kwargs: 额外的更新参数 | Additional update parameters
        """
        if self._fig is None:
            self.render(data, **kwargs)
        else:
            # 清除旧的绘图对象 | Clear old plot objects
            self._clear_plot_objects()
            
            # 重新渲染 | Re-render
            self.render(data, **kwargs)
            
            # 刷新显示 | Refresh display
            if self.is_interactive:
                plt.draw()
    
    def _clear_plot_objects(self) -> None:
        """清除绘图对象 | Clear plot objects"""
        for obj in self._plot_objects:
            if hasattr(obj, 'remove'):
                obj.remove()
        self._plot_objects.clear()
        
        if self._colorbar:
            self._colorbar.remove()
            self._colorbar = None
    
    def clear(self) -> None:
        """清除渲染内容 | Clear rendered content"""
        if self._ax:
            self._ax.clear()
        self._clear_plot_objects()
        self._current_data = None
    
    def save_figure(self, filepath: str, **kwargs) -> None:
        """
        保存图形到文件 | Save figure to file
        
        Args:
            filepath: 文件路径 | File path
            **kwargs: 保存参数 | Save parameters
        """
        if self._fig is None:
            raise RenderingError("No figure to save. Call render() first.")
        
        # 默认保存参数 | Default save parameters
        save_params = {
            'dpi': self.config.get('dpi', 100),
            'bbox_inches': 'tight',
            'facecolor': self.config.get('background_color', 'white'),
            'edgecolor': 'none'
        }
        save_params.update(kwargs)
        
        try:
            self._fig.savefig(filepath, **save_params)
        except Exception as e:
            raise RenderingError(f"Failed to save figure: {e}")
    
    def show(self) -> None:
        """显示图形 | Show figure"""
        if self._fig is None:
            raise RenderingError("No figure to show. Call render() first.")
        
        if self.config.get('tight_layout', True):
            self._fig.tight_layout()
        
        plt.show()
    
    def close(self) -> None:
        """关闭图形 | Close figure"""
        if self._fig:
            plt.close(self._fig)
            self._fig = None
            self._ax = None
        self._clear_plot_objects()
        self._current_data = None
    
    def get_figure(self) -> Optional[plt.Figure]:
        """获取Matplotlib图形对象 | Get Matplotlib figure object"""
        return self._fig
    
    def get_axes(self) -> Optional[plt.Axes]:
        """获取Matplotlib坐标轴对象 | Get Matplotlib axes object"""
        return self._ax


class Matplotlib3DRenderer(MatplotlibRenderer):
    """
    Matplotlib 3D渲染器 | Matplotlib 3D renderer
    
    专门用于3D山体地形可视化 | Specialized for 3D mountain terrain visualization
    """
    
    def _render_implementation(self, x: np.ndarray, y: np.ndarray, z: np.ndarray) -> plt.Figure:
        """3D渲染实现 | 3D rendering implementation"""
        # 设置3D图形 | Setup 3D figure
        self._setup_figure(projection='3d')
        
        # 获取渲染参数 | Get rendering parameters
        colormap = self.config.get('colormap', 'terrain')
        alpha = self.config.get('alpha', 1.0)
        marker_size = self.config.get('marker_size', 20)
        
        # 创建颜色映射 | Create color mapping
        norm = Normalize(vmin=np.min(z), vmax=np.max(z))
        colors = cm.get_cmap(colormap)(norm(z))
        
        # 绘制3D散点图 | Plot 3D scatter
        scatter = self._ax.scatter(x, y, z, c=colors, s=marker_size, alpha=alpha)
        self._plot_objects.append(scatter)
        
        # 如果数据点足够多，创建表面图 | Create surface plot if enough data points
        if len(x) > 10 and self.config.get('show_surface', True):
            try:
                X_grid, Y_grid, Z_grid = self._create_interpolated_grid(x, y, z)
                
                # 过滤无效值 | Filter invalid values
                mask = ~np.isnan(Z_grid)
                if np.any(mask):
                    surface = self._ax.plot_surface(
                        X_grid, Y_grid, Z_grid,
                        cmap=colormap,
                        alpha=alpha * 0.7,
                        linewidth=0,
                        antialiased=True
                    )
                    self._plot_objects.append(surface)
            except Exception as e:
                warnings.warn(f"Surface plotting failed: {e}")
        
        # 设置标签和标题 | Setup labels and title
        self._setup_labels_and_title()
        
        # 设置网格 | Setup grid
        self._setup_grid()
        
        # 添加颜色条 | Add colorbar
        self._add_colorbar(scatter)
        
        # 设置视角 | Set viewing angle
        elev = self.config.get('elevation_angle', 30)
        azim = self.config.get('azimuth_angle', 45)
        self._ax.view_init(elev=elev, azim=azim)
        
        # 设置坐标轴比例 | Set axis aspect ratio
        if self.config.get('equal_aspect', False):
            self._ax.set_box_aspect([1,1,0.5])
        
        return self._fig


class MatplotlibContourRenderer(MatplotlibRenderer):
    """
    Matplotlib等高线渲染器 | Matplotlib contour renderer
    
    专门用于等高线地形可视化 | Specialized for contour terrain visualization
    """
    
    def _render_implementation(self, x: np.ndarray, y: np.ndarray, z: np.ndarray) -> plt.Figure:
        """等高线渲染实现 | Contour rendering implementation"""
        # 设置2D图形 | Setup 2D figure
        self._setup_figure()
        
        # 创建插值网格 | Create interpolated grid
        try:
            X_grid, Y_grid, Z_grid = self._create_interpolated_grid(x, y, z)
        except Exception as e:
            raise RenderingError(f"Grid interpolation failed: {e}")
        
        # 获取渲染参数 | Get rendering parameters
        colormap = self.config.get('colormap', 'terrain')
        num_levels = self.config.get('contour_levels', 20)
        
        # 创建等高线级别 | Create contour levels
        z_min, z_max = np.nanmin(Z_grid), np.nanmax(Z_grid)
        if isinstance(num_levels, int):
            levels = np.linspace(z_min, z_max, num_levels)
        else:
            levels = num_levels
        
        # 绘制填充等高线 | Plot filled contours
        if self.config.get('filled_contours', True):
            contourf = self._ax.contourf(X_grid, Y_grid, Z_grid, levels=levels, cmap=colormap)
            self._plot_objects.append(contourf)
            
            # 添加颜色条 | Add colorbar
            self._add_colorbar(contourf)
        
        # 绘制等高线 | Plot contour lines
        if self.config.get('show_contour_lines', True):
            line_color = self.config.get('contour_line_color', 'black')
            line_width = self.config.get('line_width', 1.0)
            line_alpha = self.config.get('contour_line_alpha', 0.5)
            
            contour = self._ax.contour(
                X_grid, Y_grid, Z_grid, 
                levels=levels, 
                colors=line_color, 
                linewidths=line_width,
                alpha=line_alpha
            )
            self._plot_objects.append(contour)
            
            # 添加等高线标签 | Add contour labels
            if self.config.get('show_contour_labels', True):
                label_fontsize = self.config.get('font_size', 12) - 2
                self._ax.clabel(contour, inline=True, fontsize=label_fontsize, fmt='%.0f')
        
        # 绘制原始数据点 | Plot original data points
        if self.config.get('show_data_points', True):
            marker_size = self.config.get('marker_size', 20)
            marker_color = self.config.get('data_point_color', 'red')
            marker_alpha = self.config.get('data_point_alpha', 0.8)
            
            scatter = self._ax.scatter(
                x, y, 
                s=marker_size, 
                c=marker_color, 
                alpha=marker_alpha,
                edgecolors='black',
                linewidth=0.5,
                zorder=10
            )
            self._plot_objects.append(scatter)
        
        # 设置标签和标题 | Setup labels and title
        self._setup_labels_and_title()
        
        # 设置网格 | Setup grid
        self._setup_grid()
        
        # 设置坐标轴比例 | Set axis aspect ratio
        if self.config.get('equal_aspect', True):
            self._ax.set_aspect('equal')
        
        return self._fig


# 为了向后兼容，提供一个通用的MatplotlibRenderer别名 | For backward compatibility, provide a generic MatplotlibRenderer alias
class MatplotlibRenderer(Matplotlib3DRenderer):
    """
    通用Matplotlib渲染器（默认为3D模式） | Generic Matplotlib renderer (defaults to 3D mode)
    
    这是一个便捷类，默认使用3D渲染模式 | This is a convenience class that defaults to 3D rendering mode
    """
    pass