import json
import requests
import logging
import time
from concurrent.futures import ThreadPoolExecutor

class Crontab():
    def __init__(self):
        super().__init__()

        # 线程池，最大5个线程
        self.executor = ThreadPoolExecutor(max_workers=5)
        # 定时任务调度
        self.schedule_tasks()

    def schedule_tasks(self):
        '''
        @Desc    : 调度所有定时任务
        @Author  : 钟水洲
        @Time    : 2025/05/29 14:21:14
        '''
        self.schedule_task(self.get_task, 10)  # 监听任务（10秒）

    def schedule_task(self, task_func, interval):
        '''
        @Desc    : 使用线程池调度定时任务
        @Author  : 钟水洲
        @Time    : 2025/05/29 14:22:11
        '''
        def run_task():
            while True:
                try:
                    task_func()
                except Exception as e:
                    logging.error(f"任务 {task_func.__name__} 发生错误: {str(e)}")
                time.sleep(interval)

        self.executor.submit(run_task)

    def get_task(self):
        '''
        @Desc    : 获取任务
        @Author  : 钟水洲
        @Time    : 2025/05/29 14:21:14
        '''
        print("获取任务")