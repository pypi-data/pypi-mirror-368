import setuptools #导入setuptools打包工具
 
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
 
setuptools.setup(
    name="GeoModelingZ",
    version="0.0.6",
    author="Zhoums",
    author_email="18652950852@163.com",
    description="地理建模与可视化工具库",
    long_description=long_description, 
    long_description_content_type="text/markdown",
    url="https://github.com/Zhoums396/GeoModelingZ",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires='>=3.6',
    install_requires=[
        'numpy',
        'matplotlib',
        'ipython',
        'folium',
    ],
    extras_require={
        'jupyter': [
            'ipywidgets>=7.0.0',
            'jupyterlab_widgets',
        ],
    },
)