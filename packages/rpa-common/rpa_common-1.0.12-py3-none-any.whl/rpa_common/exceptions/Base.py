import json

class BaseAppException(Exception):
    """
    所有自定义异常的基类
    """
    def __init__(self, error_msg="系统异常", error_response=None, error_code=10000, *args, **kwargs):
        self.error_msg = error_msg
        self.error_code = error_code

        # 如果是 dict 或 list，则转为 JSON 字符串
        if isinstance(error_response, (dict, list)):
            self.error_response = json.dumps(error_response, ensure_ascii=False)
        else:
            self.error_response = error_response if error_response is not None else ""

        super().__init__(error_msg)

    def error_data(self):
        '''
        @Desc    : 错误信息统一返回
        @Author  : 钟水洲
        @Time    : 2025/07/10 19:06:53
        '''
        data = {
            "error_code": self.error_code,
            "error_msg": self.error_msg,
            "error_response": self.error_response
        }
        return data

    def __str__(self):
        return f"[{self.error_code}] {self.error_msg}"
