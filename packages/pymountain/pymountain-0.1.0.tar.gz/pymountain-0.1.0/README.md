# PyMountain 🏔️

**A powerful and flexible Python library for mountain terrain data visualization**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](#)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](#)

## 🌟 Features

### 🎯 Core Features
- **Multiple visualization methods**
  - 3D surface rendering
  - Contour maps
  - Scatter plots
  - Custom renderers

- **Flexible data processing**
  - Multiple data format support
  - Data interpolation and smoothing
  - Statistical analysis features
  - Data import/export

- **Highly customizable**
  - Custom color mapping
  - Configurable rendering parameters
  - Plugin-based architecture
  - Theme and style system

### 🚀 Performance Advantages
- **Efficient rendering**
- **Memory optimization**
- **Large dataset support**
- **Parallel processing**

## 📦 Installation

### Install with pip
```bash
pip install pymountain
```

### Install from source
```bash
git clone https://github.com/yourusername/pymountain.git
cd pymountain
pip install -e .
```

### Development installation
```bash
git clone https://github.com/yourusername/pymountain.git
cd pymountain
pip install -e ".[dev]"
```

## 🚀 Quick Start

### Create your first mountain in 30 seconds

```python
from pymountain import quick_render

# Define mountain peak data points (x, y, elevation)
points = [
    (0, 0, 1000),    # Peak
    (1, 0, 800),     # East side
    (-1, 0, 800),    # West side
    (0, 1, 750),     # North side
    (0, -1, 750),    # South side
]

# Complete 3D visualization in one line!
renderer = quick_render(points, renderer_type="3d", title="My First Mountain")
renderer.show()
```

### More detailed usage

```python
from pymountain import MountainData, Matplotlib3DRenderer

# Create data object
data = MountainData()

# Add data points
data.add_point(0, 0, 1000, metadata={'name': 'Main Peak'})
data.add_point(1, 1, 800, metadata={'name': 'Secondary Peak'})
data.add_point(-1, -1, 600, metadata={'name': 'Small Peak'})

# Create renderer
renderer = Matplotlib3DRenderer(
    config={
        'title': 'Mountain Terrain Map',
        'colormap': 'terrain',
        'figure_size': (12, 8)
    }
)

# Render and display
fig = renderer.render(data)
renderer.show()

# Save image
renderer.save_figure('my_mountain.png')
```

## 📚 Documentation and Examples

### 📖 Example Code

We provide rich example code to help you get started quickly:

```bash
# Quick start example
python examples/quick_start.py

# Basic usage example
python examples/basic_usage.py

# Advanced features example
python examples/advanced_usage.py
```

### 🎓 Learning Path

1. **Beginners**: Start with `examples/quick_start.py`
2. **Intermediate**: Learn `examples/basic_usage.py`
3. **Advanced**: Explore `examples/advanced_usage.py`

## 🛠️ API Reference

### Core Classes

#### `MountainData`
Mountain data management class

```python
from pymountain import MountainData

data = MountainData()
data.add_point(x, y, elevation, metadata={})
data.get_bounds()  # Get data bounds
data.get_elevation_stats()  # Get elevation statistics
```

#### `BaseRenderer`
Base renderer class

```python
from pymountain import Matplotlib3DRenderer

renderer = Matplotlib3DRenderer(config={
    'title': 'Title',
    'colormap': 'terrain',
    'figure_size': (10, 8)
})
```

### Renderer Types

| Renderer | Description | Use Case |
|----------|-------------|----------|
| `Matplotlib3DRenderer` | 3D surface rendering | 3D terrain display |
| `MatplotlibContourRenderer` | Contour rendering | Terrain analysis |
| `MatplotlibRenderer` | General renderer | Custom visualization |

### Utility Functions

#### Interpolation Functions
```python
from pymountain.utils import (
    linear_interpolation,
    cubic_interpolation,
    rbf_interpolation
)

# Linear interpolation
zi = linear_interpolation(x, y, z, xi, yi)
```

#### Color Mapping
```python
from pymountain.utils import ColorMapper, create_elevation_colormap

# Create custom color mapping
colormap = create_elevation_colormap({
    (0, 500): '#2E8B57',      # Lowland
    (500, 1000): '#DAA520',   # Hills
    (1000, 2000): '#A0522D'   # Mountains
})
```

## 🎨 Advanced Features

### Custom Color Mapping

```python
from pymountain import ColorMapper

# Create color mapper
mapper = ColorMapper()

# Define elevation band colors
elevation_colors = {
    (0, 200): '#2E8B57',      # Sea green - lowland
    (200, 600): '#DAA520',    # Golden - hills
    (600, 1000): '#A0522D',   # Sienna - mountains
    (1000, float('inf')): '#FFFFFF'  # White - snow peaks
}

colormap = mapper.create_elevation_colormap(elevation_colors)
```

### Data Interpolation

```python
from pymountain.utils import interpolate_mountain_data

# Interpolate sparse data
interpolated_data = interpolate_mountain_data(
    data, 
    method='cubic',
    grid_size=(100, 100)
)
```

### Performance Optimization

```python
# Large dataset processing recommendations
data = MountainData()

# Use batch addition
points = [(x, y, z) for x, y, z in large_dataset]
data.add_points_batch(points)

# Use data sampling
sampled_data = data.sample(max_points=1000)
```

## 📊 Supported Data Formats

### Input Formats
- **NumPy arrays**: `(x, y, z)` coordinates
- **Pandas DataFrame**: DataFrame with coordinate columns
- **JSON files**: Structured terrain data
- **CSV files**: Comma-separated coordinate data
- **Python lists**: `[(x1, y1, z1), (x2, y2, z2), ...]`

### Output Formats
- **Image files**: PNG, JPG, SVG, PDF
- **Data files**: JSON, CSV, NumPy (.npz)
- **Interactive charts**: HTML (via Plotly)

## 🔧 Configuration Options

### Renderer Configuration

```python
config = {
    # Basic settings
    'title': 'Mountain Terrain Map',
    'figure_size': (12, 8),
    'dpi': 300,
    
    # Color settings
    'colormap': 'terrain',
    'color_levels': 20,
    
    # 3D settings
    'elevation_angle': 30,
    'azimuth_angle': 45,
    'surface_alpha': 0.8,
    
    # Contour settings
    'contour_levels': 15,
    'filled_contours': True,
    'show_contour_lines': True,
    
    # Data point settings
    'show_data_points': True,
    'point_size': 50,
    'point_color': 'red'
}
```

## 🧪 Testing

Run test suite:

```bash
# Run all tests
pytest

# Run specific tests
pytest tests/test_core.py

# Generate coverage report
pytest --cov=pymountain
```

## 🤝 Contributing

We welcome all forms of contributions!

### How to Contribute

1. **Fork** this repository
2. **Create** a feature branch
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit** your changes
   ```bash
   git commit -m 'Add some amazing feature'
   ```
4. **Push** to the branch
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open** a Pull Request

### Development Guidelines

- Follow PEP 8 code style
- Add appropriate tests
- Update documentation
- Ensure all tests pass

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to all contributors
- Built on excellent open source libraries:
  - [NumPy](https://numpy.org/) - Numerical computing
  - [Matplotlib](https://matplotlib.org/) - Data visualization
  - [SciPy](https://scipy.org/) - Scientific computing

## 📞 Support

- **Documentation**: [Online Documentation](https://pymountain.readthedocs.io/)
- **Issue Reports**: [GitHub Issues](https://github.com/yourusername/pymountain/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/pymountain/discussions)
- **Email**: support@pymountain.org

## 🗺️ Roadmap

### v1.1 (Planned)
- [ ] Interactive 3D visualization
- [ ] More renderer support
- [ ] Performance optimization
- [ ] Mobile support

### v1.2 (Future)
- [ ] Real-time data streaming
- [ ] Machine learning integration
- [ ] Cloud rendering service
- [ ] VR/AR support

---

**Start your mountain visualization journey! 🏔️**

[⬆ Back to top](#pymountain-🏔️)