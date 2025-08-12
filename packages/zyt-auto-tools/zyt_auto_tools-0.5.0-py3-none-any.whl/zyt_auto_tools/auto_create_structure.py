# -*- coding: utf-8 -*-
"""
Project Name: zyt_auto_tools
File Created: 2025.01.26
Author: ZhangYuetao
File Name: auto_create_structure.py
Update: 2025.08.12
"""

import os
import argparse
import fnmatch
import sys
from pathlib import Path

# 默认忽略的目录和文件
DEFAULT_IGNORES = {
    # Python 相关
    '__pycache__', '*.pyc', '*.pyo', '*.pyd', '*.pyi',
    '*.egg-info', '*.dist-info', 'build', 'dist', 'site-packages',

    # 版本控制
    '.git', '.svn', '.hg', '.bzr', '.gitmodules',

    # IDE 和编辑器
    '.idea', '.vscode', '.vs', '.history', '.project', '.classpath',
    '.metadata', '.recommenders', '.ropeproject',

    # 虚拟环境
    'venv', 'env', '.env', 'virtualenv', 'conda', 'pipenv', 'poetry',

    # 包管理
    'node_modules', 'bower_components', 'jspm_packages', 'package-lock.json',
    'yarn.lock', 'pnpm-lock.yaml', 'requirements.txt', 'Pipfile', 'Pipfile.lock',

    # 构建工具
    'target', 'out', 'bin', 'obj', 'build', 'dist', 'lib', 'lib64', 'include',

    # 日志和缓存
    'logs', 'log', '*.log', '*.tmp', '*.bak', '*.swp', '*.swo', '*.swn',
    '*.cache', '*.class', '*.jar', '*.war', '*.ear',

    # 操作系统
    '.DS_Store', 'Thumbs.db', 'desktop.ini', '.Spotlight-V100', '.Trashes',
    '.fseventsd', '.VolumeIcon.icns', '.apdisk',

    # 其他
    '.mypy_cache', '.pytest_cache', '.coverage', '.tox', '.hypothesis',
    '.ipynb_checkpoints', '.jupyter', '.spyderproject', '.spyproject',
    '.ropeproject', '.vscode-test', '.vscode-server', '.vscode-remote',
    '.vscode-insiders', '.vscode-exploration', '.vscode-oss',
}


def load_gitignore(directory):
    """
    从项目目录加载 .gitignore 文件并返回忽略规则集合。

    :param directory: 项目目录。
    :return: 忽略规则集合。
    """
    gitignore_path = Path(directory) / '.gitignore'
    if not gitignore_path.is_file():
        return set()

    ignore_patterns = set()
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 忽略空行和注释
            if line and not line.startswith('#'):
                ignore_patterns.add(line)
    return ignore_patterns


def is_ignored(name, ignore_patterns):
    """
    检查文件或目录是否匹配忽略模式。

    :param name: 文件或目录名称。
    :param ignore_patterns: 忽略模式集合。
    :return: 是否匹配忽略模式。
    """
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(name, pattern):
            return True
    return False


def generate_text_tree(directory, output_file=None, ignore_patterns=None, use_gitignore=False, only_dirs=False):
    """
    生成文本结构树。

    :param directory: 目录路径。
    :param output_file: 输出文件路径。
    :param ignore_patterns: 忽略模式集合。
    :param use_gitignore: 是否使用 .gitignore 文件。
    """
    # 如果启用 use_gitignore，则替换默认忽略列表
    if use_gitignore:
        ignore_patterns = load_gitignore(directory) | (ignore_patterns or set())
    else:
        # 否则使用默认忽略列表和用户指定的忽略列表
        ignore_patterns = DEFAULT_IGNORES | (ignore_patterns or set())

    tree = []

    def build_tree(path, prefix=''):
        try:
            entries = sorted([
                e for e in os.listdir(path)
                if not is_ignored(e, ignore_patterns)
            ])
        except PermissionError:
            # 无权限访问时，添加提示，包含目录名称
            dirname = os.path.basename(path)
            tree.append(f"{prefix}└── **no_permission_dir（{dirname}）**/")
            return
        
        dirs = []
        files = []

        for entry in entries:
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                dirs.append(entry)
            elif not only_dirs:
                files.append(entry)

        # 文件夹优先
        all_entries = dirs + files

        for index, entry in enumerate(all_entries):
            full_path = os.path.join(path, entry)
            is_last = index == len(all_entries) - 1

            if os.path.isdir(full_path):
                tree.append(f"{prefix}{'└── ' if is_last else '├── '}{entry}/")
                new_prefix = prefix + ('    ' if is_last else '│   ')
                build_tree(full_path, new_prefix)
            else:
                tree.append(f"{prefix}{'└── ' if is_last else '├── '}{entry}")

    tree.append(os.path.basename(directory) + '/')
    build_tree(directory)

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(tree))
        print(f"✅ 文本结构图已保存至：{output_file}")
    else:
        print('\n'.join(tree))


def main():
    """
    主函数，用于命令行调用。
    """
    parser = argparse.ArgumentParser(description="自动生成项目结构图")
    parser.add_argument('-d', '--dir', default=os.getcwd(),
                        help="项目目录（默认当前目录）")
    parser.add_argument('-o', '--output',
                        help="输出文件路径（可选）")
    parser.add_argument('-i', '--ignore', nargs='+',
                        help="额外忽略的目录/文件（支持通配符，空格分隔）")
    parser.add_argument('--use-gitignore', action='store_true',
                        help="使用 .gitignore 文件中的规则替换默认忽略列表")
    parser.add_argument('--only-dirs', action='store_true',
                        help="仅生成文件夹结构，不包括文件")

    args = parser.parse_args()

    try:
        generate_text_tree(
            args.dir,
            output_file=args.output,
            ignore_patterns=set(args.ignore) if args.ignore else None,
            use_gitignore=args.use_gitignore,
            only_dirs=args.only_dirs
        )
    except Exception as e:
        print(f"❌ 错误：{str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
