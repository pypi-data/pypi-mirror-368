# 未知异常

from .Base import BaseAppException

class UnknownException(BaseAppException):
    def __init__(self, error_msg="未知异常", error_response=None):
        super().__init__(error_msg, error_response, "99999")
