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


# 创建一个地理地图，输入参数为地图宽高（默认为800*600）、geojson数据文件（默认随机生成点）、点大小（默认50）
def create_geo_map(width=800, height=600, geojson_file=None, 
                center=[39.89945, 116.40769], zoom_start=5, mapbox_token='', basemap='streets'):
    """
    创建一个交互式地理地图，使用Folium和Mapbox底图。支持点、线、多边形数据渲染。
    
    参数:
        width (int): 地图宽度
        height (int): 地图高度
        geojson_file (str): GeoJSON数据文件路径
        center (list): 地图中心点坐标 [纬度, 经度]
        zoom_start (int): 初始缩放级别
        mapbox_token (str): Mapbox访问令牌
        basemap (str): 底图类型，可选值：'streets'(矢量地图)、'satellite'(影像地图)、'outdoors'(地形图)、'light'(浅色)、'dark'(深色)
    
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
    
    # 底图类型映射
    basemap_styles = {
        'streets': 'streets-v11',    # 矢量地图
        'satellite': 'satellite-v9', # 影像地图
        'outdoors': 'outdoors-v11',  # 地形图
        'light': 'light-v10',        # 浅色底图
        'dark': 'dark-v10'           # 深色底图
    }
    
    # 确保选择的底图类型有效
    if basemap not in basemap_styles:
        print(f"警告: 未知的底图类型 '{basemap}'，使用默认的 'streets'")
        basemap = 'streets'
    
    # 创建地图
    m = folium.Map(
        location=center,
        zoom_start=zoom_start,
        width=width,
        height=height,
        tiles="https://api.mapbox.com/styles/v1/mapbox/{style}/tiles/{{z}}/{{x}}/{{y}}?access_token={token}".format(
            style=basemap_styles[basemap],
            token=mapbox_token
        ),
        attr='Mapbox'
    )
    
    # 添加底图切换控件
    if mapbox_token:
        # 添加不同类型的底图
        for map_type, style in basemap_styles.items():
            # 创建底图名称的英文映射
            map_type_names = {
                'streets': 'Streets',
                'satellite': 'Satellite',
                'outdoors': 'Terrain',
                'light': 'Light',
                'dark': 'Dark'
            }
            
            # 使用英文名称
            display_name = f"Mapbox {map_type_names.get(map_type, map_type.capitalize())}"
            
            folium.TileLayer(
                tiles="https://api.mapbox.com/styles/v1/mapbox/{style}/tiles/{{z}}/{{x}}/{{y}}?access_token={token}".format(
                    style=style,
                    token=mapbox_token
                ),
                attr='Mapbox',
                name=display_name
            ).add_to(m)
    
    # 添加开源底图选项（不需要token）
    folium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(m)
    
    if geojson_file is None:
        print("没有提供geojson文件")
        folium.LayerControl(position='topright', collapsed=True).add_to(m)
        return m
    else:
        # 读取geojson数据
        try:
            with open(geojson_file, 'r') as f:
                geojson_data = json.load(f)
            
            # 创建点聚类图层（如果有多个点）
            marker_cluster = MarkerCluster(name="点聚类").add_to(m)
            
            # 处理Point和MultiPoint类型，将其转换为单独的点
            for feature in geojson_data.get('features', []):
                geometry = feature.get('geometry', {})
                geometry_type = geometry.get('type')
                properties = feature.get('properties', {})
                
                if geometry_type == 'Point':
                    # 处理单点
                    point = geometry['coordinates']
                    folium.CircleMarker(
                        location=[point[1], point[0]],  # 注意经纬度顺序
                        radius=5,
                        color='#ff0000',
                        fill=True,
                        fill_color='#ffffff',
                        fill_opacity=1.0,
                        popup=folium.Popup(
                            html='<br>'.join([f"{k}: {v}" for k, v in properties.items() if not k.startswith('tdt_')]),
                            max_width=300
                        )
                    ).add_to(marker_cluster)
                elif geometry_type == 'MultiPoint':
                    # 处理多点
                    for point in geometry['coordinates']:
                        folium.CircleMarker(
                            location=[point[1], point[0]],  # 注意经纬度顺序
                            radius=5,
                            color='#ff0000',
                            fill=True,
                            fill_color='#ffffff',
                            fill_opacity=1.0,
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
                        'fillColor': '#ffffff',
                        'color': '#ff0000',
                        'weight': 2,
                        'fillOpacity': 1.0,
                        'radius': 5
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

            # print(all_fields)
            
            # 过滤掉tdt_开头的技术字段
            display_fields = [field for field in all_fields if not field.startswith('tdt_')]

            # print(display_fields)

            # 如果字段太多，只显示重要的几个
            # if len(display_fields) > 5:
            #     important_fields = ['省份', '城市', '园区', '经度', '纬度']
            #     display_fields = [f for f in important_fields if f in display_fields]
            
            
            # 创建对应的别名
            aliases = [f"{field}:" for field in display_fields]

            # print(aliases)
            
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
            
            # 过滤掉Point和MultiPoint类型的要素，只保留其他几何类型
            filtered_geojson = {
                'type': 'FeatureCollection',
                'features': []
            }
            
            for feature in geojson_data.get('features', []):
                geometry_type = feature.get('geometry', {}).get('type')
                if geometry_type != 'Point' and geometry_type != 'MultiPoint':
                    filtered_geojson['features'].append(feature)
            
            # 添加过滤后的GeoJSON数据到地图（不包含点数据）
            if filtered_geojson['features']:
                try:
                    folium.GeoJson(
                        filtered_geojson,
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
            
            # 添加图层控制（包括底图选择），默认收起
            folium.LayerControl(position='topright', collapsed=True).add_to(m)
            
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

