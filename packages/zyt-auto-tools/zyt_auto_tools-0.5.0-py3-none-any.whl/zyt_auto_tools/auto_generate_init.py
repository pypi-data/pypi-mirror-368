# -*- coding: utf-8 -*-
"""
Project Name: zyt_auto_tools
File Created: 2023.12.30
Author: ZhangYuetao
File Name: auto_generate_init.py
Update: 2025.07.07
"""

import sys
import os
import glob
import re
import ast
from datetime import datetime
import argparse


def get_project_name(use_files):
    """
    从 文件中获取项目名称。

    :param use_files: 文件路径列表。
    :return: 项目名称。
    """
    for file_path in use_files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            match = re.search(r"Project Name: (.*)", content)
            if match:
                return match.group(1).strip()
    return os.path.basename(os.getcwd())  # 如果未找到，则使用项目根目录的名称


def extract_top_level_defs(file_path, type="public"):
    """
    从 Python 文件中提取顶层函数名和类名（不包括类内函数）。

    :param file_path: 文件路径。
    :param type: 导入类型。
    :return: 顶层类与函数列表。
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 解析文件的抽象语法树（AST）
    tree = ast.parse(content)

    # 提取所有函数与类的定义
    functions = []
    classes = []

    # 只遍历顶层节点
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            if type == "all" or not node.name.startswith("_"):
                functions.append(node.name)
        elif isinstance(node, ast.ClassDef):
            if type == "all" or not node.name.startswith("_"):
                classes.append(node.name)

    return classes + functions

def generate_init_file_with_name(file_dir, includes, type, project_name, file_created_date, author):
    """
    生成顶层函数与类内容的__init__.py文件。

    :param file_dir: 文件目录路径。
    :param includes: 指定包含内容的文件名。
    :param type: 导入类型。
    :param project_name: 项目名称。
    :param file_created_date: 文件创建日期。
    :param author: 作者名。
    """
    # 获取当前日期
    today = datetime.now().strftime("%Y.%m.%d")

    # 删除旧的 __init__.py 文件（如果存在），并读取其 File Created 日期
    init_file_path = os.path.join(file_dir, "__init__.py")
    if os.path.exists(init_file_path):
        # 读取旧文件的 File Created 日期
        with open(init_file_path, "r", encoding="utf-8") as f:
            content = f.read()
            match = re.search(r"File Created: (\d{4}\.\d{2}\.\d{2})", content)
            if match:
                file_created_date = match.group(1)
        # 删除旧文件
        os.remove(init_file_path)
        print("旧的 __init__.py 文件已删除！")

    # 获取文件目录下所有包含includes的文件
    use_files = glob.glob(os.path.join(file_dir, includes))
    # 过滤掉 "__init__.py"
    use_files = [f for f in use_files if not f.endswith("__init__.py")]

    # 提取模块名（去掉 .py 后缀）
    modules = {os.path.basename(f)[:-3]: f"{os.path.basename(f)[:-3]} 模块中的函数" for f in use_files}

    # 生成导入部分和 __all__ 列表
    init_content = f'''# -*- coding: utf-8 -*-
#
# Auto created by: auto_generate_init.py
#
"""
Project Name: {project_name}
File Created: {file_created_date}
Author: {author}
File Name: __init__.py
Update: {today}
"""

'''
    # 将项目根目录添加到 sys.path
    project_root = os.path.dirname(file_dir)
    if project_root not in sys.path:
        sys.path.append(project_root)

    # 生成导入部分
    for module_name, comment in modules.items():
        file_path = os.path.join(file_dir, f"{module_name}.py")
        if os.path.exists(file_path):
            top_levels = extract_top_level_defs(file_path, type)
            if top_levels:  # 如果当前模块有类或函数，才生成导入部分
                init_content += f"# 导入 {comment}\n"
                init_content += f"from .{module_name} import (\n"
                for top_level in top_levels:
                    init_content += f"    {top_level},\n"
                init_content += ")\n\n"

    # 生成 __all__ 列表
    init_content += "# 定义包的公共接口\n"
    init_content += "__all__ = [\n"
    for module_name, comment in modules.items():
        file_path = os.path.join(file_dir, f"{module_name}.py")
        if os.path.exists(file_path):
            top_levels = extract_top_level_defs(file_path, type)
            if top_levels:  # 如果当前模块有类或函数，才生成 __all__ 部分
                init_content += f"    # {module_name}\n"
                for top_level in top_levels:
                    init_content += f"    '{top_level}',\n"
        init_content += "\n"
    init_content += "]\n"

    # 将生成的内容写入 __init__.py
    with open(init_file_path, "w", encoding="utf-8") as f:
        f.write(init_content)

    print("新的 __init__.py 文件已生成！")


def generate_init_file_with_star(file_dir, includes, project_name, file_created_date, author):
    """
    生成通配导入内容的__init__.py 文件。

    :param file_dir: 文件目录路径。
    :param includes: 指定包含内容的文件名。
    :param project_name: 项目名称。
    :param file_created_date: 文件创建日期。
    :param author: 作者名。
    """
    # 获取当前日期
    today = datetime.now().strftime("%Y.%m.%d")

    # 删除旧的 __init__.py 文件（如果存在），并读取其 File Created 日期
    init_file_path = os.path.join(file_dir, "__init__.py")
    if os.path.exists(init_file_path):
        # 读取旧文件的 File Created 日期
        with open(init_file_path, "r", encoding="utf-8") as f:
            content = f.read()
            match = re.search(r"File Created: (\d{4}\.\d{2}\.\d{2})", content)
            if match:
                file_created_date = match.group(1)
        # 删除旧文件
        os.remove(init_file_path)
        print("旧的 __init__.py 文件已删除！")

    # 获取文件目录下所有包含includes的文件
    use_files = glob.glob(os.path.join(file_dir, includes))
    # 过滤掉 "__init__.py"
    use_files = [f for f in use_files if not f.endswith("__init__.py")]

    # 提取模块名（去掉 .py 后缀）
    modules = {os.path.basename(f)[:-3]: f"{os.path.basename(f)[:-3]} 模块" for f in use_files}

    # 生成导入部分和 __all__ 列表
    init_content = f'''# -*- coding: utf-8 -*-
#
# Auto created by: auto_generate_init.py
#
"""
Project Name: {project_name}
File Created: {file_created_date}
Author: {author}
File Name: __init__.py
Update: {today}
"""

'''
    # 将项目根目录添加到 sys.path
    project_root = os.path.dirname(file_dir)
    if project_root not in sys.path:
        sys.path.append(project_root)

    # 生成导入部分
    for module_name, comment in modules.items():
        init_content += f"# 导入 {comment}\n"
        init_content += f"from .{module_name} import *\n"

    # 将生成的内容写入 __init__.py
    with open(init_file_path, "w", encoding="utf-8") as f:
        f.write(init_content)

    print("新的 __init__.py 文件已生成！")


def main():
    """
    主函数，用于命令行调用。
    """
    # 获取当前日期
    today = datetime.now().strftime("%Y.%m.%d")

    # 获取当前工作目录作为项目根目录
    project_root = os.getcwd()

    # 创建 ArgumentParser 对象
    parser = argparse.ArgumentParser(description="自动定义__init__.py")

    # 从环境变量中读取默认作者名，如果未设置则使用 'ZhangYuetao'
    default_author = os.getenv("DEFAULT_AUTHOR", "ZhangYuetao")

    # 添加命令行参数
    parser.add_argument("-d", "--dir", type=str, default="utils", help="文件夹名（默认为utils文件夹）")
    parser.add_argument("-i", "--include", type=str, default="*.py", help="指定包含内容的文件名（默认为以.py结尾的文件）")
    parser.add_argument("-a", "--author", type=str, default=default_author,
                        help="作者名（默认为环境变量 DEFAULT_AUTHOR 或 'ZhangYuetao'）")
    parser.add_argument("-t", "--type", type=str, default="public", help="__init__文件内容(public:非_开头的顶层类和函数;all:全部顶层类和函数;star:通配导入,默认public)")

    # 解析命令行参数
    args = parser.parse_args()

    # 获取目录路径
    file_dir = os.path.join(project_root, args.dir)
    if not os.path.exists(file_dir):
        print(f"错误：目录 '{file_dir}' 不存在！")
        return

    # 获取项目名称
    use_files = glob.glob(os.path.join(file_dir, args.include))
    # 过滤掉 "__init__.py"
    use_files = [f for f in use_files if not f.endswith("__init__.py")]
    if not use_files:
        print(f"错误：搜索指定haven内容为空！")
        return

    project_name = get_project_name(use_files)

    # 生成 __init__.py 文件
    if args.type == 'public' or args.type == 'all':
        generate_init_file_with_name(file_dir, args.include, args.type, project_name, today, args.author)
    elif args.type == 'star':
        generate_init_file_with_star(file_dir, args.include, project_name, today, args.author)
    else:
        print(f'类型{args.type}不存在，请输入正确的类型(public:非_开头的顶层类和函数;all:全部顶层类和函数;star:通配导入,默认public)！')
        return


if __name__ == "__main__":
    main()
