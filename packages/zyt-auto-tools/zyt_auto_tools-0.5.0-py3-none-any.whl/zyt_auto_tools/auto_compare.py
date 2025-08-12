# -*- coding: utf-8 -*-
"""
Project Name: zyt_auto_tools
File Created: 2025.08.07
Author: ZhangYuetao
File Name: auto_compare.py
Update: 2025.08.12
"""

import re
import sys
import argparse


def parse_tree_txt_to_paths(file_path):
    """
    解析树状文本文件，返回文件路径列表。

    :param file_path: 树状文本文件路径。
    :return: 文件路径列表。
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        first_line = f.readline()
        lines = [line.rstrip('\n') for line in f if line.strip()]

    base_indent_pattern = re.compile(r"^[\s│]*[├└]── ")
    stack = []
    result = []

    for line in lines:
        # 跳过最顶层目录（如 auto_testing/）
        if not base_indent_pattern.search(line):
            continue

        # 获取当前缩进级别（以 ├── 或 └── 前的字符长度为基础）
        indent = len(line) - len(line.lstrip(' │'))

        # 解析出当前的文件或文件夹名
        name = base_indent_pattern.sub('', line).strip()

        # 弹出比当前缩进更深的路径
        while stack and stack[-1][0] >= indent:
            stack.pop()

        # 构造当前路径
        current_path = '/'.join(item[1] for item in stack + [(indent, name)])
        result.append(current_path)

        # 如果是目录，压入栈（判断方式：以 `/` 结尾）
        if name.endswith('/'):
            stack.append((indent, name.strip('/')))

    return first_line, result


def _get_diff_list(list_a, list_b):
    """
    获取两个列表的差异，返回差异列表。

    :param list_a: 待比较列表 A。
    :param list_b: 被比较列表 B。
    :return: 差异列表。
    """
    set_b = set(list_b)
    diff_list = [a for a in list_a if a not in set_b]

    return diff_list


def build_tree_from_paths(paths, root_name="root"):
    """
    从文件路径列表构建树状结构。

    :param paths: 文件路径列表。
    :param root_name: 根节点名称。
    :return: 树状结构字符串。
    """
    from collections import defaultdict

    # 构建树结构的嵌套字典
    tree = lambda: defaultdict(tree)
    root = tree()

    # 插入路径
    for path in sorted(paths):
        parts = [p for p in path.strip("/").split("/") if p]
        current = root
        for part in parts:
            current = current[part + "/"]

    # 格式化为树状结构字符串
    def _format_tree(node, prefix=""):
        """
        格式化节点为树状结构字符串。

        :param node: 节点。
        :param prefix: 前缀。
        :return: 树状结构字符串。
        """
        lines = []
        items = list(node.items())
        for i, (key, child) in enumerate(items):
            connector = "└── " if i == len(items) - 1 else "├── "
            lines.append(prefix + connector + key)
            if child:
                extension = "    " if i == len(items) - 1 else "│   "
                lines.extend(_format_tree(child, prefix + extension))
        return lines

    # 添加 root 节点
    return root_name + "\n".join(_format_tree(root))


def compare_tree_texts(compare_texts, compared_texts, output_file=None):
    """
    比较两个树状文本文件，输出差异列表。

    :param compare_texts: 要比较的树状文本文件路径列表。
    :param compared_texts: 被比较的树状文本文件路径列表。
    :param output_file: 输出文件路径。
    """
    all_outputs = []

    for compare_text in compare_texts:
        compared_list = []
        for compared_text in compared_texts:
            compared_list.extend(parse_tree_txt_to_paths(compared_text)[1])
        
        first_line, compare_list = parse_tree_txt_to_paths(compare_text)

        diff_list = _get_diff_list(compare_list, compared_list)
        
        diff_tree = build_tree_from_paths(diff_list, first_line)
        all_outputs.append(diff_tree)
    
    final_output = "\n\n".join(all_outputs)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_output)
        print(f"✅ 文本结构图已保存至：{output_file}")
    else:
        print(final_output)


def main():
    """
    命令行入口函数。
    """
    parser = argparse.ArgumentParser(description="比较两个或多个树状文本文件的差异")
    parser.add_argument(
        "-c", "--compare",
        nargs="+",
        required=True,
        help="要比较的树状文本文件路径（一个或多个）"
    )
    parser.add_argument(
        "-b", "--base",
        nargs="+",
        required=True,
        help="被比较的树状文本文件路径（一个或多个）"
    )
    parser.add_argument(
        "-o", "--output",
        help="输出文件路径（可选，不填则打印到终端）"
    )

    args = parser.parse_args()

    try:
        compare_tree_texts(args.compare, args.base, args.output)
    except Exception as e:
        print(f"❌ 错误：{str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
