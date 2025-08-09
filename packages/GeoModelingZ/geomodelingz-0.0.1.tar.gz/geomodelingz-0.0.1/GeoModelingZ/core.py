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