# 参数异常

from .Base import BaseAppException

class IpException(BaseAppException):
    def __init__(self, error_msg="IP异常", error_response=None):
        super().__init__(error_msg, error_response, "41000")

class EmailException(BaseAppException):
    def __init__(self, error_msg="邮箱异常", error_response=None):
        super().__init__(error_msg, error_response, "42000")

class TaskParamsException(BaseAppException):
    def __init__(self, error_msg="任务参数异常", error_response=None):
        super().__init__(error_msg, error_response, "43000")

class GoogleAuthException(BaseAppException):
    def __init__(self, error_msg="谷歌验证器异常", error_response=None):
        super().__init__(error_msg, error_response, "44000")