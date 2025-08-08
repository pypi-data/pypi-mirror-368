# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='rpa_temu',  # 包的名字
    version='1.0.3',  # 包的版本
    packages=find_packages(),  # 自动寻找包中的模块
    install_requires=[  # 依赖的其他包
        "beautifulsoup4==4.13.4",
        "chardet==5.2.0",
        "mitmproxy==8.0.0",
        "pandas==2.0.3",
        "psutil==5.8.0",
        "pyotp==2.4.0",
        "pytz==2025.2",
        "selenium==4.27.1",
        "undetected_chromedriver==3.5.5",
    ],
    author='Zhongshuizhou',
    author_email='zhongshuizhou@qq.com',
    description='RPA automated execution program for Temu',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://pypi.org/project/rpa-temu/',
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',  # 支持的Python版本
)
