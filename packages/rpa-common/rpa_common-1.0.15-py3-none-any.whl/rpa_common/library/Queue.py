import uuid
import json
import time
import threading
import pika
import psutil
import gc
from concurrent.futures import ThreadPoolExecutor
from rpa_common import Env
from rpa_common import Common
from rpa_common.library.Task import Task

env = Env()
common = Common()

class Queue:
    def __init__(self):
        super().__init__()

        env_data = env.get()
        self.queue_name = f'queues_auto_task'
        self.rabbitmq = env_data['rabbitmq']
        self.connection = None
        self.channel = None
        self.heartbeat_thread = None
        # 当前活跃进程
        self.active_count = 0
        # 队列最大待确认数
        self.prefetch_count = 10
        # 机器最多同时跑n个任务
        self.max_workers = 5

        # 运行
        self.run()

    def run(self):
        '''
        @Desc    : 循环连接 RabbitMQ
        @Author  : 钟水洲
        @Time    : 2025/05/29 14:42:03
        '''
        while True:
            try:
                print("尝试连接 RabbitMQ 服务器...")
                time.sleep(1)
                self.connect()
                print("连接成功，开始消费...")
                time.sleep(1)
                self.consume()
            except Exception as e:
                print(f"连接异常: {e}")
                time.sleep(1)
            finally:
                print(f"释放 RabbitMQ 资源")
                time.sleep(1)
                self.stop_heartbeat()
                self.close_connection()
            time.sleep(60)

    def connect(self):
        '''
        @Desc    : 建立 RabbitMQ 连接
        @Author  : 钟水洲
        @Time    : 2025/05/17 10:11:04
        '''
        print("建立 RabbitMQ 连接...")
        time.sleep(1)
        try:
            credentials = pika.PlainCredentials(self.rabbitmq['username'], self.rabbitmq['password'])
            parameters = pika.ConnectionParameters(
                host=self.rabbitmq['host'],
                port=self.rabbitmq['port'],
                virtual_host=self.rabbitmq['vhost'],
                credentials=credentials,
                heartbeat=60,
                blocked_connection_timeout=120
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.queue_name, durable=True)
            print(f"开始心跳")
            self.start_heartbeat()
        except Exception as e:
            print(f"停止心跳")
            self.stop_heartbeat()  # ✅ 出错也应停止
            raise e

    def consume(self):
        '''
        @Desc    : 设置 RabbitMQ,并启动消费
        @Author  : 钟水洲
        @Time    : 2025/05/29 14:43:16
        '''
        print("设置 RabbitMQ,并启动消费...")
        time.sleep(1)
        if not self.channel or not self.channel.is_open:
            print("RabbitMQ channel 未开启，退出消费")
            return
        self.channel.basic_qos(prefetch_count=self.prefetch_count)
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback)
        print("开始消费任务...")
        time.sleep(1)
        try:
            self.channel.start_consuming()
        except Exception as e:
            print(f"消费任务异常: {e}")
            time.sleep(1)

    def callback(self, channel, method, properties, body):
        '''
        @Desc    : 收到消息
        @Author  : 钟水洲
        @Time    : 2025/05/29 14:43:32
        '''
        try:
            timestamp = int(time.time() * 1000)
            print(f"线程池活跃数：{self.active_count} ,{timestamp}")
            time.sleep(1)
            if self.active_count < self.max_workers:
                # 确认消息
                channel.basic_ack(delivery_tag=method.delivery_tag)
                # 增加活跃数
                self.active_count += 1
                # 提交任务给线程池
                print(f"提交任务给线程池... ,{timestamp}")
                thread = threading.Thread(target=self.process_message, args=(body,))
                thread.start()
                time.sleep(1)
            else:
                # 如果线程池忙碌，将消息重新放回队列
                print(f"线程池忙碌... ,{timestamp}")
                channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)  # 不确认消息，重新放回队列
                time.sleep(1)

        except Exception as e:
            print(f"callback 异常: {e}")
            time.sleep(1)

    def process_message(self, body):
        """线程池中处理消息"""
        try:
            timestamp = int(time.time() * 1000)
            body = json.loads(body.decode())
            print("body", json.dumps(body))
            data = body.get("data", {})
            # 执行脚本
            task = Task()
            task.run(data)
            print(f"消息处理完成 ,{timestamp}")
            time.sleep(1)
        except Exception as e:
            print(f"处理消息异常（已确认不重试）: {e}")
            time.sleep(1)
        finally:
            self.active_count -= 1

    def start_heartbeat(self):
        """启动心跳线程，保持 RabbitMQ 连接"""
        if not self.heartbeat_thread or not self.heartbeat_thread.is_alive():
            self.heartbeat_thread = threading.Thread(target=self.send_heartbeat, daemon=True)
            self.heartbeat_thread.start()

    def stop_heartbeat(self):
        """停止心跳线程"""
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            print("心跳停止，等待重连...")
            self.heartbeat_thread = None

    def send_heartbeat(self):
        """保持连接心跳"""
        while self.connection and self.connection.is_open:
            try:
                timestamp = int(time.time() * 1000)
                self.connection.process_data_events()
                print(f"心跳... ,{timestamp}")
                time.sleep(1)
                print(f"线程池活跃数：{self.active_count} ,{timestamp}")
                time.sleep(4)
            except Exception as e:
                print(f"心跳异常: {e}")
                break  # 让线程退出，避免阻塞 stop_heartbeat

    def close_connection(self):
        """关闭 RabbitMQ 连接，释放资源"""
        try:
            if self.channel and self.channel.is_open:
                self.channel.close()
            if self.connection and self.connection.is_open:
                self.connection.close()
        except Exception as e:
            print(f"关闭连接时异常: {e}")