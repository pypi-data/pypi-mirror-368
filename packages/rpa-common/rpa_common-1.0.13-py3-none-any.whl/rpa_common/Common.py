import argparse
import hashlib
import importlib
import json
import os
import sys
import random
import socket
import time
from urllib.parse import quote
from datetime import datetime
from pathlib import Path, PureWindowsPath
from typing import Union, Dict, Literal, List, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Common():
    def __init__(self):
        super().__init__()

    def back(self, status=1, message='success', data={}):
        '''
        @Desc    : 返回数据
        @Author  : 钟水洲
        @Time    : 2024/05/31 10:02:40
        '''
        return {'status': status, 'message': message, 'data': data}

    def handleArgs(self, args):
        '''
        @Desc    : 处理参数
        @Author  : 钟水洲
        @Time    : 2024/05/31 10:02:48
        '''
        # 创建解析器对象
        parser = argparse.ArgumentParser(description="命令行参数解析")

        # 添加文件参数
        parser.add_argument("f", help="指定文件")

        # 添加可选参数
        parser.add_argument("-m", "--m", help="指定类")
        parser.add_argument("-a", "--a", help="指定方法")

        # 捕获所有剩余参数
        parser.add_argument("options", nargs='+', help="参数")

        # 解析命令行参数
        args = parser.parse_args()

        args.options = self.parseStr(args.options)

        return args

    def parseStr(self, args):
        '''
        @Desc    : 解析字符串
        @Author  : 钟水洲
        @Time    : 2024/05/31 10:02:55
        '''
        arg_dict = {}
        for arg in args:
            key, value = arg.split('=')
            arg_dict[key] = value
        return arg_dict

    def runJob(self, driver, shop_data, options):
        '''
        @Desc    : 运行脚本
        @Author  : 钟水洲
        @Time    : 2024/05/31 10:02:55
        '''
        # 分离模块路径和方法名
        task_job = options["task_job"]
        module_path, method_name = task_job.split('@')

        print("module_path", module_path)

        # 动态导入模块
        module = importlib.import_module(module_path)

        # 获取类和实例化（假设 OptimizerService 是一个类）
        class_name = module_path.rsplit('.', 1)[1]
        print("class_name", class_name)
        class_obj = getattr(module, class_name)
        instance = class_obj()  # 如果该类需要参数，要在这里传入
        print("method_name", method_name)

        # 解析参数
        params = options["params"]
        if isinstance(params, str):
            params = json.loads(params)

        # 调用方法并传递参数
        getattr(instance, method_name)(driver, shop_data, params)

    def resourcePath(self, relative_path):
        '''
        @Desc    : 获取资源文件的绝对路径
        @Author  : 钟水洲
        @Time    : 2024/05/31 10:03:28
        '''
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller 创建的临时文件夹
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def getCookie(self, driver, key):
        '''
        @Desc    : 获取指定Cookie值
        @Author  : 钟水洲
        @Time    : 2024/05/31 10:03:28
        '''
        # 获取所有 Cookie
        cookies = driver.get_cookies()
        # 查找
        value = None
        for cookie in cookies:
            if cookie['name'] == key:
                value = cookie['value']
                break

        print(f"{key}:", value)
        return value

    def is_port_free(self, port):
        '''
        @Desc    : 检查端口是否空闲
        @Author  : 钟水洲
        @Time    : 2025/07/09 11:14:13
        '''
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return True
            except socket.error:
                return False

    def get_free_port(self):
        '''
        @Desc    : 获取一个空闲端口
        @Author  : 钟水洲
        @Time    : 2025/07/09 11:14:20
        '''
        while True:
            port = random.randint(10000, 65535)  # 随机端口范围
            if self.is_port_free(port):
                return port

    def click_element(self, driver, selectors, timeout=0.1, wait_after=1):
        '''
        @Desc    : 通用点击函数
        @Author  : 钟水洲
        @Time    : 2025/07/11 11:08:13
        '''
        wait = WebDriverWait(driver, timeout)

        for by, selector in selectors:
            try:
                element = wait.until(EC.element_to_be_clickable((by, selector)))
                element.click()
                print(f"✅ 成功点击元素：{by} -> {selector}")
                time.sleep(wait_after)
                return True
            except:
                continue

        print("❌ 未找到可点击的元素")
        return False

    def input_text(self, driver, text, selectors, timeout=0.1, clear_first=True, wait_after=0.5):
        '''
        @Desc    : 通用输入函数
        @Author  : 钟水洲
        @Time    : 2025/07/11 11:09:47
        '''
        wait = WebDriverWait(driver, timeout)

        for by, selector in selectors:
            try:
                element = wait.until(EC.presence_of_element_located((by, selector)))
                if clear_first:
                    element.clear()
                element.send_keys(text)
                print(f"✅ 成功输入文本到元素：{by} -> {selector}")
                time.sleep(wait_after)
                return True
            except:
                continue

        print("❌ 未找到可输入的元素")
        return False

    # 将字典转换为URL查询参数字符串
    def object_to_params(self, params):
        """
        @Desc     : 将字典转换为URL查询参数字符串
        @Author   : 祁国庆
        @Time     : 2025/04/18 10:08:40
        @Params   :
            - params: 字典格式的params(转换后的结果不会包含?符号)
        """
        params_list = []

        for key, value in params.items():
            # 处理值为None的情况
            if value is None:
                params_list.append(quote(str(key)))
                continue

            # 处理列表/元组
            if isinstance(value, (list, tuple)):
                for item in value:
                    params_list.append(f"{quote(str(key))}={quote(str(item))}")
                continue

            # 处理字典/对象
            if isinstance(value, dict):
                params_list.append(f"{quote(str(key))}={quote(json.dumps(value))}")
                continue

            # 基本类型
            params_list.append(f"{quote(str(key))}={quote(str(value))}")
        if not params_list:
            return ''
        return '&'.join(params_list)

    def hash_encrypt(self, string, algorithm):
        """
        @Desc     : 整合hash哈希加密算法
        @Author   : 祁国庆
        @Time     : 2025/04/18 10:46:33
        @Params   :
            - string: 要加密的字符串
            - algorithm: 选择要使用的加密库（标准库）
        """
        # 支持的算法列表
        supported_algorithms = ['md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512',
                                'blake2b', 'blake2s',
                                'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512',
                                'shake_128', 'shake_256']
        # 检查算法是否支持
        if algorithm not in supported_algorithms:
            raise ValueError('不支持的算法')
        try:
            hash_obj = getattr(hashlib, algorithm)()
            hash_obj.update(string.encode('utf-8'))
            return hash_obj.hexdigest()
        except Exception as e:
            raise ValueError(f'加密发生错误: {e}')

    def load_template(self, path:str):
        """
        @Desc    : 读取文件
        @param   : path 文件路径
        @Author  : 黄豪杰
        @Time    : 2025/07/22 13:55:13
        """
        path = os.path.normpath(os.path.join(Path(__file__).resolve().parents[2], path))
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def print_(self, *args: any) -> None:
        """开发者测试专用 可代替print打印"""
        formatted_time = datetime.fromtimestamp(time.time()).strftime("%H:%M:%S.%f")[:-3]  # %Y/%m/%d %H:%M:%S.%f
        if len(args) > 1:
            label, *values = args
            type_str = "".join(f"[{type(v).__name__}]" for v in values)
            value_str = " ".join(f"[{v}]" for v in values)
            print(f'[{formatted_time}][{label}] | {type_str} -> {value_str}')
            return
        elif len(args) == 1:
            # 打印单数值
            print(f'[{formatted_time}][{type(args[0]).__name__}] -> [{args[0]}]')

    def lambda_set(self) -> dict:
        """
        @Desc     : lambda 集合
        @Author   : 祁国庆
        @Time     : 2025/07/23 18:06:53
            - date_to_timestamp: 将 %Y-%m-%d 转换为 10 位时间戳 列：fun('2025-06-09')
            - date_to_timestamp_fill:
                    转换 将【年-月-日】字符串转换为时间戳， _：年-月-日 | i：1000为13位时间戳 1为10位时间戳 | y：86399为[xxxx-xx-xx 23:59:59] 0为[xxxx-xx-xx 00:00:00]
                    列：fun(_='2025-06-09', i=1000, y=0)
        """
        return {
            'date_to_timestamp' : lambda _: int(datetime.strptime(_, '%Y-%m-%d').timestamp()),   #
            'date_to_timestamp_fill' : lambda _='2025-01-01', i=1000, y=86399: int((datetime.strptime(_, '%Y-%m-%d').timestamp() + y) * i)
        }

    def win_to_unix_path(self,path: str) -> str:
        """
        将给定路径（可能是 Windows 或 POSIX 风格）规范化为 POSIX（Linux）风格路径。
        """
        # 先让 os.path.normpath 规范路径（去除冗余）
        normalized = os.path.normpath(path)
        # 再利用 PureWindowsPath 转换为 POSIX 风格路径
        return PureWindowsPath(normalized).as_posix()