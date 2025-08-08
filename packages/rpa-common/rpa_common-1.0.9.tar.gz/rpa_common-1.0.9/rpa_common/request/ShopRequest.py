import json
from rpa_common import Env
from rpa_common.library.Request import Request

env = Env()
request = Request()

class ShopRequest():
    def __init__(self):
        super().__init__()

        env_data = env.get()
        self.host = env_data['api']

    def getDetail(self, data):
        '''
        @Desc    : 获取店铺详情
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        url = self.host + '/api/v2/index/post?c=shop&a=getShopInfo&zsit=debug'
        res = request.post(url, data)
        return res

    def saveStorage(self, data):
        '''
        @Desc    : 保存店铺缓存
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("保存店铺缓存 strat")
        url = self.host + '/api/v2/index/post?c=shop&a=setShopStorage&zsit=debug'
        res = request.post(url, data)
        print("保存店铺缓存 end", res)
        return res

    def saveFingerprintLog(self, data):
        '''
        @Desc    : 保存店铺指纹记录
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("保存店铺指纹记录 strat")
        url = self.host + '/api/v2/index/post?c=shop&a=saveFingerprint&zsit=debug'
        res = request.post(url, data)
        print("保存店铺指纹记录 end", res)
        return res