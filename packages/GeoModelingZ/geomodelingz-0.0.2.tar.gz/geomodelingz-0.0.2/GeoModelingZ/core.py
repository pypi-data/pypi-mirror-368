# GeoModelingZ/core.py

import datetime
import sys
import numpy as np
import matplotlib.pyplot as plt

# 检查是否在Jupyter环境中运行
def is_jupyter():
    """
    检查当前环境是否为Jupyter Notebook或JupyterLab
    """
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':  # Jupyter notebook or qtconsole
            return True
        elif shell == 'TerminalInteractiveShell':  # Terminal IPython
            return False
        else:
            return False
    except NameError:  # 普通Python环境
        return False

# 如果在Jupyter环境中，导入相关模块
if is_jupyter():
    try:
        from IPython.display import display, HTML, Markdown
        import ipywidgets as widgets
        from ipywidgets import interact, interactive, fixed, interact_manual
        _HAS_JUPYTER_SUPPORT = True
    except ImportError:
        _HAS_JUPYTER_SUPPORT = False
else:
    _HAS_JUPYTER_SUPPORT = False

def say_hello(name: str):
    """
    生成一句友好的问候语。
    
    如果在Jupyter环境中运行，将以HTML格式显示。
    
    参数:
        name (str): 用户名
    
    返回:
        str: 问候语
    """
    greeting = f"Hello, {name}! Welcome to GeoModelingZ."
    
    if _HAS_JUPYTER_SUPPORT:
        display(HTML(f"<h3 style='color:green'>{greeting}</h3>"))
    
    return greeting

def get_current_time_str():
    """
    以字符串形式返回当前时间。
    
    返回:
        str: 格式化的当前时间
    """
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def show_time_widget():
    """
    显示一个交互式时间小部件，可以选择时间格式。
    
    仅在Jupyter环境中有效。
    """
    if not _HAS_JUPYTER_SUPPORT:
        print("此功能仅在Jupyter环境中可用。")
        return
    
    @interact
    def format_time(format_str=widgets.Dropdown(
        options=['%Y-%m-%d %H:%M:%S', '%Y/%m/%d', '%H:%M:%S', '%Y年%m月%d日 %H时%M分%S秒'],
        value='%Y-%m-%d %H:%M:%S',
        description='时间格式:'
    )):
        now = datetime.datetime.now()
        formatted = now.strftime(format_str)
        display(HTML(f"<p>当前时间: <b>{formatted}</b></p>"))
        return formatted

def plot_simple_chart(x_data=None, y_data=None, title="简单图表", interactive=True):
    """
    绘制简单图表，支持交互式调整。
    
    参数:
        x_data (list): x轴数据，默认为None（自动生成）
        y_data (list): y轴数据，默认为None（自动生成）
        title (str): 图表标题
        interactive (bool): 是否使用交互式控件
    
    返回:
        matplotlib.figure.Figure: 图表对象
    """
    if x_data is None:
        x_data = np.linspace(0, 10, 100)
    if y_data is None:
        y_data = np.sin(x_data)
    
    if _HAS_JUPYTER_SUPPORT and interactive:
        @interact
        def update(
            amplitude=widgets.FloatSlider(min=0.1, max=2.0, step=0.1, value=1.0, description='振幅:'),
            frequency=widgets.FloatSlider(min=0.1, max=2.0, step=0.1, value=1.0, description='频率:'),
            chart_title=widgets.Text(value=title, description='标题:')
        ):
            plt.figure(figsize=(10, 6))
            plt.plot(x_data, amplitude * np.sin(frequency * x_data))
            plt.title(chart_title)
            plt.xlabel('X轴')
            plt.ylabel('Y轴')
            plt.grid(True)
            plt.show()
    else:
        fig = plt.figure(figsize=(10, 6))
        plt.plot(x_data, y_data)
        plt.title(title)
        plt.xlabel('X轴')
        plt.ylabel('Y轴')
        plt.grid(True)
        return fig

def display_markdown(text):
    """
    以Markdown格式显示文本。
    
    参数:
        text (str): Markdown格式的文本
    """
    if _HAS_JUPYTER_SUPPORT:
        display(Markdown(text))
    else:
        print(text)

def create_geo_widget():
    """
    创建一个地理数据可视化的简单交互式小部件。
    
    仅在Jupyter环境中有效。
    """
    if not _HAS_JUPYTER_SUPPORT:
        print("此功能仅在Jupyter环境中可用。")
        return
    
    # 创建一些示例数据
    latitudes = np.random.uniform(20, 50, 10)
    longitudes = np.random.uniform(100, 140, 10)
    values = np.random.uniform(0, 100, 10)
    
    @interact
    def plot_geo(
        marker_size=widgets.IntSlider(min=10, max=200, step=10, value=50, description='点大小:'),
        color_map=widgets.Dropdown(
            options=['viridis', 'plasma', 'inferno', 'magma', 'cividis'],
            value='viridis',
            description='颜色映射:'
        )
    ):
        plt.figure(figsize=(12, 8))
        scatter = plt.scatter(longitudes, latitudes, c=values, s=marker_size, cmap=color_map, alpha=0.7)
        plt.colorbar(scatter, label='数值')
        plt.title('地理数据可视化')
        plt.xlabel('经度')
        plt.ylabel('纬度')
        plt.grid(True)
        plt.show()

# 创建一个地理地图，输入参数为地图宽高（默认为800*600）、geojson数据文件（默认随机生成点）、点大小（默认50）、颜色映射（默认viridis）
def create_geo_map(width=800, height=600, geojson_file=None, point_size=50, color_map='viridis', 
                center=[35, 120], zoom_start=5, mapbox_token=''):
    """
    创建一个交互式地理地图，使用Folium和Mapbox底图。支持点、线、多边形数据渲染。
    
    参数:
        width (int): 地图宽度
        height (int): 地图高度
        geojson_file (str): GeoJSON数据文件路径
        point_size (int): 点大小
        color_map (str): 颜色映射
        center (list): 地图中心点坐标 [纬度, 经度]
        zoom_start (int): 初始缩放级别
        mapbox_token (str): Mapbox访问令牌
    
    返回:
        folium.Map: 交互式地图对象
    """
    try:
        import folium
        import json
        from folium.plugins import HeatMap, MarkerCluster
        from branca.colormap import LinearColormap
    except ImportError:
        print("请安装folium库: pip install folium")
        return None
    
    # 创建地图
    m = folium.Map(
        location=center,
        zoom_start=zoom_start,
        width=width,
        height=height,
        tiles="https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/{z}/{x}/{y}?access_token=" + mapbox_token,
        attr='Mapbox'
    )
    
    if geojson_file is None:
        # 随机生成点
        latitudes = np.random.uniform(20, 50, 10)
        longitudes = np.random.uniform(100, 140, 10)
        values = np.random.uniform(0, 100, 10)
        
        # 创建颜色映射
        color_scale = LinearColormap(
            colors=['green', 'yellow', 'red'],
            vmin=min(values),
            vmax=max(values),
            caption='数值'
        )
        
        # 添加点到地图
        for lat, lon, val in zip(latitudes, longitudes, values):
            folium.CircleMarker(
                location=[lat, lon],
                radius=point_size/10,  # 调整大小比例
                color=None,
                fill=True,
                fill_color=color_scale(val),
                fill_opacity=0.7,
                popup=f"值: {val:.2f}"
            ).add_to(m)
            
        # 添加颜色图例
        color_scale.add_to(m)
    else:
        # 读取geojson数据
        try:
            with open(geojson_file, 'r') as f:
                geojson_data = json.load(f)
            
            # 创建点聚类图层（如果有多个点）
            marker_cluster = MarkerCluster(name="点聚类").add_to(m)
            
            # 处理MultiPoint类型，将其转换为单独的点
            for feature in geojson_data.get('features', []):
                if feature.get('geometry', {}).get('type') == 'MultiPoint':
                    properties = feature.get('properties', {})
                    for point in feature['geometry']['coordinates']:
                        folium.CircleMarker(
                            location=[point[1], point[0]],  # 注意经纬度顺序
                            radius=5,
                            color='#3186cc',
                            fill=True,
                            fill_color='#3186cc',
                            fill_opacity=0.7,
                            popup=folium.Popup(
                                html='<br>'.join([f"{k}: {v}" for k, v in properties.items() if not k.startswith('tdt_')]),
                                max_width=300
                            )
                        ).add_to(marker_cluster)
            
            # 根据几何类型应用不同的样式
            def style_function(feature):
                geometry_type = feature['geometry']['type']
                if geometry_type == 'Point' or geometry_type == 'MultiPoint':
                    return {
                        'fillColor': '#3186cc',
                        'color': '#3186cc',
                        'weight': 2,
                        'fillOpacity': 0.7
                    }
                elif geometry_type == 'LineString' or geometry_type == 'MultiLineString':
                    return {
                        'color': '#ff7800',
                        'weight': 3,
                        'opacity': 0.7
                    }
                elif geometry_type == 'Polygon' or geometry_type == 'MultiPolygon':
                    return {
                        'fillColor': '#ffff00',
                        'color': 'black',
                        'weight': 1,
                        'fillOpacity': 0.5
                    }
                else:
                    # 默认样式
                    return {
                        'fillColor': '#cccccc',
                        'color': '#000000',
                        'weight': 1,
                        'fillOpacity': 0.5
                    }
            
            # 高亮样式
            def highlight_function(feature):
                geometry_type = feature['geometry']['type']
                if geometry_type == 'Point' or geometry_type == 'MultiPoint':
                    return {
                        'fillColor': '#0000ff',
                        'color': '#0000ff',
                        'weight': 3,
                        'fillOpacity': 0.9
                    }
                elif geometry_type == 'LineString' or geometry_type == 'MultiLineString':
                    return {
                        'color': '#ff0000',
                        'weight': 5,
                        'opacity': 0.9
                    }
                elif geometry_type == 'Polygon' or geometry_type == 'MultiPolygon':
                    return {
                        'fillColor': '#000000',
                        'color': '#000000',
                        'fillOpacity': 0.7,
                        'weight': 2
                    }
                else:
                    # 默认高亮样式
                    return {
                        'fillColor': '#ff00ff',
                        'color': '#ff00ff',
                        'weight': 3,
                        'fillOpacity': 0.9
                    }
            
            # 获取所有可能的属性字段
            all_fields = set()
            for feature in geojson_data.get('features', []):
                properties = feature.get('properties', {})
                all_fields.update(properties.keys())
            
            # 过滤掉tdt_开头的技术字段
            display_fields = [field for field in all_fields if not field.startswith('tdt_')]
            
            # 如果字段太多，只显示重要的几个
            if len(display_fields) > 5:
                important_fields = ['省份', '城市', '园区', '经度', '纬度']
                display_fields = [f for f in important_fields if f in display_fields]
            
            # 创建对应的别名
            aliases = [f"{field}:" for field in display_fields]
            
            # 打印GeoJSON数据的结构，帮助调试
            print(f"GeoJSON数据包含 {len(geojson_data.get('features', []))} 个要素")
            
            # 检查是否是单个Feature而不是FeatureCollection
            if 'type' in geojson_data and geojson_data['type'] == 'Feature':
                # 将单个Feature转换为FeatureCollection
                geojson_data = {
                    'type': 'FeatureCollection',
                    'features': [geojson_data]
                }
                print("已将单个Feature转换为FeatureCollection")
                
            # 确保数据是有效的GeoJSON
            if 'features' not in geojson_data:
                print("警告: GeoJSON数据中没有'features'字段")
                if 'geometry' in geojson_data:
                    # 尝试将对象转换为标准GeoJSON
                    geojson_data = {
                        'type': 'FeatureCollection',
                        'features': [{
                            'type': 'Feature',
                            'geometry': geojson_data['geometry'],
                            'properties': geojson_data.get('properties', {})
                        }]
                    }
                    print("已尝试修复GeoJSON格式")
            
            # 添加GeoJSON数据到地图
            try:
                folium.GeoJson(
                    geojson_data,
                    name='geojson',
                    style_function=style_function,
                    highlight_function=highlight_function,
                    tooltip=folium.features.GeoJsonTooltip(
                        fields=display_fields,
                        aliases=aliases,
                        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
                    ),
                    popup=folium.features.GeoJsonPopup(
                        fields=display_fields,
                        aliases=aliases,
                        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
                    )
                ).add_to(m)
                print("GeoJSON数据已成功添加到地图")
            except Exception as e:
                print(f"添加GeoJSON到地图时出错: {e}")
                
                # 尝试直接使用folium.Polygon渲染MultiPolygon
                try:
                    for feature in geojson_data.get('features', []):
                        if feature.get('geometry', {}).get('type') == 'MultiPolygon':
                            properties = feature.get('properties', {})
                            # 提取不以tdt_开头的属性
                            popup_content = '<br>'.join([f"{k}: {v}" for k, v in properties.items() if not k.startswith('tdt_')])
                            
                            # 处理每个多边形
                            for polygon in feature['geometry']['coordinates']:
                                # 转换坐标点顺序（folium需要[lat, lon]而GeoJSON是[lon, lat]）
                                locations = [[point[1], point[0]] for point in polygon[0]]
                                
                                folium.Polygon(
                                    locations=locations,
                                    color='black',
                                    weight=1,
                                    fill=True,
                                    fill_color='#ffff00',
                                    fill_opacity=0.5,
                                    popup=folium.Popup(popup_content, max_width=300)
                                ).add_to(m)
                            
                            print(f"已使用folium.Polygon直接渲染MultiPolygon")
                except Exception as inner_e:
                    print(f"尝试直接渲染MultiPolygon时出错: {inner_e}")
            
            # 添加图层控制
            folium.LayerControl().add_to(m)
            
            # 自动聚焦到数据区域
            try:
                # 收集所有坐标点
                all_coords = []
                for feature in geojson_data.get('features', []):
                    geometry = feature.get('geometry', {})
                    geom_type = geometry.get('type', '')
                    coords = geometry.get('coordinates', [])
                    
                    if geom_type == 'Point':
                        all_coords.append([coords[1], coords[0]])  # 转换为[lat, lon]
                    elif geom_type == 'MultiPoint':
                        for point in coords:
                            all_coords.append([point[1], point[0]])
                    elif geom_type == 'LineString':
                        for point in coords:
                            all_coords.append([point[1], point[0]])
                    elif geom_type == 'MultiLineString':
                        for line in coords:
                            for point in line:
                                all_coords.append([point[1], point[0]])
                    elif geom_type == 'Polygon':
                        for ring in coords:
                            for point in ring:
                                all_coords.append([point[1], point[0]])
                    elif geom_type == 'MultiPolygon':
                        for polygon in coords:
                            for ring in polygon:
                                for point in ring:
                                    all_coords.append([point[1], point[0]])
                
                if all_coords:
                    # 计算边界框
                    sw = [min(coord[0] for coord in all_coords), min(coord[1] for coord in all_coords)]
                    ne = [max(coord[0] for coord in all_coords), max(coord[1] for coord in all_coords)]
                    
                    # 设置地图边界
                    m.fit_bounds([sw, ne])
                    print(f"已自动聚焦到数据区域: {sw} 到 {ne}")
            except Exception as bounds_e:
                print(f"自动聚焦到数据区域时出错: {bounds_e}")
            
        except Exception as e:
            print(f"读取GeoJSON文件出错: {e}")
    return m