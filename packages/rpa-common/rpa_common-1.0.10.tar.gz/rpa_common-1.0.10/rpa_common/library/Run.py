import threading
import time
import gc
from rpa_common.Common import Common
from rpa_common.request.TaskRequest import TaskRequest
from rpa_common.exceptions import TaskParamsException
from rpa_common.library.Task import Task

common = Common()
taskRequest = TaskRequest()

class Run:
    def __init__(self):
        super().__init__()

        # 运行
        self.run()

    def run(self):
        '''
        @Desc    : 执行
        @Author  : 钟水洲
        @Time    : 2025/05/29 14:42:03
        '''
        res = taskRequest.getTaskShopList()
        if res['code'] != 1:
            print(res['msg'])
            return

        task_list = res['data']

        threads = []

        for key, item in enumerate(task_list):
            index = key + 1

            print(f"任务 {index}: {item}")

            def run_task(task_item):
                task = Task()
                task.run(task_item)

            thread = threading.Thread(target=run_task, args=(item,))
            threads.append(thread)
            thread.start()

            time.sleep(1)

        # 等待所有线程完成
        for thread in threads:
            thread.join()