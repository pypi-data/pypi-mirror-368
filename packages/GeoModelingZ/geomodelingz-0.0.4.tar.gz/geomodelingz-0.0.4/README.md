# GeoModelingZ

这是一个地理建模与可视化工具库，专为Jupyter Notebook环境优化，提供了丰富的交互式地理数据可视化功能。

## 主要功能

- **环境检测**: 自动检测Jupyter Notebook环境
- **交互式图表**: 支持matplotlib交互式图表绘制
- **地理地图可视化**: 强大的交互式地理地图功能
- **GeoJSON支持**: 完整支持GeoJSON数据格式
- **多几何类型**: 支持点、线、多边形和Multi类型几何数据
- **自动聚焦**: 智能聚焦到数据区域
- **多底图支持**: 支持Mapbox和OpenStreetMap等多种底图

## 安装

### 基本安装

```bash
pip install GeoModelingZ
```

### 安装Jupyter支持（推荐）

```bash
pip install GeoModelingZ[jupyter]
```

## 使用方法

### 环境检测

```python
from GeoModelingZ import is_jupyter

# 检查是否在Jupyter环境中运行
if is_jupyter():
    print("当前在Jupyter环境中运行")
else:
    print("当前在普通Python环境中运行")
```

### 交互式图表

```python
from GeoModelingZ import plot_simple_chart

# 创建简单的交互式图表
fig = plot_simple_chart(title="我的图表")

# 在Jupyter环境中，可以交互调整参数
# 在普通环境中，返回matplotlib图表对象
```

### 地理地图可视化

```python
from GeoModelingZ import create_geo_map

# 创建基本地图
map_obj = create_geo_map(
    width=1000, 
    height=700,
    center=[39.9042, 116.4074],  # 北京坐标
    zoom_start=10
)

# 加载GeoJSON数据
map_with_data = create_geo_map(
    geojson_file="path/to/your/data.geojson",
    mapbox_token="your_mapbox_token",  # 可选
)

# 显示地图（在Jupyter中）
map_with_data
```

## 支持的GeoJSON几何类型

- **Point**: 单点数据
- **MultiPoint**: 多点数据
- **LineString**: 线数据
- **MultiLineString**: 多线数据
- **Polygon**: 多边形数据
- **MultiPolygon**: 复杂多边形数据

## 底图类型

- **streets**: 矢量街道地图（默认）
- **satellite**: 卫星影像地图
- **outdoors**: 地形图
- **light**: 浅色底图
- **dark**: 深色底图
- **OpenStreetMap**: 开源街道地图

## 依赖

- Python >= 3.6
- numpy
- matplotlib
- ipython
- folium

### 可选依赖（用于Jupyter功能）

- ipywidgets >= 7.0.0
- jupyterlab_widgets

## 更新日志

### v0.0.4
- 重构代码结构，移除冗余功能
- 专注于地理数据可视化核心功能
- 优化GeoJSON数据处理逻辑
- 改进地图渲染性能
- 增强错误处理和调试信息

### v0.0.3
- 修改了可视化地图的渲染样式
- 优化了GeoJSON数据处理

### v0.0.2
- 添加了交互式地理地图功能 (create_geo_map)
- 支持GeoJSON数据的可视化
- 支持点、线、多边形和Multi类型几何数据
- 自动聚焦到数据区域

### v0.0.1
- 初始版本发布
- 基本功能实现

## 贡献

欢迎提交Issue和Pull Request来改进这个库！

## 许可证

MIT License