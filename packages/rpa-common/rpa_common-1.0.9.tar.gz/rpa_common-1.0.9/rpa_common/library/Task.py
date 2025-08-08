import json
import gc
import requests
import time
import threading
import tempfile
import traceback
import sys
import os
from pathlib import Path
from rpa_common.Common import Common
from rpa_common.library.Chrome import Chrome
from rpa_common.request.ShopRequest import ShopRequest
from rpa_common.request.TaskRequest import TaskRequest
from rpa_tiktok.service.TiktokService import TiktokService
from rpa_lazada.service.LazadaService import LazadaService
from rpa_temu.service import TemuService

common = Common()
chrome = Chrome()
shopRequest = ShopRequest()
taskRequest = TaskRequest()
tiktokService = TiktokService()
lazadaService = LazadaService()
temuService = TemuService()

class Task():
    def __init__(self):
        super().__init__()

    def run(self, options):
        '''
        @Desc    : 运行
        @Author  : 钟水洲
        @Time    : 2025/05/29 14:21:14
        '''
        driver = None
        v2ray = None
        stop_event = None
        monitor_thread = None

        try:
            # 关闭超时进程
            chrome.closeTimeoutProcess()

            # 获取店铺详情
            res = shopRequest.getDetail(options)
            if res['code'] != 1:
                print(res['msg'])
                return common.back(0, res['msg'])
            shop_data = res['data']

            # 启动v2ray
            listen_port = common.get_free_port()
            v2ray = chrome.run_V2Ray(shop_data, listen_port)
            print(f"✅ v2ray 已启动，本地监听 {listen_port}")

            # 指定用户目录
            shop_global_id = shop_data['shop_global_id']
            root_dir = Path(__file__).resolve().parents[2]
            user_data_dir = os.path.join(root_dir, "cache", "chrome", "user", str(shop_global_id))
            print("user_data_dir", user_data_dir)  # 临时目录路径

            # 启动驱动
            driver = chrome.start_driver(shop_data, listen_port, user_data_dir)

            # 监听新标签页
            known_handles = set(driver.window_handles)
            stop_event = threading.Event()
            monitor_thread = threading.Thread(
                target=chrome.monitorNewTabs,
                args=(driver, shop_data, known_handles, stop_event),
                daemon=True
            )
            monitor_thread.start()

            # 指纹检测
            chrome.getFingerprint(driver, shop_data)

            # 登录
            res = self.login(driver, options, shop_data)
            if res['status'] != 1:
                print(res['message'])
                return common.back(0, res['message'])

            # 循环任务
            self.loop_task(driver, options, shop_data)

        finally:
            # 停止监听新标签页线程
            if stop_event:
                stop_event.set()

            if monitor_thread:
                monitor_thread.join()

            # 关闭 driver
            if driver:
                driver.quit()
                time.sleep(1)

            # 关闭 v2ray
            if v2ray:
                v2ray.kill()
                time.sleep(1)

            # 垃圾回收
            gc.collect()

    def login(self, driver, options, shop_data):
        '''
        @Desc    : 登录
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("登录")

        platform = options['platform']

        if platform == 'tiktok':
            # 登录
            res = tiktokService.login(driver, shop_data, options)
            if res['status'] != 1:
                print(res['message'])
                return common.back(0, res['message'])
        elif platform == 'lazada':
            # 登录
            res = lazadaService.login(driver, shop_data, options)
            if res['status'] != 1:
                print(res['message'])
                return common.back(0, res['message'])
        elif platform == 'temu':
            temuService.login(driver, shop_data, options)
        else:
            return common.back(0, '平台不支持')

        return common.back(1, "登录成功")

    def loop_task(self, driver, options, shop_data):
        '''
        @Desc    : 循环任务
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("循环任务开始")

        while True:
            res = taskRequest.getShopTask(options)  # 获取任务
            if res['code'] != 1:
                print(f"任务失败: {res['msg']}，停止循环任务")
                return common.back(0, res['msg'])  # 任务失败时返回，并停止循环

            task_params = res['data']  # 获取任务数据

            # 执行任务
            print("任务执行中...")
            self.run_task(driver, task_params, shop_data)

            time.sleep(0.1)

    def run_task(self, driver, options, shop_data):
        '''
        @Desc    : 执行任务
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("执行任务")

        # 记录开始时间
        start_time = time.time()

        try:
            # 默认参数
            default_params = options["params"]
            if isinstance(default_params, str):
                default_params = json.loads(default_params)

            # 获取任务参数
            res = taskRequest.getTask(default_params)
            if res['code'] != 1:
                return common.back(0, res['msg'])
            task_data = res['data']

            # 任务参数
            task_params = task_data['params']

            # 合并参数
            params = {**default_params, **task_params}
            options['params'] = params

            # 调用脚本
            common.runJob(driver, shop_data, options)

            # 计算运行时长（秒）
            run_duration = time.time() - start_time
            params['run_duration'] = run_duration
            print(f"任务用时：{run_duration}秒")

            # 完成任务
            taskRequest.end(params)

        except Exception as e:
            try:
                exc_type, exc_obj, tb = sys.exc_info()  # 解包
                # 获取完整 traceback 栈
                tb_list = traceback.extract_tb(tb)
            except Exception:
                exc_obj = None
                tb_list = None

            # 失败信息
            try:
                error_data = e.error_data()
            except Exception:
                if tb_list:
                    last_call = tb_list[-1]  # 最底层的异常点
                    file_path = last_call.filename
                    line_no = last_call.lineno
                else:
                    file_path = None
                    line_no = -1

                error_data = {
                    "error_code": "99999",
                    "error_msg": "未知异常",
                    "error_response": str(exc_obj),
                    "error_file": file_path,
                    "error_line": line_no
                }

            # 计算运行时长（秒）
            run_duration = time.time() - start_time
            error_data['run_duration'] = run_duration
            print(f"任务用时：{run_duration}秒")

            # 任务ID
            error_data['task_id'] = default_params['task_id']
            print("任务失败", json.dumps(error_data, ensure_ascii=False))

            # 任务失败
            taskRequest.error(error_data)