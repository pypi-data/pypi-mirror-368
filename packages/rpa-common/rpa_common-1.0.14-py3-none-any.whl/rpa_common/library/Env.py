import json
import subprocess
import os
import shutil
import sys
import platform
from rpa_common import Common

common = Common()

class Env():
    def __init__(self):
        super().__init__()

        # 判断系统，只有 Windows 才调用安装方法
        if sys.platform.startswith('win'):
            self.install_chrome()
        else:
            print("非 Windows 系统，跳过安装谷歌浏览器")

    def install_chrome(self):
        '''
        @Desc    : 安装谷歌浏览器
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("检查 Chrome ...")

        if self.is_chrome_installed():
            print("Chrome 已安装，跳过安装。")
            return

        # 判断系统版本
        system = platform.system()
        release = platform.release()
        version = platform.version()

        if '2012' in release or '6.3' in version:
            installer = "109.exe"
        else:
            installer = "136.exe"

        installer_path = common.resourcePath(f"./env/chrome/exe/{installer}")

        print(f"开始安装 Chrome ({installer}) ...")
        subprocess.run([installer_path, '/silent', '/install'], shell=True)
        print("Chrome 安装完成！")

    def is_chrome_installed(self):
        '''
        @Desc    : 检查注册表，判断是否安装了 Google Chrome
        @Author  : 钟水洲
        @Time    : 2025/06/02 11:51:55
        '''
        import winreg
        registry_paths = [
            r"SOFTWARE\Google\Chrome\BLBeacon",                       # 一般在 64 位系统中使用
            r"SOFTWARE\WOW6432Node\Google\Chrome\BLBeacon",           # 32 位 Chrome 安装在 64 位系统
        ]

        for reg_path in registry_paths:
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                    version, _ = winreg.QueryValueEx(key, "version")
                    if version:
                        print(f"检测到已安装 Chrome,版本: {version}")
                        return True
            except FileNotFoundError:
                continue
        return False