# 登录异常

from .Base import BaseAppException

class LoginException(BaseAppException):
    def __init__(self, error_msg="登录异常", error_response=None):
        super().__init__(error_msg, error_response, "61000")