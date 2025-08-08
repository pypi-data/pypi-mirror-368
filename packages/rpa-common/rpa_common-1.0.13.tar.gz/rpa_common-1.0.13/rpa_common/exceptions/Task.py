# 任务异常

from .Base import BaseAppException

class TimeoutException(BaseAppException):
    def __init__(self, error_msg="任务超时异常", error_response=None):
        super().__init__(error_msg, error_response, "61000")