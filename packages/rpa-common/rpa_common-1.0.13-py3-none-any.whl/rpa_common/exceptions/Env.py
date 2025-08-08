# 环境异常

from .Base import BaseAppException

class ChromeException(BaseAppException):
    def __init__(self, error_msg="浏览器异常", error_response=None):
        super().__init__(error_msg, error_response, "51000")

class FingerprintException(BaseAppException):
    def __init__(self, error_msg="指纹异常", error_response=None):
        super().__init__(error_msg, error_response, "51010")