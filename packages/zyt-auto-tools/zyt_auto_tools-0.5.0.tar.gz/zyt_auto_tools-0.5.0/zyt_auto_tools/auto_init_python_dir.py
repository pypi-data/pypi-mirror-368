# -*- coding: utf-8 -*-
"""
Project Name: zyt_auto_tools
File Created: 2025.06.06
Author: ZhangYuetao
File Name: auto_init_python_dir.py
Update: 2025.08.12
"""

import os
import argparse
from datetime import datetime
import importlib.resources as pkg_resources

import zyt_auto_tools.templates


def create_project_structure(author, project_type, target_dir=None):
    """
    创建项目结构（文件夹 + 多个初始化文件），每个文件先写入 base_header，再追加模板代码（如存在）

    :param author: 作者名
    :param project_type: 类型，可选 'software' 或 'crawler'
    :param target_dir: 项目路径，默认当前目录
    """

    if target_dir is None:
        target_dir = os.getcwd()

    os.makedirs(target_dir, exist_ok=True)

    # 获取当前工作目录的名称作为项目名称
    project_name = os.path.basename(os.getcwd())
    current_date = datetime.now().strftime("%Y.%m.%d")

    def base_header(filename):
        return f"""# -*- coding: utf-8 -*-
\"\"\"
Project Name: {project_name}
File Created: {current_date}
Author: {author}
File Name: {filename}
Update: {current_date}
\"\"\"
"""

    file_map = {
        "init": ["__init__.py"],
        "software": ["main.py", "config.py", "utils.py", 
                     os.path.join('settings', 'secret.toml'),os.path.join('settings', 'software_infos.toml'), os.path.join('settings', 'xey.ico'),
                     os.path.join('network', '__init__.py'), os.path.join('network', 'server_connect.py'), os.path.join('network', 'software_update.py'), 
                     os.path.join('ui', '__init__.py'), os.path.join('ui', 'feedback.py'), os.path.join('ui', 'feedback.ui'),
                     os.path.join('ui', 'main', '__init__.py'), os.path.join('ui', 'main', 'main_window.py'), os.path.join('ui', 'main', 'feedback_main.py')
                     ],
        "crawler": ["config.py", "logger.py", "start_crawler.py",
                    os.path.join('settings', 'basic_setting.toml'), os.path.join('settings', 'chrome_setting.toml'),
                    os.path.join('settings', 'lake', 'proxies.txt'), os.path.join('settings', 'lake', 'user_agents.txt'), 
                    os.path.join('settings', 'cookies', 'load_cookies.toml'),
                    os.path.join('spiders', '__init__.py'), os.path.join('spiders', 'example.py'),
                    os.path.join('utils', '__init__.py'), os.path.join('utils', 'generic_utils.py'), os.path.join('utils', 'log_utils.py'),
                    os.path.join('plugins', '__init__.py'), os.path.join('plugins', 'open_chrome.py'), os.path.join('plugins', 'proxy_test.py')
                    ],
        "spiders": ["proxy_test.py", "config.py", "utils.py", "start_crawler.py", "scrapy.cfg",
                    os.path.join('settings', 'basic_settings.toml'), 
                    os.path.join('settings', 'lake', 'proxies.txt'), os.path.join('settings', 'lake', 'user_agents.txt'),
                    os.path.join('web_spiders', '__init__.py'), os.path.join('web_spiders', 'items.py'), os.path.join('web_spiders', 'middlewares.py'),
                    os.path.join('web_spiders', 'pipelines.py'), os.path.join('web_spiders', 'settings.py'),
                    os.path.join('web_spiders', 'spiders', '__init__.py'), os.path.join('web_spiders', 'spiders', 'example.py')
                    ]
    }
    if project_type is None:
        project_type = "init"

    if project_type not in file_map:
        raise ValueError(f"未知项目类型: {project_type}")
    
    if target_dir:
        file_map[project_type].append("__init__.py")

    for filename in file_map[project_type]:
        file_path = os.path.join(target_dir, filename)
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        template_pkg = f"zyt_auto_tools.templates.{project_type}"
        template_file = filename + ".txt"

        # 构建最终文件内容
        content = base_header(os.path.basename(filename))
        
        if 'xey.ico' in filename:
            with pkg_resources.files(template_pkg).joinpath(template_file).open("rb") as tpl:
                template_content = tpl.read()
        else:
            with pkg_resources.files(template_pkg).joinpath(template_file).open("r", encoding="utf-8") as tpl:
                template_content = tpl.read()  
            content += template_content

        # 写入到文件中
        if file_path.endswith('.py'):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        else:
            if 'xey.ico' in filename:
                with open(file_path, 'wb') as f:
                    f.write(template_content)
            else:
                if 'secret.toml' in filename:
                    file_path = file_path.replace('secret', '.secret')
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(template_content)

        print(f"初始化文件 '{file_path}' 创建成功！")

    print(f"项目文件夹 '{target_dir}' 创建完成，类型：{project_type}")


def main():
    """
    主函数，用于命令行调用
    """
    # 创建 ArgumentParser 对象
    parser = argparse.ArgumentParser(description="自动初始化创建python项目文件夹，并填充初始内容")

    # 从环境变量中读取默认作者名，如果未设置则使用 'ZhangYuetao'
    default_author = os.getenv("DEFAULT_AUTHOR", "ZhangYuetao")

    # 添加命令行参数
    parser.add_argument("-a", "--author", type=str, default=default_author,
                        help="作者名（默认为环境变量 DEFAULT_AUTHOR 或 'ZhangYuetao'）")
    parser.add_argument("-t", "--type", type=str, default=None, choices=[None, "software", "crawler", "spiders"],
                        help="项目类型：None（默认）表示单__init__.py文件的初始化python文件夹，software 表示软件项目，crawler 表示爬虫项目，spiders 表示爬虫项目(scrapy框架)")
    parser.add_argument("-d", "--dir", type=str, default=None, 
                        help="目标文件夹路径（可选，默认为当前目录）")
    
    # 解析命令行参数
    args = parser.parse_args()

    create_project_structure(args.author, args.type, args.dir)


if __name__ == "__main__":
    main()
