# -*-coding:utf-8-*-

""" 队列配置 """
class server:
    def __init__(self):
        super().__init__()

    @staticmethod
    def default():
        data = {
            "api": "http://api.rpa.spocoo.com",
            "cdn": "https://oss-rpa.oss-cn-shenzhen.aliyuncs.com",
        }

        return data