"""
PyMountain插值工具模块 | PyMountain interpolation utilities module

提供各种插值算法用于山体地形数据的平滑和重建 | Provides various interpolation algorithms for smoothing and reconstruction of mountain terrain data
"""

import numpy as np
from typing import Tuple, Optional, Union, Callable, Dict
from scipy.interpolate import griddata, interp2d, RBFInterpolator
from scipy.spatial.distance import cdist
import warnings


def linear_interpolation(x: np.ndarray, y: np.ndarray, z: np.ndarray, 
                        xi: np.ndarray, yi: np.ndarray, 
                        fill_value: float = np.nan) -> np.ndarray:
    """
    线性插值 | Linear interpolation
    
    使用线性插值方法对散点数据进行网格插值 | Use linear interpolation method for grid interpolation of scattered data
    
    Args:
        x: 原始X坐标数组 | Original X coordinate array
        y: 原始Y坐标数组 | Original Y coordinate array
        z: 原始Z值数组 | Original Z value array
        xi: 目标X坐标网格 | Target X coordinate grid
        yi: 目标Y坐标网格 | Target Y coordinate grid
        fill_value: 填充值 | Fill value for extrapolation
        
    Returns:
        插值后的Z值网格 | Interpolated Z value grid
        
    Raises:
        ValueError: 输入数据维度不匹配 | Input data dimensions mismatch
    """
    # 验证输入数据 | Validate input data
    if len(x) != len(y) or len(y) != len(z):
        raise ValueError("Input arrays must have the same length")
    
    if len(x) < 3:
        raise ValueError("At least 3 points are required for interpolation")
    
    # 检查重复点 | Check for duplicate points
    points = np.column_stack((x, y))
    unique_points, unique_indices = np.unique(points, axis=0, return_index=True)
    
    if len(unique_points) < len(points):
        warnings.warn("Duplicate points detected, using first occurrence")
        x, y, z = x[unique_indices], y[unique_indices], z[unique_indices]
        points = unique_points
    
    # 创建目标网格点 | Create target grid points
    xi_flat, yi_flat = xi.flatten(), yi.flatten()
    target_points = np.column_stack((xi_flat, yi_flat))
    
    # 执行线性插值 | Perform linear interpolation
    try:
        zi_flat = griddata(points, z, target_points, method='linear', fill_value=fill_value)
        zi = zi_flat.reshape(xi.shape)
    except Exception as e:
        raise ValueError(f"Linear interpolation failed: {e}")
    
    return zi


def cubic_interpolation(x: np.ndarray, y: np.ndarray, z: np.ndarray, 
                       xi: np.ndarray, yi: np.ndarray, 
                       fill_value: float = np.nan) -> np.ndarray:
    """
    三次样条插值 | Cubic spline interpolation
    
    使用三次样条插值方法对散点数据进行网格插值 | Use cubic spline interpolation method for grid interpolation of scattered data
    
    Args:
        x: 原始X坐标数组 | Original X coordinate array
        y: 原始Y坐标数组 | Original Y coordinate array
        z: 原始Z值数组 | Original Z value array
        xi: 目标X坐标网格 | Target X coordinate grid
        yi: 目标Y坐标网格 | Target Y coordinate grid
        fill_value: 填充值 | Fill value for extrapolation
        
    Returns:
        插值后的Z值网格 | Interpolated Z value grid
        
    Raises:
        ValueError: 输入数据维度不匹配或点数不足 | Input data dimensions mismatch or insufficient points
    """
    # 验证输入数据 | Validate input data
    if len(x) != len(y) or len(y) != len(z):
        raise ValueError("Input arrays must have the same length")
    
    if len(x) < 6:
        raise ValueError("At least 6 points are required for cubic interpolation")
    
    # 检查重复点 | Check for duplicate points
    points = np.column_stack((x, y))
    unique_points, unique_indices = np.unique(points, axis=0, return_index=True)
    
    if len(unique_points) < len(points):
        warnings.warn("Duplicate points detected, using first occurrence")
        x, y, z = x[unique_indices], y[unique_indices], z[unique_indices]
        points = unique_points
    
    # 创建目标网格点 | Create target grid points
    xi_flat, yi_flat = xi.flatten(), yi.flatten()
    target_points = np.column_stack((xi_flat, yi_flat))
    
    # 执行三次插值 | Perform cubic interpolation
    try:
        zi_flat = griddata(points, z, target_points, method='cubic', fill_value=fill_value)
        zi = zi_flat.reshape(xi.shape)
    except Exception as e:
        # 如果三次插值失败，回退到线性插值 | Fall back to linear interpolation if cubic fails
        warnings.warn(f"Cubic interpolation failed ({e}), falling back to linear interpolation")
        zi_flat = griddata(points, z, target_points, method='linear', fill_value=fill_value)
        zi = zi_flat.reshape(xi.shape)
    
    return zi


def rbf_interpolation(x: np.ndarray, y: np.ndarray, z: np.ndarray, 
                     xi: np.ndarray, yi: np.ndarray, 
                     kernel: str = 'thin_plate_spline',
                     smoothing: float = 0.0,
                     epsilon: Optional[float] = None) -> np.ndarray:
    """
    径向基函数插值 | Radial Basis Function (RBF) interpolation
    
    使用径向基函数进行高质量的散点数据插值 | Use radial basis functions for high-quality scattered data interpolation
    
    Args:
        x: 原始X坐标数组 | Original X coordinate array
        y: 原始Y坐标数组 | Original Y coordinate array
        z: 原始Z值数组 | Original Z value array
        xi: 目标X坐标网格 | Target X coordinate grid
        yi: 目标Y坐标网格 | Target Y coordinate grid
        kernel: RBF核函数类型 | RBF kernel type
        smoothing: 平滑参数 | Smoothing parameter
        epsilon: 形状参数 | Shape parameter
        
    Returns:
        插值后的Z值网格 | Interpolated Z value grid
        
    Raises:
        ValueError: 输入数据维度不匹配 | Input data dimensions mismatch
    """
    # 验证输入数据 | Validate input data
    if len(x) != len(y) or len(y) != len(z):
        raise ValueError("Input arrays must have the same length")
    
    if len(x) < 3:
        raise ValueError("At least 3 points are required for RBF interpolation")
    
    # 检查重复点 | Check for duplicate points
    points = np.column_stack((x, y))
    unique_points, unique_indices = np.unique(points, axis=0, return_index=True)
    
    if len(unique_points) < len(points):
        warnings.warn("Duplicate points detected, using first occurrence")
        x, y, z = x[unique_indices], y[unique_indices], z[unique_indices]
        points = unique_points
    
    # 创建目标网格点 | Create target grid points
    xi_flat, yi_flat = xi.flatten(), yi.flatten()
    target_points = np.column_stack((xi_flat, yi_flat))
    
    # 执行RBF插值 | Perform RBF interpolation
    try:
        # 使用scipy的RBFInterpolator | Use scipy's RBFInterpolator
        rbf_params = {'kernel': kernel, 'smoothing': smoothing}
        if epsilon is not None:
            rbf_params['epsilon'] = epsilon
        
        rbf = RBFInterpolator(points, z, **rbf_params)
        zi_flat = rbf(target_points)
        zi = zi_flat.reshape(xi.shape)
        
    except Exception as e:
        # 如果RBF插值失败，回退到线性插值 | Fall back to linear interpolation if RBF fails
        warnings.warn(f"RBF interpolation failed ({e}), falling back to linear interpolation")
        zi_flat = griddata(points, z, target_points, method='linear', fill_value=np.nan)
        zi = zi_flat.reshape(xi.shape)
    
    return zi


def adaptive_interpolation(x: np.ndarray, y: np.ndarray, z: np.ndarray, 
                          xi: np.ndarray, yi: np.ndarray, 
                          density_threshold: float = 0.1) -> np.ndarray:
    """
    自适应插值 | Adaptive interpolation
    
    根据数据点密度自动选择最适合的插值方法 | Automatically select the most suitable interpolation method based on data point density
    
    Args:
        x: 原始X坐标数组 | Original X coordinate array
        y: 原始Y坐标数组 | Original Y coordinate array
        z: 原始Z值数组 | Original Z value array
        xi: 目标X坐标网格 | Target X coordinate grid
        yi: 目标Y坐标网格 | Target Y coordinate grid
        density_threshold: 密度阈值 | Density threshold
        
    Returns:
        插值后的Z值网格 | Interpolated Z value grid
    """
    # 计算数据点密度 | Calculate data point density
    x_range = np.max(x) - np.min(x)
    y_range = np.max(y) - np.min(y)
    area = x_range * y_range
    density = len(x) / area if area > 0 else 0
    
    # 根据密度和点数选择插值方法 | Select interpolation method based on density and point count
    if len(x) < 6:
        # 点数太少，使用线性插值 | Too few points, use linear interpolation
        return linear_interpolation(x, y, z, xi, yi)
    elif density < density_threshold or len(x) < 20:
        # 密度低或点数较少，使用线性插值 | Low density or few points, use linear interpolation
        return linear_interpolation(x, y, z, xi, yi)
    elif len(x) < 100:
        # 中等点数，使用三次插值 | Medium point count, use cubic interpolation
        return cubic_interpolation(x, y, z, xi, yi)
    else:
        # 点数较多，使用RBF插值 | Many points, use RBF interpolation
        return rbf_interpolation(x, y, z, xi, yi)


def create_interpolation_grid(x_bounds: Tuple[float, float], 
                             y_bounds: Tuple[float, float], 
                             resolution: int = 100) -> Tuple[np.ndarray, np.ndarray]:
    """
    创建插值网格 | Create interpolation grid
    
    Args:
        x_bounds: X坐标边界 (min, max) | X coordinate bounds (min, max)
        y_bounds: Y坐标边界 (min, max) | Y coordinate bounds (min, max)
        resolution: 网格分辨率 | Grid resolution
        
    Returns:
        (X_grid, Y_grid)网格元组 | (X_grid, Y_grid) grid tuple
    """
    x_min, x_max = x_bounds
    y_min, y_max = y_bounds
    
    xi = np.linspace(x_min, x_max, resolution)
    yi = np.linspace(y_min, y_max, resolution)
    
    return np.meshgrid(xi, yi)


def interpolate_mountain_data(x: np.ndarray, y: np.ndarray, z: np.ndarray, 
                             method: str = 'auto',
                             resolution: int = 100,
                             bounds: Optional[Tuple[Tuple[float, float], Tuple[float, float]]] = None,
                             **kwargs) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    山体数据插值的便捷函数 | Convenience function for mountain data interpolation
    
    Args:
        x: X坐标数组 | X coordinate array
        y: Y坐标数组 | Y coordinate array
        z: Z值数组 | Z value array
        method: 插值方法 | Interpolation method ('linear', 'cubic', 'rbf', 'auto')
        resolution: 网格分辨率 | Grid resolution
        bounds: 插值边界 | Interpolation bounds ((x_min, x_max), (y_min, y_max))
        **kwargs: 传递给插值函数的额外参数 | Additional parameters for interpolation functions
        
    Returns:
        (X_grid, Y_grid, Z_grid)插值结果 | (X_grid, Y_grid, Z_grid) interpolation result
    """
    # 确定插值边界 | Determine interpolation bounds
    if bounds is None:
        x_bounds = (np.min(x), np.max(x))
        y_bounds = (np.min(y), np.max(y))
    else:
        x_bounds, y_bounds = bounds
    
    # 创建插值网格 | Create interpolation grid
    X_grid, Y_grid = create_interpolation_grid(x_bounds, y_bounds, resolution)
    
    # 选择插值方法 | Select interpolation method
    interpolation_functions = {
        'linear': linear_interpolation,
        'cubic': cubic_interpolation,
        'rbf': rbf_interpolation,
        'auto': adaptive_interpolation
    }
    
    if method not in interpolation_functions:
        raise ValueError(f"Unsupported interpolation method: {method}. "
                        f"Supported methods: {list(interpolation_functions.keys())}")
    
    interpolation_func = interpolation_functions[method]
    
    # 执行插值 | Perform interpolation
    if method == 'rbf':
        Z_grid = interpolation_func(x, y, z, X_grid, Y_grid, **kwargs)
    else:
        # 过滤kwargs中不适用的参数 | Filter out inapplicable parameters from kwargs
        valid_kwargs = {}
        if 'fill_value' in kwargs:
            valid_kwargs['fill_value'] = kwargs['fill_value']
        Z_grid = interpolation_func(x, y, z, X_grid, Y_grid, **valid_kwargs)
    
    return X_grid, Y_grid, Z_grid


def calculate_interpolation_error(x: np.ndarray, y: np.ndarray, z: np.ndarray, 
                                 method: str = 'linear',
                                 test_fraction: float = 0.2,
                                 random_state: Optional[int] = None) -> Dict[str, float]:
    """
    计算插值误差 | Calculate interpolation error
    
    使用交叉验证方法评估插值精度 | Use cross-validation method to evaluate interpolation accuracy
    
    Args:
        x: X坐标数组 | X coordinate array
        y: Y坐标数组 | Y coordinate array
        z: Z值数组 | Z value array
        method: 插值方法 | Interpolation method
        test_fraction: 测试数据比例 | Test data fraction
        random_state: 随机种子 | Random seed
        
    Returns:
        误差统计字典 | Error statistics dictionary
    """
    if random_state is not None:
        np.random.seed(random_state)
    
    # 随机选择测试点 | Randomly select test points
    n_total = len(x)
    n_test = int(n_total * test_fraction)
    test_indices = np.random.choice(n_total, n_test, replace=False)
    train_indices = np.setdiff1d(np.arange(n_total), test_indices)
    
    # 分割训练和测试数据 | Split training and test data
    x_train, y_train, z_train = x[train_indices], y[train_indices], z[train_indices]
    x_test, y_test, z_test = x[test_indices], y[test_indices], z[test_indices]
    
    # 创建测试网格 | Create test grid
    xi_test, yi_test = np.meshgrid(x_test, y_test, indexing='ij')
    
    # 执行插值 | Perform interpolation
    interpolation_functions = {
        'linear': linear_interpolation,
        'cubic': cubic_interpolation,
        'rbf': rbf_interpolation,
        'auto': adaptive_interpolation
    }
    
    interpolation_func = interpolation_functions[method]
    
    try:
        # 对测试点进行插值 | Interpolate test points
        z_pred = []
        for i in range(len(x_test)):
            xi_single = np.array([[x_test[i]]])
            yi_single = np.array([[y_test[i]]])
            z_single = interpolation_func(x_train, y_train, z_train, xi_single, yi_single)
            z_pred.append(z_single[0, 0])
        
        z_pred = np.array(z_pred)
        
        # 计算误差统计 | Calculate error statistics
        valid_mask = ~np.isnan(z_pred)
        if np.sum(valid_mask) == 0:
            return {'mae': np.inf, 'rmse': np.inf, 'r2': -np.inf, 'valid_predictions': 0}
        
        z_test_valid = z_test[valid_mask]
        z_pred_valid = z_pred[valid_mask]
        
        # 平均绝对误差 | Mean Absolute Error
        mae = np.mean(np.abs(z_test_valid - z_pred_valid))
        
        # 均方根误差 | Root Mean Square Error
        rmse = np.sqrt(np.mean((z_test_valid - z_pred_valid)**2))
        
        # R²决定系数 | R² coefficient of determination
        ss_res = np.sum((z_test_valid - z_pred_valid)**2)
        ss_tot = np.sum((z_test_valid - np.mean(z_test_valid))**2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else -np.inf
        
        return {
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
            'valid_predictions': np.sum(valid_mask)
        }
        
    except Exception as e:
        warnings.warn(f"Error calculation failed: {e}")
        return {'mae': np.inf, 'rmse': np.inf, 'r2': -np.inf, 'valid_predictions': 0}