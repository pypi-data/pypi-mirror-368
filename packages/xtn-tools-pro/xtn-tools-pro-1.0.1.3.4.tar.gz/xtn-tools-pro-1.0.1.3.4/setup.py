#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 说明：
#    setup
# History:
# Date          Author    Version       Modification
# --------------------------------------------------------------------------------------------------
# 2024/4/17    xiatn     V00.01.000    新建
# --------------------------------------------------------------------------------------------------
import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="xtn-tools-pro",  # 模块名称
    version="1.0.1.3.4",  # 版本
    author="xtn",  # 作者
    author_email="czw011122@gmail.com",  # 作者邮箱
    description="xtn 开发工具",  # 模块简介
    long_description=long_description,  # 模块详细介绍
    long_description_content_type="text/markdown",  # 模块详细介绍格式
    packages=setuptools.find_packages(include=["xtn_tools_pro", "xtn_tools_pro.*"]),  # 自动找到项目中导入的模块
    include_package_data=True,  # 确保非 Python 文件（如模板文件）也被包含
    package_data={
        "xtn_tools_pro.flask_demo": ["templates/*", "templates/app/*"],
    },
    # 模块相关的元数据(更多描述信息)
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    # 依赖模块
    install_requires=[
        "pymongo",
        "redis",
        "pymysql",
        "dbutils",
        "colorlog",
        "requests",
        "Faker",
        "PyJWT",
        "tqdm",
        "fabric",
        "pyotp",
        # "moviepy",
        "pycryptodome",
        "requests",
        "psutil"
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'xtn_tools_pro=xtn_tools_pro.flask_demo.cli:main',
        ],
    }
)
