# GeoModelingZ/__init__.py

# 让用户可以直接从包导入
from .core import (
    say_hello, 
    get_current_time_str, 
    is_jupyter, 
    show_time_widget, 
    plot_simple_chart, 
    display_markdown, 
    create_geo_widget
)

# 定义包的版本号，非常重要！
__version__ = "0.0.1"