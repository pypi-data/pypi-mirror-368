import pyotp

from rpa_common import Common
from rpa_common.exceptions import GoogleAuthException

common = Common()

class GoogleService():
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_verify_code(secret_key):
        '''
        @Desc    : 获取验证码
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print('secret_key', secret_key)
        if not secret_key:
            raise GoogleAuthException("谷歌验证器秘钥不能为空")

        # 创建 TOTP 对象
        totp = pyotp.TOTP(secret_key)

        # 获取当前验证码
        current_otp = totp.now()

        return common.back(1, '获取成功', current_otp)