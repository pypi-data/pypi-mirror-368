# -*- coding: utf-8 -*-
"""
Project Name: zyt_auto_tools
File Created: 2025.01.02
Author: ZhangYuetao
File Name: setup.py
Update: 2025.08.12
"""

from setuptools import setup, find_packages

# 读取 README.md 文件内容作为长描述
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# noinspection PyInterpreter
setup(
    name="zyt_auto_tools",
    version="0.5.0",
    author="ZhangYuetao",
    author_email="zhang894171707@gmail.com",
    description="A collection of automation tools for Python projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VerySeriousMan/zyt_auto_tools",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "zyt_auto_tools": [
            "templates/init/*.txt",
            "templates/software/*.txt",
            "templates/software/network/*.txt",
            "templates/software/ui/*.txt",
            "templates/software/ui/main/*.txt",
            "templates/software/settings/*.txt",
            "templates/crawler/*.txt",
            "templates/crawler/settings/*.txt",
            "templates/crawler/settings/lake/*.txt",
            "templates/crawler/settings/cookies/*.txt",
            "templates/crawler/spiders/*.txt",
            "templates/crawler/plugins/*.txt",
            "templates/crawler/utils/*.txt",
            "templates/spiders/*.txt",
            "templates/spiders/settings/*.txt",
            "templates/spiders/settings/lake/*.txt",
            "templates/spiders/web_spiders/*.txt",
            "templates/spiders/web_spiders/spiders/*.txt",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[],
    entry_points={
        "console_scripts": [
            "auto-generate-init=zyt_auto_tools.auto_generate_init:main",
            "auto-init-python-file=zyt_auto_tools.auto_init_python_file:main",
            "auto-update-ctime=zyt_auto_tools.auto_update_ctime:main",
            "auto-create-structure=zyt_auto_tools.auto_create_structure:main",
            "auto-init-python-dir=zyt_auto_tools.auto_init_python_dir:main",
            "auto-compare=zyt_auto_tools.auto_compare:main",
        ],
    },
)
