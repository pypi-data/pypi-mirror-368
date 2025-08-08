"""
PyMountain渲染器基类模块 | PyMountain renderer base class module

定义了渲染器的抽象基类和通用接口 | Defines abstract base class and common interfaces for renderers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple, List, Union
import numpy as np
from .data import MountainData


class BaseRenderer(ABC):
    """
    渲染器抽象基类 | Abstract base class for renderers
    
    定义了所有渲染器必须实现的基本接口 | Defines basic interfaces that all renderers must implement
    
    Attributes:
        config: 渲染器配置参数 | Renderer configuration parameters
        is_interactive: 是否支持交互 | Whether interactive mode is supported
        update_interval_ms: 更新间隔（毫秒） | Update interval in milliseconds
        _current_data: 当前渲染的数据 | Currently rendered data
        _figure: 图形对象 | Figure object
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, 
                 is_interactive: bool = False, 
                 update_interval_ms: int = 100):
        """
        初始化渲染器 | Initialize renderer
        
        Args:
            config: 渲染器配置参数 | Renderer configuration parameters
            is_interactive: 是否启用交互模式 | Whether to enable interactive mode
            update_interval_ms: 更新间隔（毫秒） | Update interval in milliseconds
        """
        self.config: Dict[str, Any] = config or {}
        self.is_interactive: bool = is_interactive
        self.update_interval_ms: int = update_interval_ms
        self._current_data: Optional[MountainData] = None
        self._figure: Optional[Any] = None
        
        # 设置默认配置 | Set default configuration
        self._set_default_config()
        
        # 验证配置 | Validate configuration
        self._validate_config()
    
    def _set_default_config(self) -> None:
        """设置默认配置参数 | Set default configuration parameters"""
        default_config = {
            'figure_size': (10, 8),
            'dpi': 100,
            'title': 'Mountain Terrain Visualization',
            'xlabel': 'X Coordinate',
            'ylabel': 'Y Coordinate',
            'zlabel': 'Elevation (m)',
            'colormap': 'terrain',
            'show_colorbar': True,
            'grid': True,
            'background_color': 'white',
            'font_size': 12,
            'line_width': 1.0,
            'marker_size': 20,
            'alpha': 1.0,
            'interpolation_method': 'linear',
            'grid_resolution': 100
        }
        
        # 合并用户配置和默认配置 | Merge user config with default config
        for key, value in default_config.items():
            if key not in self.config:
                self.config[key] = value
    
    def _validate_config(self) -> None:
        """验证配置参数的有效性 | Validate configuration parameters"""
        # 验证数值参数 | Validate numeric parameters
        numeric_params = {
            'dpi': (50, 500),
            'font_size': (6, 24),
            'line_width': (0.1, 10.0),
            'marker_size': (1, 200),
            'alpha': (0.0, 1.0),
            'grid_resolution': (10, 1000),
            'update_interval_ms': (10, 10000)
        }
        
        for param, (min_val, max_val) in numeric_params.items():
            if param in self.config:
                value = self.config[param]
                if not isinstance(value, (int, float)) or not min_val <= value <= max_val:
                    raise ValueError(f"{param} must be between {min_val} and {max_val}")
        
        # 验证figure_size | Validate figure_size
        if 'figure_size' in self.config:
            size = self.config['figure_size']
            if not (isinstance(size, (tuple, list)) and len(size) == 2 and 
                   all(isinstance(x, (int, float)) and x > 0 for x in size)):
                raise ValueError("figure_size must be a tuple/list of two positive numbers")
        
        # 验证插值方法 | Validate interpolation method
        if 'interpolation_method' in self.config:
            valid_methods = ['linear', 'cubic', 'rbf']
            if self.config['interpolation_method'] not in valid_methods:
                raise ValueError(f"interpolation_method must be one of {valid_methods}")
    
    @abstractmethod
    def render(self, data: MountainData, **kwargs) -> Any:
        """
        渲染山体数据 | Render mountain data
        
        Args:
            data: 山体数据对象 | Mountain data object
            **kwargs: 额外的渲染参数 | Additional rendering parameters
            
        Returns:
            渲染结果对象 | Rendering result object
        """
        pass
    
    @abstractmethod
    def update(self, data: MountainData, **kwargs) -> None:
        """
        更新渲染内容 | Update rendered content
        
        Args:
            data: 新的山体数据 | New mountain data
            **kwargs: 额外的更新参数 | Additional update parameters
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """清除渲染内容 | Clear rendered content"""
        pass
    
    def set_config(self, **kwargs) -> None:
        """
        设置配置参数 | Set configuration parameters
        
        Args:
            **kwargs: 配置参数键值对 | Configuration parameter key-value pairs
        """
        self.config.update(kwargs)
        self._validate_config()
    
    def get_config(self, key: Optional[str] = None) -> Union[Any, Dict[str, Any]]:
        """
        获取配置参数 | Get configuration parameters
        
        Args:
            key: 配置参数键（可选） | Configuration parameter key (optional)
            
        Returns:
            配置参数值或完整配置字典 | Configuration parameter value or complete config dict
        """
        if key is None:
            return self.config.copy()
        return self.config.get(key)
    
    def save_figure(self, filepath: str, **kwargs) -> None:
        """
        保存图形到文件 | Save figure to file
        
        Args:
            filepath: 文件路径 | File path
            **kwargs: 保存参数 | Save parameters
            
        Raises:
            NotImplementedError: 子类未实现此方法 | Subclass has not implemented this method
        """
        raise NotImplementedError("Subclass must implement save_figure method")
    
    def show(self) -> None:
        """
        显示图形 | Show figure
        
        Raises:
            NotImplementedError: 子类未实现此方法 | Subclass has not implemented this method
        """
        raise NotImplementedError("Subclass must implement show method")
    
    def close(self) -> None:
        """
        关闭图形 | Close figure
        
        Raises:
            NotImplementedError: 子类未实现此方法 | Subclass has not implemented this method
        """
        raise NotImplementedError("Subclass must implement close method")
    
    def get_current_data(self) -> Optional[MountainData]:
        """
        获取当前渲染的数据 | Get currently rendered data
        
        Returns:
            当前数据对象或None | Current data object or None
        """
        return self._current_data
    
    def get_figure(self) -> Optional[Any]:
        """
        获取图形对象 | Get figure object
        
        Returns:
            图形对象或None | Figure object or None
        """
        return self._figure
    
    def set_interactive_mode(self, enabled: bool) -> None:
        """
        设置交互模式 | Set interactive mode
        
        Args:
            enabled: 是否启用交互模式 | Whether to enable interactive mode
        """
        self.is_interactive = enabled
    
    def set_update_interval(self, interval_ms: int) -> None:
        """
        设置更新间隔 | Set update interval
        
        Args:
            interval_ms: 更新间隔（毫秒） | Update interval in milliseconds
        """
        if not isinstance(interval_ms, int) or interval_ms < 10:
            raise ValueError("Update interval must be an integer >= 10 milliseconds")
        self.update_interval_ms = interval_ms
    
    def get_supported_formats(self) -> List[str]:
        """
        获取支持的文件格式 | Get supported file formats
        
        Returns:
            支持的格式列表 | List of supported formats
        """
        return ['png', 'jpg', 'pdf', 'svg']
    
    def get_renderer_info(self) -> Dict[str, Any]:
        """
        获取渲染器信息 | Get renderer information
        
        Returns:
            渲染器信息字典 | Renderer information dictionary
        """
        return {
            'name': self.__class__.__name__,
            'is_interactive': self.is_interactive,
            'update_interval_ms': self.update_interval_ms,
            'supported_formats': self.get_supported_formats(),
            'config': self.config.copy()
        }
    
    def _prepare_data_for_rendering(self, data: MountainData) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        为渲染准备数据 | Prepare data for rendering
        
        Args:
            data: 山体数据对象 | Mountain data object
            
        Returns:
            (x, y, z)数组元组 | (x, y, z) array tuple
            
        Raises:
            ValueError: 数据为空 | Data is empty
        """
        if len(data) == 0:
            raise ValueError("Cannot render empty data")
        
        x, y, z = data.to_numpy_arrays()
        
        # 验证数据有效性 | Validate data validity
        if np.any(np.isnan(x)) or np.any(np.isnan(y)) or np.any(np.isnan(z)):
            raise ValueError("Data contains NaN values")
        
        if np.any(np.isinf(x)) or np.any(np.isinf(y)) or np.any(np.isinf(z)):
            raise ValueError("Data contains infinite values")
        
        return x, y, z
    
    def _create_interpolated_grid(self, x: np.ndarray, y: np.ndarray, z: np.ndarray, 
                                 resolution: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        创建插值网格 | Create interpolated grid
        
        Args:
            x: X坐标数组 | X coordinate array
            y: Y坐标数组 | Y coordinate array
            z: Z坐标数组 | Z coordinate array
            resolution: 网格分辨率 | Grid resolution
            
        Returns:
            (X_grid, Y_grid, Z_grid)网格元组 | (X_grid, Y_grid, Z_grid) grid tuple
        """
        if resolution is None:
            resolution = self.config.get('grid_resolution', 100)
        
        # 创建网格 | Create grid
        x_min, x_max = np.min(x), np.max(x)
        y_min, y_max = np.min(y), np.max(y)
        
        xi = np.linspace(x_min, x_max, resolution)
        yi = np.linspace(y_min, y_max, resolution)
        X_grid, Y_grid = np.meshgrid(xi, yi)
        
        # 插值计算 | Interpolation calculation
        from scipy.interpolate import griddata
        
        method = self.config.get('interpolation_method', 'linear')
        if method == 'rbf':
            method = 'cubic'  # griddata doesn't support rbf, use cubic instead
        
        points = np.column_stack((x, y))
        Z_grid = griddata(points, z, (X_grid, Y_grid), method=method, fill_value=np.nan)
        
        return X_grid, Y_grid, Z_grid
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(interactive={self.is_interactive}, interval={self.update_interval_ms}ms)"
    
    def __repr__(self) -> str:
        return self.__str__()


class RenderingError(Exception):
    """渲染错误异常类 | Rendering error exception class"""
    pass


class ConfigurationError(Exception):
    """配置错误异常类 | Configuration error exception class"""
    pass