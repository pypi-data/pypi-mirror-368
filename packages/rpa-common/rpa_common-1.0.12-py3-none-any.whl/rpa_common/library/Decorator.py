'''装饰器库'''
from functools import wraps
import threading
from typing import Union, Dict, Literal, List
import time

def retry(*, max_retries=3, delay=1, exceptions=(Exception,)):
    """
    重试装饰器
    :param max_retries: 最大重试次数
    :param delay: 重试间隔时间(秒)
    :param exceptions: 需要重试的异常类型
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries >= max_retries:
                        raise ValueError(f"操作在重试{max_retries}次后仍然失败: {e}")
                    time.sleep(delay)

        return wrapper

    return decorator

def singleton(cls):
    """singleton 线程安全的单例装饰器

    :return: 返回实例化内容
    """    
    instances = {}
    lock = threading.Lock()
    
    def get_instance(*args, **kwargs):
        nonlocal instances
        if cls not in instances:
            with lock:  # 确保线程安全
                if cls not in instances:  # 双重检查锁定
                    # print(f"Creating new {cls.__name__} instance in thread: {threading.current_thread().name}")
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance