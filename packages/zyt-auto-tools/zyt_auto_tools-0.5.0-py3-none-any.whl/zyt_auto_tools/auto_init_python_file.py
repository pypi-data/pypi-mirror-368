# -*- coding: utf-8 -*-
"""
Project Name: zyt_auto_tools
File Created: 2023.12.31
Author: ZhangYuetao
File Name: auto_init_python_file.py
Update: 2025.08.12
"""

import os
import argparse
from datetime import datetime


def create_py_file(file_name, author, target_dir=None):
    """
    创建一个 .py 文件，并填充初始内容

    :param file_name: 要创建的文件名（包括 .py 后缀）
    :param author: 作者名
    :param target_dir: 目标文件夹路径（可选，默认为当前目录）
    """
    new_dir = False
    
    # 检查文件名是否以 .py 结尾，如果没有则自动添加
    if not file_name.endswith(".py"):
        file_name += ".py"

    # 如果没有指定目标文件夹，则使用当前目录
    if target_dir is None:
        target_dir = os.getcwd()
    else:
        # 如果目标文件夹不存在，则初始化创建python文件夹
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            if file_name != "__init__.py":
                new_dir = True

    # 获取当前工作目录的名称作为项目名称
    project_name = os.path.basename(os.getcwd())

    # 获取当前日期
    current_date = datetime.now().strftime("%Y.%m.%d")

    # 初始内容模板
    content = f"""# -*- coding: utf-8 -*-
\"""
Project Name: {project_name}
File Created: {current_date}
Author: {author}
File Name: {file_name}
Update: {current_date}
\"""
"""

    # 拼接目标文件路径
    file_path = os.path.join(target_dir, file_name)

    # 创建文件并写入内容
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

    print(f"文件 '{file_path}' 创建成功！")
    
    return new_dir


def main():
    """
    主函数，用于命令行调用
    """
    # 创建 ArgumentParser 对象
    parser = argparse.ArgumentParser(description="自动初始化创建一个 .py 文件，并填充初始内容")

    # 从环境变量中读取默认作者名，如果未设置则使用 'ZhangYuetao'
    default_author = os.getenv("DEFAULT_AUTHOR", "ZhangYuetao")

    # 添加命令行参数
    parser.add_argument("file_name", type=str, 
                        help="要创建的文件名（包括 .py 后缀）")
    parser.add_argument("-a", "--author", type=str, default=default_author,
                        help="作者名（默认为环境变量 DEFAULT_AUTHOR 或 'ZhangYuetao'）")
    parser.add_argument("-d", "--dir", type=str, default=None, 
                        help="目标文件夹路径（可选，默认为当前目录）")

    # 解析命令行参数
    args = parser.parse_args()

    # 调用函数创建文件
    new_dir = create_py_file(args.file_name, args.author, args.dir)
    if new_dir:
        create_py_file("__init__.py", args.author, args.dir)


if __name__ == "__main__":
    main()
