import json
from rpa_common import Env
from rpa_common.library.Request import Request

env = Env()
request = Request()

class TaskRequest():
    def __init__(self):
        super().__init__()

        env_data = env.get()
        self.host = env_data['api']

    def getTaskShopList(self):
        '''
        @Desc    : 获取任务店铺列表
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("获取任务店铺列表 strat")
        url = self.host + '/api/v2/index/post?c=task&a=getTaskShopList&zsit=debug'
        res = request.post(url, {})
        print("获取任务店铺列表 end", res)
        return res

    def getShopTask(self, data):
        '''
        @Desc    : 获取任务店铺列表
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("获取店铺任务 strat")
        url = self.host + '/api/v2/index/post?c=task&a=getShopTask&zsit=debug'
        res = request.post(url, data)
        print("获取店铺任务 end", res)
        return res

    def getTask(self, data):
        '''
        @Desc    : 获取任务信息
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("获取任务信息 strat")

        url = self.host + '/api/v2/index/post?c=task&a=getTaskInfo&zsit=debug'
        res = request.post(url, data)
        print("获取任务信息 end", res)
        return res

    def save(self, data):
        '''
        @Desc    : 保存数据
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("保存数据 strat")
        url = self.host + '/api/v2/index/post?c=data&a=storage&zsit=debug'
        res = request.post(url, data)
        print("保存数据 end", res)
        return res

    def end(self, data):
        '''
        @Desc    : 完成任务
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("完成任务 strat")
        url = self.host + '/api/v2/index/post?c=task&a=completeTask&zsit=debug'
        res = request.post(url, data)
        print("完成任务 end", res)
        return res

    def error(self, data):
        '''
        @Desc    : 任务失败
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("任务失败 strat")
        url = self.host + '/api/v2/index/post?c=task&a=failedTask&zsit=debug'
        res = request.post(url, data)
        print("任务失败 end", res)
        return res