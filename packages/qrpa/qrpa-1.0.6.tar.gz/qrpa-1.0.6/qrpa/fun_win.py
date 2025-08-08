import os
import win32com.client

from .fun_base import log

def find_software_install_path(app_keyword: str):
    """从开始菜单或桌面查找指定软件的安装路径"""
    possible_dirs = [
        os.environ.get('PROGRAMDATA', '') + r'\Microsoft\Windows\Start Menu\Programs',
        os.environ.get('APPDATA', '') + r'\Microsoft\Windows\Start Menu\Programs',
        os.environ.get('USERPROFILE', '') + r'\Desktop',
        os.environ.get('PUBLIC', '') + r'\Desktop'
    ]

    shell = win32com.client.Dispatch("WScript.Shell")

    for base_dir in possible_dirs:
        for root, _, files in os.walk(base_dir):
            for file in files:
                if file.lower().endswith('.lnk') and app_keyword.lower() in file.lower():
                    lnk_path = os.path.join(root, file)
                    try:
                        shortcut = shell.CreateShortcut(lnk_path)
                        target_path = shortcut.Targetpath
                        if os.path.exists(target_path):
                            return target_path
                    except Exception as e:
                        continue

    log(f'未能查找到{str}安装位置')
    return None
