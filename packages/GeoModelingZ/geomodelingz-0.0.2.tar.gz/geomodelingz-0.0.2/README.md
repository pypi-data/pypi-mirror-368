# GeoModelingZ

这是一个地理建模工具库，专为Jupyter Notebook环境优化，提供了丰富的交互式功能。

## 功能

- 提供友好的问候语
- 获取格式化的当前时间
- Jupyter Notebook交互式组件
- 数据可视化与图表交互
- 交互式地理地图（支持GeoJSON数据）
- 支持点、线、多边形和Multi类型几何数据
- Markdown内容展示

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

### 基本功能

```python
import GeoModelingZ

# 使用基本函数
print(GeoModelingZ.say_hello("World"))
print(f"当前时间是: {GeoModelingZ.get_current_time_str()}")

# 查看版本号
print(f"库版本: {GeoModelingZ.__version__}")
```

### Jupyter Notebook中的交互功能

```python
import GeoModelingZ

# 显示交互式时间小部件
GeoModelingZ.show_time_widget()

# 创建交互式图表
GeoModelingZ.plot_simple_chart()

# 显示Markdown内容
GeoModelingZ.display_markdown("# 这是一个标题\n这是**加粗**的文本")

# 创建地理数据可视化小部件
GeoModelingZ.create_geo_widget()

# 创建交互式地理地图（支持GeoJSON数据）
GeoModelingZ.create_geo_map(geojson_file="path/to/your/data.geojson")
```

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

### v0.0.2
- 添加了交互式地理地图功能 (create_geo_map)
- 支持GeoJSON数据的可视化
- 支持点、线、多边形和Multi类型几何数据
- 自动聚焦到数据区域

### v0.0.1
- 初始版本发布
- 基本功能实现