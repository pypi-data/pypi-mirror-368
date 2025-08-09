# -*-coding:utf-8-*-

""" 队列配置 """
class rabbitmq:
    def __init__(self):
        super().__init__()

    @staticmethod
    def default():
        data = {
            'connector':'Amqp',
            'expire':60,
            'default':'default',
            'host':'192.168.1.20',
            'username':'admin',
            'password':'admin',
            'port':5672,
            'vhost':'/',
            'select':0,
            'timeout':0,
            'persistent':False,
        }

        return data