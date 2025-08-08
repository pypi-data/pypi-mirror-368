"""
PyMountain核心数据模块 | PyMountain core data module

定义了山体地形数据的基础数据结构和管理类 | Defines basic data structures and management classes for mountain terrain data
"""

import numpy as np
from typing import List, Tuple, Optional, Union, Dict, Any, Iterator
from dataclasses import dataclass, field
import copy
import json
from pathlib import Path


@dataclass
class BasePoint:
    """
    山体地形数据点的基础类 | Base class for mountain terrain data points
    
    表示三维空间中的一个点，包含坐标和高程信息 | Represents a point in 3D space with coordinates and elevation
    
    Attributes:
        x: X坐标 | X coordinate
        y: Y坐标 | Y coordinate  
        z: Z坐标（高程） | Z coordinate (elevation)
        metadata: 附加元数据字典 | Additional metadata dictionary
    """
    
    x: float
    y: float
    z: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化后验证数据 | Post-initialization data validation"""
        if not all(isinstance(coord, (int, float)) for coord in [self.x, self.y, self.z]):
            raise TypeError("Coordinates must be numeric values")
        
        # 转换为float确保数值精度 | Convert to float for numerical precision
        self.x = float(self.x)
        self.y = float(self.y)
        self.z = float(self.z)
    
    def distance_to(self, other: 'BasePoint') -> float:
        """
        计算到另一个点的欧几里得距离 | Calculate Euclidean distance to another point
        
        Args:
            other: 目标点 | Target point
            
        Returns:
            距离值 | Distance value
        """
        return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)
    
    def distance_2d(self, other: 'BasePoint') -> float:
        """
        计算到另一个点的2D距离（忽略高程） | Calculate 2D distance to another point (ignoring elevation)
        
        Args:
            other: 目标点 | Target point
            
        Returns:
            2D距离值 | 2D distance value
        """
        return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def to_tuple(self) -> Tuple[float, float, float]:
        """
        转换为元组格式 | Convert to tuple format
        
        Returns:
            (x, y, z)元组 | (x, y, z) tuple
        """
        return (self.x, self.y, self.z)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式 | Convert to dictionary format
        
        Returns:
            包含点数据的字典 | Dictionary containing point data
        """
        return {
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BasePoint':
        """
        从字典创建点对象 | Create point object from dictionary
        
        Args:
            data: 包含点数据的字典 | Dictionary containing point data
            
        Returns:
            BasePoint实例 | BasePoint instance
        """
        return cls(
            x=data['x'],
            y=data['y'],
            z=data['z'],
            metadata=data.get('metadata', {})
        )
    
    def copy(self) -> 'BasePoint':
        """
        创建点的深拷贝 | Create deep copy of the point
        
        Returns:
            新的BasePoint实例 | New BasePoint instance
        """
        return BasePoint(
            x=self.x,
            y=self.y,
            z=self.z,
            metadata=copy.deepcopy(self.metadata)
        )
    
    def __str__(self) -> str:
        return f"BasePoint(x={self.x:.3f}, y={self.y:.3f}, z={self.z:.3f})"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, BasePoint):
            return False
        return (np.isclose(self.x, other.x) and 
                np.isclose(self.y, other.y) and 
                np.isclose(self.z, other.z))
    
    def __hash__(self) -> int:
        return hash((round(self.x, 6), round(self.y, 6), round(self.z, 6)))


class MountainData:
    """
    山体地形数据管理类 | Mountain terrain data management class
    
    负责存储、管理和操作山体地形数据点集合 | Responsible for storing, managing and operating mountain terrain data point collections
    
    Attributes:
        points: 数据点列表 | List of data points
        metadata: 数据集元数据 | Dataset metadata
        _bounds_cache: 边界缓存 | Bounds cache
        _grid_cache: 网格缓存 | Grid cache
    """
    
    def __init__(self, points: Optional[List[BasePoint]] = None, metadata: Optional[Dict[str, Any]] = None):
        """
        初始化山体数据对象 | Initialize mountain data object
        
        Args:
            points: 初始数据点列表 | Initial list of data points
            metadata: 数据集元数据 | Dataset metadata
        """
        self.points: List[BasePoint] = points or []
        self.metadata: Dict[str, Any] = metadata or {}
        self._bounds_cache: Optional[Dict[str, float]] = None
        self._grid_cache: Optional[Dict[str, Any]] = None
        
        # 验证初始数据 | Validate initial data
        if self.points:
            self._validate_points()
    
    def _validate_points(self) -> None:
        """验证数据点的有效性 | Validate data points"""
        if not all(isinstance(point, BasePoint) for point in self.points):
            raise TypeError("All points must be BasePoint instances")
    
    def _clear_cache(self) -> None:
        """清除缓存数据 | Clear cached data"""
        self._bounds_cache = None
        self._grid_cache = None
    
    def add_point(self, x: float, y: float, z: float, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        添加新的数据点 | Add new data point
        
        Args:
            x: X坐标 | X coordinate
            y: Y坐标 | Y coordinate
            z: Z坐标（高程） | Z coordinate (elevation)
            metadata: 点的元数据 | Point metadata
        """
        point = BasePoint(x=x, y=y, z=z, metadata=metadata or {})
        self.points.append(point)
        self._clear_cache()
    
    def add_point_object(self, point: BasePoint) -> None:
        """
        添加BasePoint对象 | Add BasePoint object
        
        Args:
            point: BasePoint实例 | BasePoint instance
        """
        if not isinstance(point, BasePoint):
            raise TypeError("Point must be a BasePoint instance")
        self.points.append(point)
        self._clear_cache()
    
    def remove_point(self, index: int) -> BasePoint:
        """
        移除指定索引的数据点 | Remove data point at specified index
        
        Args:
            index: 点的索引 | Point index
            
        Returns:
            被移除的点 | Removed point
            
        Raises:
            IndexError: 索引超出范围 | Index out of range
        """
        if not 0 <= index < len(self.points):
            raise IndexError(f"Point index {index} out of range")
        
        removed_point = self.points.pop(index)
        self._clear_cache()
        return removed_point
    
    def update_point(self, index: int, x: Optional[float] = None, y: Optional[float] = None, 
                    z: Optional[float] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        更新指定索引的数据点 | Update data point at specified index
        
        Args:
            index: 点的索引 | Point index
            x: 新的X坐标（可选） | New X coordinate (optional)
            y: 新的Y坐标（可选） | New Y coordinate (optional)
            z: 新的Z坐标（可选） | New Z coordinate (optional)
            metadata: 新的元数据（可选） | New metadata (optional)
            
        Raises:
            IndexError: 索引超出范围 | Index out of range
        """
        if not 0 <= index < len(self.points):
            raise IndexError(f"Point index {index} out of range")
        
        point = self.points[index]
        if x is not None:
            point.x = float(x)
        if y is not None:
            point.y = float(y)
        if z is not None:
            point.z = float(z)
        if metadata is not None:
            point.metadata.update(metadata)
        
        self._clear_cache()
    
    def get_bounds(self) -> Dict[str, float]:
        """
        获取数据边界 | Get data bounds
        
        Returns:
            包含min_x, max_x, min_y, max_y, min_z, max_z的字典 | Dictionary containing bounds
        """
        if self._bounds_cache is not None:
            return self._bounds_cache
        
        if not self.points:
            return {'min_x': 0, 'max_x': 0, 'min_y': 0, 'max_y': 0, 'min_z': 0, 'max_z': 0}
        
        x_coords = [p.x for p in self.points]
        y_coords = [p.y for p in self.points]
        z_coords = [p.z for p in self.points]
        
        self._bounds_cache = {
            'min_x': min(x_coords),
            'max_x': max(x_coords),
            'min_y': min(y_coords),
            'max_y': max(y_coords),
            'min_z': min(z_coords),
            'max_z': max(z_coords)
        }
        
        return self._bounds_cache
    
    def get_points_in_region(self, min_x: float, max_x: float, min_y: float, max_y: float) -> List[BasePoint]:
        """
        获取指定区域内的数据点 | Get data points within specified region
        
        Args:
            min_x: 最小X坐标 | Minimum X coordinate
            max_x: 最大X坐标 | Maximum X coordinate
            min_y: 最小Y坐标 | Minimum Y coordinate
            max_y: 最大Y坐标 | Maximum Y coordinate
            
        Returns:
            区域内的点列表 | List of points in region
        """
        return [p for p in self.points 
                if min_x <= p.x <= max_x and min_y <= p.y <= max_y]
    
    def get_elevation_stats(self) -> Dict[str, float]:
        """
        获取高程统计信息 | Get elevation statistics
        
        Returns:
            包含统计信息的字典 | Dictionary containing statistics
        """
        if not self.points:
            return {'min': 0, 'max': 0, 'mean': 0, 'std': 0, 'count': 0}
        
        elevations = np.array([p.z for p in self.points])
        
        return {
            'min': float(np.min(elevations)),
            'max': float(np.max(elevations)),
            'mean': float(np.mean(elevations)),
            'std': float(np.std(elevations)),
            'count': len(elevations)
        }
    
    def to_numpy_arrays(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        转换为NumPy数组格式 | Convert to NumPy array format
        
        Returns:
            (x_array, y_array, z_array)元组 | (x_array, y_array, z_array) tuple
        """
        if not self.points:
            return np.array([]), np.array([]), np.array([])
        
        x_coords = np.array([p.x for p in self.points])
        y_coords = np.array([p.y for p in self.points])
        z_coords = np.array([p.z for p in self.points])
        
        return x_coords, y_coords, z_coords
    
    def load_from_arrays(self, x_array: np.ndarray, y_array: np.ndarray, z_array: np.ndarray, 
                        clear_existing: bool = True) -> None:
        """
        从NumPy数组加载数据 | Load data from NumPy arrays
        
        Args:
            x_array: X坐标数组 | X coordinate array
            y_array: Y坐标数组 | Y coordinate array
            z_array: Z坐标数组 | Z coordinate array
            clear_existing: 是否清除现有数据 | Whether to clear existing data
        """
        if len(x_array) != len(y_array) or len(y_array) != len(z_array):
            raise ValueError("All arrays must have the same length")
        
        if clear_existing:
            self.points.clear()
        
        for x, y, z in zip(x_array, y_array, z_array):
            self.add_point(float(x), float(y), float(z))
    
    def load_from_dataframe(self, df, x_col: str = 'x', y_col: str = 'y', z_col: str = 'z', 
                           clear_existing: bool = True) -> None:
        """
        从pandas DataFrame加载数据 | Load data from pandas DataFrame
        
        Args:
            df: pandas DataFrame对象 | pandas DataFrame object
            x_col: X坐标列名 | X coordinate column name
            y_col: Y坐标列名 | Y coordinate column name
            z_col: Z坐标列名 | Z coordinate column name
            clear_existing: 是否清除现有数据 | Whether to clear existing data
            
        Raises:
            ImportError: pandas未安装 | pandas not installed
            KeyError: 指定列不存在 | Specified column does not exist
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required for DataFrame loading. Install with: pip install pandas")
        
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame")
        
        required_cols = [x_col, y_col, z_col]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise KeyError(f"Missing columns: {missing_cols}")
        
        if clear_existing:
            self.points.clear()
        
        for _, row in df.iterrows():
            self.add_point(float(row[x_col]), float(row[y_col]), float(row[z_col]))
    
    def to_json(self, filepath: Optional[Union[str, Path]] = None) -> Union[str, None]:
        """
        导出为JSON格式 | Export to JSON format
        
        Args:
            filepath: 文件路径（可选） | File path (optional)
            
        Returns:
            JSON字符串（如果未指定文件路径） | JSON string (if no filepath specified)
        """
        data = {
            'metadata': self.metadata,
            'points': [point.to_dict() for point in self.points]
        }
        
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json_str)
            return None
        else:
            return json_str
    
    def load_from_json(self, data: Union[str, Path, Dict[str, Any]], clear_existing: bool = True) -> None:
        """
        从JSON格式加载数据 | Load data from JSON format
        
        Args:
            data: JSON字符串、文件路径或字典 | JSON string, file path, or dictionary
            clear_existing: 是否清除现有数据 | Whether to clear existing data
        """
        if isinstance(data, (str, Path)):
            # 判断是文件路径还是JSON字符串 | Determine if it's a file path or JSON string
            if Path(data).exists():
                with open(data, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
            else:
                json_data = json.loads(data)
        elif isinstance(data, dict):
            json_data = data
        else:
            raise TypeError("Data must be a JSON string, file path, or dictionary")
        
        if clear_existing:
            self.points.clear()
        
        # 加载元数据 | Load metadata
        if 'metadata' in json_data:
            self.metadata.update(json_data['metadata'])
        
        # 加载数据点 | Load data points
        if 'points' in json_data:
            for point_data in json_data['points']:
                point = BasePoint.from_dict(point_data)
                self.add_point_object(point)
    
    def copy(self) -> 'MountainData':
        """
        创建数据的深拷贝 | Create deep copy of the data
        
        Returns:
            新的MountainData实例 | New MountainData instance
        """
        new_points = [point.copy() for point in self.points]
        new_metadata = copy.deepcopy(self.metadata)
        return MountainData(points=new_points, metadata=new_metadata)
    
    def clear(self) -> None:
        """清除所有数据点 | Clear all data points"""
        self.points.clear()
        self._clear_cache()
    
    def __len__(self) -> int:
        return len(self.points)
    
    def __getitem__(self, index: int) -> BasePoint:
        return self.points[index]
    
    def __setitem__(self, index: int, point: BasePoint) -> None:
        if not isinstance(point, BasePoint):
            raise TypeError("Point must be a BasePoint instance")
        self.points[index] = point
        self._clear_cache()
    
    def __iter__(self) -> Iterator[BasePoint]:
        return iter(self.points)
    
    def __str__(self) -> str:
        bounds = self.get_bounds()
        stats = self.get_elevation_stats()
        return (f"MountainData(points={len(self.points)}, "
                f"bounds=({bounds['min_x']:.2f},{bounds['min_y']:.2f}) to ({bounds['max_x']:.2f},{bounds['max_y']:.2f}), "
                f"elevation={stats['min']:.2f}-{stats['max']:.2f}m)")
    
    def __repr__(self) -> str:
        return self.__str__()