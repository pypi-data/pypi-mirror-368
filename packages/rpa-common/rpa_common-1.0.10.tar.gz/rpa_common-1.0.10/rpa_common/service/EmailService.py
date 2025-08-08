import json
import json5
import imaplib
import email
import time
import random
import uuid
import pytz
import chardet
import hashlib
import requests
import re
from urllib.parse import quote
from functools import wraps
from typing import Union, Dict, Literal, List
from bs4 import BeautifulSoup
from email.header import decode_header
from datetime import datetime, timedelta

from rpa_common import Common
from rpa_common.exceptions import EmailException
from rpa_common.Env import Env
from rpa_common.service.SqlalchemyService import EMAIL_DedicatedDataCaching

common = Common()

class EmailService():
    def __init__(self):
        super().__init__()
        self.env = Env()

        self.platform_list = ['qq', '163'] #目前支持的平台
        # 邮件截止时间
        now = datetime.now()
        end_time = now - timedelta(minutes=30) #30分钟
        self.end_timestamp = int(time.mktime(end_time.timetuple()))

        # 类型
        self.type = ''
        # 平台
        self.platform = ''
        # 邮箱
        self.email = ''
        # 授权码
        self.auth_code = ''

        # 邮箱服务
        self.mail = None

    def get_verify_code(self, type, data):
        '''
        @Desc    : 获取验证码
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        if not type:
            raise EmailException("邮箱类型不能为空")
        self.type = type.lower()
        print('type', self.type)

        platform = data['platform']
        if not platform:
            raise EmailException("邮箱平台不能为空")
        self.platform = platform.lower()
        print('platform', self.platform)

        email = data['email']
        if not email:
            raise EmailException("邮箱账号不能为空")

        self.email = email.lower()
        print('email', self.email)

        auth_code = data['auth_code']
        if not auth_code:
            raise EmailException("邮箱授权码不能为空")
        self.auth_code = auth_code

        if platform not in self.platform_list:
            raise EmailException("不支持的邮箱平台")

        res = self.get_email()
        if res['status'] != 1:
            return common.back(0, res['message'])

        return common.back(1, '获取成功', res['data'])

    def get_email(self):
        '''
        @Desc    : 获取邮件
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print('获取邮件')
        res = self.connect_imap()
        if res['status'] != 1:
            print(res['message'])
            return common.back(0, res['message'])
        self.mail = res['data']

        res = self.get_email_list()
        if res['status'] != 1:
            print(res['message'])
            return common.back(0, res['message'])
        uid_list = res['data']

        # 验证码
        verify_code = ''
        # 遍历UID列表
        for uid in uid_list:
            # 获取邮件的原始数据
            status, data = self.mail.fetch(uid, '(RFC822)')
            if status != 'OK':
                continue

            # 解析邮件数据
            msg = email.message_from_bytes(data[0][1])
            # 邮件日期
            raw_date = msg['Date']
            date = ''
            # 转换时间格式
            if raw_date is not None:
                date = self.to_china_date(raw_date)
            # 是否解析失败
            if date == '':
                continue

            # 将字符串转换为datetime对象
            specified_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            # 将datetime对象转换为时间戳
            timestamp = int(specified_date.timestamp())
            print("当前邮件时间戳:", timestamp)

            if timestamp < self.end_timestamp:
                print("当前邮件超过截止时间，停止查询")
                break

            # 解析邮件数据
            res = self.decode_email_data(uid)
            if res['status'] != 1:
                continue
            email_data = res['data']

            verify_code = self.decode_verification_code(email_data)

            if verify_code == '':
                continue

            # 获取到验证码
            print("verify_code:", verify_code)
            break

        if verify_code == '':
            raise EmailException("未获取到邮箱验证码")

        return common.back(1, '获取成功', verify_code)

    def decode_verification_code(self, data):
        '''
        @Desc    : 解析验证码
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        if self.type == 'tiktok_verifycode':
            return self.decode_tiktok_verifycode(data)

    def connect_imap(self):
        '''
        @Desc    : 连接IMAP
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        try:
            imap_server = self.get_imap_server()

            if self.platform == '163':
                imaplib.Commands["ID"] = "NONAUTH"

            mail = imaplib.IMAP4_SSL(imap_server)
            mail.login(self.email, self.auth_code)

            if self.platform == '163':
                mail._simple_command("ID",'("name" "test" "version" "1.0.0")')

            return common.back(1, "连接成功", mail)
        except Exception as e:
            return common.back(0, f"IMAP 登录失败: {e}")
        
    def get_imap_server(self):
        '''
        @Desc    : 获取IMAP服务域名
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        servers = {
            'qq': 'imap.qq.com',
            '163': 'imap.163.com',
        }
        return servers.get(self.platform, '')

    # 切分电子邮件地址，获取域名部分
    def extract_domain(self, email):
        parts = email.split('@')
        if len(parts) == 2:  # 确保电子邮件地址只有一个 '@' 符号
            return parts[1]
        else:
            return ''  # 返回 '' 表示无法解析域名

    # 使用正则表达式匹配指定位数的纯数字
    def is_n_digit_number(self, s, n):
        pattern = r'^\d{' + str(n) + r'}$'
        return bool(re.match(pattern, s))

    def chardet_detect(self, value):
        '''
        @Desc    : 自动转码
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        if isinstance(value, bytes):
            # 使用chardet来自动检测编码
            detected_encoding = chardet.detect(value)
            print(f"自动转编码",detected_encoding)
            if detected_encoding['confidence'] > 0.3:
                if detected_encoding['encoding'] == 'TIS-620':
                    return ''
                if detected_encoding['encoding'] == 'ISO-8859-5':
                    return ''

                try:
                    value = value.decode(detected_encoding['encoding'])
                except Exception:
                    return ''
            else:
                return ''

        return value

    # 转为中国时间
    def to_china_date(self, raw_date):
        try:
            date_string = raw_date.split(' (')[0]
            parsed_date = datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S %z")

            # 转换时区为中国时间
            china_tz = pytz.timezone('Asia/Shanghai')
            date = parsed_date.astimezone(china_tz).strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            date = ""

        return date

    def decode_tiktok_verifycode(self, data):
        '''
        @Desc    : 解析tiktok验证码
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        body = data.get("body")
        from_email = data.get("from_email")

        # 解析HTML
        soup = BeautifulSoup(body, 'html.parser')

        verifycode = ''

        # 注册
        if from_email == 'register@account.tiktok.com':
            paragraphs = soup.find_all('p')
            for paragraph in paragraphs:
                text = paragraph.text.strip()
                if self.is_n_digit_number(text, 6):
                    verifycode = text
                    break

        # 登录验证、忘记密码
        if from_email == 'no-reply@mail.tiktokglobalshop.com':
            # 获取第一个具有class为code的内容
            first_code_snippet = soup.find(class_='code')

            # 打印第一个code的内容
            if first_code_snippet:
                verifycode = first_code_snippet.text.strip()

        return verifycode

    def decode_email_data(self, uid):
        '''
        @Desc    : 解析邮件数据
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 获取邮件的原始数据
        status, data = self.mail.fetch(uid, '(RFC822)')
        if status != 'OK':
            return common.back(0, '获取邮件数据失败')

        # 邮件UID
        decode_uid = uid.decode('utf-8')
        print(f"邮件UID: {decode_uid}")

        # 获取邮件标志
        flags = self.mail.fetch(uid, '(FLAGS)')
        is_flags = 0
        # 检查是否包含 "\\Seen" 标志
        if b'\\Seen' in flags[1][0]:
            is_flags = 1
            print(f"邮件标志: 邮件已读")
        else:
            is_flags = 0
            print(f"邮件标志: 邮件未读")

        # 解析邮件数据
        msg = email.message_from_bytes(data[0][1])

        # 获取邮件From
        raw_from = msg['From']

        # 解码 From 头部信息，通常这是一个元组，其中包含了编码和实际的字符串
        raw_from_email = decode_header(raw_from)

        # 提取邮箱地址
        from_email = ''
        for value in raw_from_email:
            if isinstance(value, tuple):
                from_name = value[0]

                from_name = self.chardet_detect(from_name)

                # 如果有编码，解码字符串
                # 使用字符串的 find 和 slice 方法来提取邮箱地址
                start_index = from_name.find('<') + 1  # 找到 '<' 后面的索引
                end_index = from_name.find('>')       # 找到 '>' 的索引
                # 提取邮箱地址
                if start_index > 0 and end_index > start_index:
                    from_email = from_name[start_index:end_index]
                else:
                    from_email = from_name
            else:
                # 如果没有编码，直接使用字符串
                from_email = value

        from_email = from_email.lower()
        # 发件人
        print(f"发件人: {from_email}")

        # 获取邮件To
        raw_to = msg['To']

        # 解码 From 头部信息，通常这是一个元组，其中包含了编码和实际的字符串
        raw_to_email = decode_header(raw_to)

        # 提取邮箱地址
        to_email = ''
        for value in raw_to_email:
            if isinstance(value, tuple):
                to_name = value[0]

                to_name = self.chardet_detect(to_name)

                # 如果有编码，解码字符串
                # 使用字符串的 find 和 slice 方法来提取邮箱地址
                start_index = to_name.find('<') + 1  # 找到 '<' 后面的索引
                end_index = to_name.find('>')       # 找到 '>' 的索引
                # 提取邮箱地址
                if start_index > 0 and end_index > start_index:
                    to_email = to_name[start_index:end_index]
                else:
                    to_email = to_name
            else:
                # 如果没有编码，直接使用字符串
                to_email = value

        to_email = to_email.lower()
        # 收件人
        print(f"收件人: {to_email}")

        # 获取邮件大小
        raw_size = len(data[0][1])
        print(f"邮件大小: {raw_size} 字节")

        # 获取邮件标题头
        raw_subject = msg['Subject']

        # 解码标题
        subject, encoding = decode_header(raw_subject)[0]
        print(f"标题编码: {encoding}")
        if encoding:
            if encoding != 'unknown-8bit':
                subject = subject.decode(encoding)

        decode_subject = self.chardet_detect(subject)

        print(f"邮件主题: {decode_subject}")

        # 邮件日期
        raw_date = msg['Date']

        date = ''
        if raw_date is not None:
            date = self.to_china_date(raw_date)

        print(f"邮件日期: {date}")

        # 带有附件的邮件
        is_multipart = msg.is_multipart()
        print(f"带有附件的邮件: {is_multipart}")

        body = ''
        # 检查邮件是否有附件
        if is_multipart:
            # 如果是多部分邮件（比如带有附件的邮件），我们需要遍历各个部分
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/html':
                    # 这通常是正文部分
                    payload = part.get_payload(decode=True)
                    if payload is not None:
                        body = self.chardet_detect(payload)
                        break  # 找到正文后停止遍历
        else:
            body = msg.get_payload(decode=True)
            body = self.chardet_detect(body)

        print(f"邮件正文: {bool(body)}")

        arr = {
            "uid": decode_uid,
            "is_flags": is_flags,
            "subject": decode_subject,
            "date": date,
            "from_email": from_email,
            "body": body,
        }

        return common.back(1, '获取成功', arr)

    # 获取邮件列表
    def get_email_list(self):
        '''
        @Desc    : 获取邮件列表数据
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print('获取邮件列表数据')

        # 选择邮件邮箱
        select_status, select_messages = self.mail.select("INBOX")
        if select_status != 'OK':
            return common.back(0, '选择邮件失败')

        # 搜索邮件
        status, messages = self.mail.search(None, 'ALL')
        if status != 'OK':
            return common.back(0, '搜索邮件失败')

        # 获取UID列表
        uid_list = messages[0].split()[::-1]
        if not uid_list:
            return common.back(0, '邮件数据为空')
        
        return common.back(1, '获取成功', uid_list)


    def get_email_verification(self, email, platform, types:int=1):
        '''
        @Desc    : 获取某平台163邮箱验证码
        @Author  : 祁国庆
        @Time    : 2025/04/09 10:41:45
            - email: 163的邮箱号
            - platform: 支持多平台（目前支持tiktok/shopee/shein/lazada）
        '''
        email = email.lower().strip()
        platform = platform.lower().strip()
        # types  1、获取邮件密码验证码(默认）   2、删除所有邮件
        """
        1、暂不支持多平台获取验证码，需要手动添加提取规则
        2、不支持重试，过早获取验证码可能会接收不到，程序不会自动重试。请求太多，添加重试功能只会是负担，可以在发送邮件的5秒后获取验证码来解决这个重试的问题。
        """
        # -------------参数校验
        if platform not in ['tiktok', 'shopee', 'shein', 'lazada']:
            raise ValueError('平台不能为空/暂不支持该平台')
        if '@163.com' not in email:
            raise ValueError('邮箱不能为空/仅支持@163邮箱')
        if types not in [1, 2]:
            raise ValueError('模式选择错误，只能是1/2')

        email_163 = email_163_verification(
            email=email,   # 邮箱号
            node_host='http://172.16.2.5:4000',  # http://172.16.2.5:4000 'http://127.0.0.1:4001',  # nodejs逆向接口地址
            servers_host='http://rpa.spocoo.com',  # 正式环境地址
            platform=platform    # 平台
        )

        if types == 1:
            '''获取某平台的验证码'''
            email_163.get_verification()
            return common.back(1, '获取成功', email_163.verification_code)
        elif types == 2:
            '''固定删除20000条邮件'''
            email_163.del_email()
            return common.back(1, '删除成功', [])
        raise ValueError('模式选择错误，只能是1/2')


class EmailService163:
    '''
    更新日期：2025-07-28  浏览器：Brave
    1、疑似可以刷新令牌：登录后将网站链接更换为https://mail.163.com/，会自动刷新新的令牌，但暂时不确定令牌的时效会不会有影响，会不会弹验证框，多注意
    【https://mail.163.com/fgw/mailsrv-master-account-core/entry/easylogin/authorize/fpwd】接口（需研究）
    2、可尝试将多邮件的cookie进行会话级并存，有概率可绕过人机验证（需研究）
    '''
    def __init__(self, *, email, password='', node_host='', servers_host='', platform=None, **params):
        print('——————————————【初始化】')
        self.EMAIL20DDC = EMAIL_DedicatedDataCaching()
        self.servers_host = servers_host or "http://rpa.spocoo.com"
        # Node地址环境 默认 http://127.0.0.1:4000  http://172.16.2.5:4000
        # self.node_host = node_host or 'http://172.16.2.5:4000'
        self.node_host = node_host or 'http://172.16.2.5:4000'
        self.replace_token = True
        self.platform = platform and platform.lower()
        self.email = email.lower()
        self.print_('邮箱', email)

        self.password = password or self.get_password
        self.initial_basic_information()
        self.EmailCookie(types=2)   # 读取cookie并赋予 self.cookie（含换环境信息）


    def login(self):
        '''登录并获取持续会话令牌'''
        print('——————————————【执行163邮箱登录流程（用账户密码）】——————————————')

        self.initial_basic_information()
        time.sleep(0.1)
        self.py_utid()
        time.sleep(0.1)
        self.fgw_mailsrvIpdetail_detail()
        time.sleep(0.1)
        self.fgw_mailsrvDeviceIdmapping_webapp_init()
        time.sleep(0.1)
        self.dl_zj_mail_ini()
        time.sleep(0.1)
        self.UA1435545636633_1()
        time.sleep(0.1)
        self.UA1435545636633_2()
        time.sleep(0.1)

        self.dl_zj_mail_powGetP()
        time.sleep(0.1)
        self.dl_zj_mail_gt()
        time.sleep(0.1)
        self.dl_zj_mail_l()
        time.sleep(0.1)
        self.entry_cgi_ntesdoor(types=3, method='POST')
        time.sleep(0.1)

        self.EmailCookie(types=1)
        # 请用Token获取登录后的令牌
        print('令牌在这里 -> ', self.cookie)
        time.sleep(3)

    def get_verification(self):
        '''执行获取邮件验证码流程'''
        print('——————————————【执行163邮箱获取验证码流程（用令牌）】——————————————')
        self.print_('全局cookie', self.cookie)
        assert self.platform, '平台未设置 - platform'
        assert self.platform in self.platform_mapping, f'暂不支持此平台获取验证码 - {self.platform}'
        if self.cookie and self.entry_cgi_ntesdoor(types=3, method='HEAD'):
            self.js6_s(types=1, limit=30)
            self.js6_read_readhtmlJsp()
            print('验证码在这里 -> ', self.verification_code)
        elif self.replace_token:
            print('****************【令牌失效 更换令牌】****************')
            self.login()
            self.replace_token = False
            self.get_verification()
        else:
            raise ValueError('[163邮箱]令牌更换失败需查看 - 大概率需要手机验证码')

    def del_email(self):
        '''执行删除邮件流程'''
        print('——————————————【执行163邮箱删除邮件流程（用令牌）】——————————————')
        self.print_('全局cookie', self.cookie)
        if self.cookie and self.entry_cgi_ntesdoor(types=3, method='HEAD'):
            self.js6_s(types=2, limit=20000)
            self.del_js6_s()
            # self.Hook()
        elif self.replace_token:
            print('****************【令牌失效 更换令牌】****************')
            self.login()
            self.replace_token = False
            self.del_email()
        else:
            raise ValueError('[163邮箱]令牌更换失败需查看')

    @property
    def core_cookie(self):
        return {
            'MAIL_PASSPORT_INFO': self.MAIL_PASSPORT_INFO,
            'MAIL_PASSPORT': self.MAIL_PASSPORT
        }
    @property
    def platform_mapping(self):
        '''多平台映射表'''
        return {
            'tiktok': {
                'subject': ['TikTok Shop商家验证码', 'is your verification code', 'TikTok Shop Verification Code'],
                're': '(?=您正在进行邮箱验证，请在验证码输入框中输入|To verify your account, enter this code in TikTok Shop).*?<span class="code">(.*?)<' + '|' + 'color: rgb\(22,24,35\);font-weight: bold;">(.*?)<'
            },
            'shopee': {
                'subject': ['Your Email OTP Verification Code'],
                're': 'line-height: 40px;"> {1,40}<b>(.*?)</b>'
            },
            'shein': {
                'subject': ['您正在登录[SHEIN]系统'],
                're': '登录验证码：(.*?)，'
            },
            'lazada': {
                'subject': ['【重要】请完成验证'],
                're': 'margin-left: -1\.25rem; line-height: 1;"></a>&nbsp;(.*?)<'
            }
        }

    def set_cookie(self):
        '''保存邮箱的Cookie到服务器'''
        print('———————————— 保存cookie到服务器')
        # 随机30天（秒） 30天 - 2天 + (随机1-47小时 * 随机1-60分 * 随机1-60秒)
        _time_set = (30 * 24 * 60 * 60) - (2 * 24 * 60 * 60) + (random.randint(1, 47) * random.randint(1, 60) * random.randint(1, 60))
        response = self.reques(method='POST',
                               url=self.servers_host + '/api/v1/index/post?c=app&a=setEmailCookie&zsit=debug',
                               json={
                                   "email": self.email,
                                   "cookie": json.dumps({
                                       'NTES_P_UTID': self.NTES_P_UTID,
                                       'NTES_SESS': self.NTES_SESS,
                                       'S_INFO': self.S_INFO,
                                       'P_INFO': self.P_INFO
                                   }),
                                   "expireTime": int(str(self.MAIL_PASSPORT_INFO).split('|')[1]) + _time_set
                               })
        response_data = response.json()
        self.print_('[请求结果][set_cookie]|[response]', response_data)
        assert response_data['code'] == 1, response_data.get('msg', '') or '设置邮箱cookie失败'

    def get_cookie(self) -> dict:
        '''服务器获取邮箱的Cookie'''
        print('———————————— 从服务器获取cookie')
        response = self.reques(method='POST',
                               url=self.servers_host + '/api/v1/index/post?c=app&a=getEmailCookie&zsit=debug',
                               json={"email": self.email})
        response_data = response.json()
        self.print_('[请求结果][get_cookie]|[response]', response_data)
        data = response_data.get('data', '') or {}
        cookie = data and json.loads(data.get('cookie') or '{}')
        if isinstance(cookie, list):
            return (cookie and cookie[0]) or {}
        if isinstance(cookie, dict):
            return cookie
        return {}

    def EmailCookie(self, types):
        '''邮箱令牌读取与保存（含环境）'''
        if types == 1:
            '''保存cookie'''
            print('———————————— 保存cookie到数据库')
            self.EMAIL20DDC.set_data(key=self.email, data={
                                           'NTES_P_UTID': self.NTES_P_UTID,
                                           'NTES_SESS': self.NTES_SESS,
                                           'S_INFO': self.S_INFO,
                                           'P_INFO': self.P_INFO,
                                           'stats_session_id': self.stats_session_id,
                                           'sdid': self.sdid,
                                           'deviceId': self.deviceId,
                                           'user_agent': self.user_agent,
                                           'sec_ch_ua': self.sec_ch_ua,
                                           'NTES_WEB_FP': self.NTES_WEB_FP,
                                           'utid': self.utid,
                                       }, timestamp_end=self.EMAIL20DDC.time(tianchao='30.1.1'),timestamp_end_up=True)

        elif types == 2:
            print('———————————— 从数据库读取cookie')
            cookie = self.EMAIL20DDC.get_data(key=self.email) or {}
            if not cookie: return
            self.NTES_P_UTID = cookie['NTES_P_UTID']
            self.NTES_SESS = cookie['NTES_SESS']
            self.S_INFO = cookie['S_INFO']
            self.P_INFO = cookie['P_INFO']
            self.cookie = {
                'NTES_P_UTID': self.NTES_P_UTID,
                'NTES_SESS': self.NTES_SESS,
                'S_INFO': self.S_INFO,
                'P_INFO': self.P_INFO,
            }
            self.stats_session_id = cookie['stats_session_id']
            self.deviceId = cookie['deviceId']
            self.sdid = cookie['sdid']
            self.user_agent = cookie['user_agent']
            self.sec_ch_ua = cookie['sec_ch_ua']
            self.NTES_WEB_FP = cookie['NTES_WEB_FP']
            self.utid = cookie['utid']
        elif types == 3:
            '''删除令牌'''
            print('———————————— 从数据库移除cookie')
            self.EMAIL20DDC.del_data(key=self.email)
        else:
            raise ValueError('[163邮箱]参数错误')

    @property
    def get_password(self) -> str:
        '''服务器获取邮箱的密码'''
        print('———————————— 从服务器获取邮箱密码')
        response = self.reques(method='POST',
                               url=self.servers_host + '/api/v1/index/post?c=app&a=getAccountPassword&zsit=debug',
                               json={
                                   "platform": self.platform,
                                   "email_name": self.email
                               })
        response_data = response.json()
        # self.print_('[请求结果][get_password]|[response]', response_data)
        data = (response_data.get('data', {}) or {}).get('email', {}) or {}
        if isinstance(data, list): data = (data and data[0]) or {}
        password = data.get('password', '')
        assert password, '[163邮箱]获取邮箱密码失败'
        self.print_('[请求结果][get_password]|[密码]', password)
        return password

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

    @retry(max_retries=3, delay=1, exceptions=(Exception,))
    def reques(self, *, method: Literal['GET', 'POST', 'HEAD'] = None, url='', data=None, json=None, cookies=None,
               headers=None,
               params=None, timeout=None):
        assert method in ['GET', 'POST', 'HEAD'], 'method参数错误'
        request = getattr(requests, method.lower())
        response = request(**{
            'url': url,
            'data': data,
            'json': json,
            'cookies': cookies,
            'headers': headers,
            'params': params,
            'timeout': timeout
        })
        return response

    def initial_basic_information(self):
        '''初始化基本请求信息'''
        self.cookie = {}
        self.NTES_WEB_FP = self.hash_encrypt(str(time.time()), 'md5')  # web指纹 随机一下
        self.code_map = {
            '201': {
                'msg': '请求成功',
                'capFlag_0': {
                    'msg': '请求成功',
                }
            },
            '401': {
                'msg': '您短时间内尝试次数过多，请一个小时后再试！',
                'dt_04': '操作超时，需要刷新页面（估计缺少cookie：l_s_mail163CvViHzl）',
                'dt_06': '操作超时，需要刷新页面（估计是这个cookie过期了：l_s_mail163CvViHzl）'
            },
            '403': {
                'msg': '当前登录有风险，需要安全认证后在登陆！',
            },
            '402': {
                'msg': '指纹错误！',
            },
            '408': {
                'msg': "该号码可能存在安全风险，请更换手机号"
            },
            '412': {
                'msg': '您短时间内尝试次数过多，请一个小时后再试！',
            },
            '413': {
                'msg': '密码错误/密码错误次数太多！！！',
                'capFlag_6': {
                    'msg': '账户密码错误！！！',
                },
                'capFlag_0': {
                    'msg': '账户或密码错误！！！',
                }
            },
            '414': {
                'msg': '您的IP短时间内登录失败次数过多，请过段时间再试！',
            },
            '415': {
                'msg': '您今天登录失败次数过多，请明天再试！',
            },
            '416': {
                'msg': '您的IP登录过于频繁，我们限制一天内登录过于频繁的情况，请稍候再试！',
            },
            '417': {
                'msg': '您的IP今天登录次数过多，我们限制一天内登录过于频繁的情况，请稍候再试！',
            },
            '418': {
                'msg': '您今天登录次数过多，请明天再试！',
            },
            '419': {
                'msg': '您的登录操作过于频繁，请稍候再试！',
            },
            '420': {
                'msg': '账号或密码错误。若账号长期未登录，可能已被注销！',
            },
            '422': {
                'msg': '此账号已被锁定，此账号已被锁定！暂时无法登录，请您解锁后再来登录！',
            },
            '423': {
                'msg': '风控账号！',
            },
            '424': {
                'msg': '服务已到期，该靓号服务已到期，请您续费！',
            },
            '434': {
                'msg': '您验证错误次数过多，请稍后再试',
            },
            '435': {
                'msg': '您验证错误次数过多，请改天再试',
            },
            '436': {
                'msg': '您验证错误次数过多，请稍后再试',
            },
            '437': {
                'msg': '您验证错误次数过多，请改天再试',
            },
            '447': {
                'msg': '由于频繁登录，请过人机验证！',
            },
            '455': {
                'msg': '账号无法使用！！！',
                'capFlag_0': {
                    'msg': '该账号无法使用，请注册其他账号！！！',
                },
            },
            '460': {
                'msg': '账号或密码错误。若账号长期未登录，可能已被注销！',
            },
            '500': {
                'msg': '系统繁忙！我们正在恢复中！请您稍候尝试！',
            },
            '503': {
                'msg': '系统繁忙！我们正在恢复中！请您稍候尝试！',
            },
            '504': {
                'msg': '系统繁忙！系统此时有点繁忙！请您重试！',
            },
            '803': {
                'msg': '加载失败，请稍后再试'
            },
            '804': {
                'msg': '加载失败，请稍后再试'
            },
            '805': {
                'msg': '加载失败，请稍后再试'
            },
            '806': {
                'msg': '加载失败，请稍后再试'
            }
        }
        self.Referer = f"https://dl.reg.163.com/webzj/v1.0.1/pub/index_dl2_new.html?cd=%2F%2Fmimg.127.net%2Fp%2Ffreemail%2Findex%2Funified%2Fstatic%2F2025%2F%2Fcss%2F&cf=urs.163.918051fb.css&MGID={int(time.time() * 1000)}.403&wdaId=&pkid=CvViHzl&product=mail163"
        v1 = random.randint(135, 160)
        v2 = random.randint(8, 24)
        v3 = random.randint(537, 600)
        self.user_agent = f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{v3}.36 (KHTML, like Gecko) Chrome/{v1}.0.0.0 Safari/{v3}.36'
        self.sec_ch_ua = f'"Chromium";v="{v1}", "Not:A-Brand";v="{v2}", "Brave";v="{v1}"'
        self.deviceId = str(uuid.uuid4()).replace('-', '') + '_v1'
        self.Verification = ''

    def date_change_str_time(self, text: str, month_add: int = 0) -> str:
        '''
        处理js的时间格式
        :param text: 要处理的文本内容
        :param month_add: 月份添加 专门针对 js 的 new Date,js默认是少一个月份的
        处理文本内容，将文本内的 new Date(2025,3,3,10,17,46) 替换为正常的时间 2025-04-02 10:41:50
        '''

        # 将字符串转换为时间对象
        def parse_time(time_str: str, month_add: int = 0) -> str:
            '''
            :param time_str: 日期 例如：2025-2-19-11-9-52 或 2025-2-19
            :param month_add: 0或1，代表的是 是否将月份+1
            :return:
            '''
            # 针对 new Date(2025,3,3,10,17,46)
            if time_str.count('-') == 5:
                # 将字符串按 "-" 分割
                year, month, day, hour, minute, second = map(int, time_str.split("-"))
                # 转换为时间对象  month添加一个月，因为js代码里没人是少于一个月的，所以我们直接添加即可，无需担心边界问题
                return str(datetime(year, month + month_add, day, hour, minute, second))
            # 针对 new Date(2025,3,3)
            elif time_str.count('-') == 2:
                # 将字符串按 "-" 分割
                year, month, day = map(int, time_str.split("-"))
                # 转换为时间对象  month添加一个月，因为js代码里没人是少于一个月的，所以我们直接添加即可，无需担心边界问题
                return str(datetime(year, month + month_add, day))
            raise ValueError('[mail 163]时间格式错误')
        # 将 new Date(2025,3,3,10,17,46)  转为  2025-04-02 10:41:50
        text = re.sub(r'new Date\(\d+,\d+,\d+,\d+,\d+,\d+\)', lambda x: '"' + parse_time(
            '-'.join(re.findall(r'\((.*?),(.*?),(.*?),(.*?),(.*?),(.*?)\)', x.group(0))[0]), 1) + '"',
                      text)
        # 将 new Date(2025,3,3)  转为   2025-3-20
        text = re.sub(r'new Date\(\d+,\d+,\d+\)',
                      lambda x: '"' + parse_time('-'.join(re.findall(r'\((.*?),(.*?),(.*?)\)', x.group(0))[0]),
                                                 1) + '"', text)
        return text

    @property
    def verification_code(self):
        '''获取验证码'''
        return self.Verification
    def code_analysis(self):
        '''状态码解析'''
        msg = f'状态码解析传参有误 - {self.code}'
        if 'dt' in self.code and 'ret' in self.code:
            msg = self.code_map.get(str(self.code['ret']), {}).get("dt_" + str(self.code['dt']),
                                                                   f'该状态码解析失败 - {self.code}')
            if isinstance(msg, dict): msg = msg['msg']
        elif 'capFlag' in self.code and 'ret' in self.code:
            msg = self.code_map.get(str(self.code['ret']), {}).get("capFlag_" + str(self.code['capFlag']),
                                                                   f'该状态码解析失败 - {self.code}')
            if isinstance(msg, dict): msg = msg['msg']
        elif 'ret' in self.code:
            msg = self.code_map.get(str(self.code['ret']), {}).get('msg') or f'该状态码解析失败 - {self.code}'
        if msg == '请求成功' or 'ret' not in self.code:
            return '请求成功'
        raise ValueError('[code_analysis] ' + str(msg))
    def hash_encrypt(self, string, algorithm):
        """
        @Desc     : 整合hash哈希加密算法
        @Author   : 祁国庆
        @Time     : 2025/04/18 10:46:33
        @Params   :
            - string: 要加密的字符串
            - algorithm: 选择要使用的加密库（标准库）
        """
        # 支持的算法列表
        supported_algorithms = ['md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512',
                                'blake2b', 'blake2s',
                                'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512',
                                'shake_128', 'shake_256']
        # 检查算法是否支持
        if algorithm not in supported_algorithms:
            raise ValueError(f'[hash_encrypt] 不支持的算法')
        try:
            hash_obj = getattr(hashlib, algorithm)()
            hash_obj.update(string.encode('utf-8'))
            return hash_obj.hexdigest()
        except Exception as e:
            raise ValueError(f'[hash_encrypt] 加密发生错误: {e}')

    def Hook(self):
        '''可能失效 和环境有关 已弃用'''
        # 开发者测试专用，生成的js脚本可以直接在163.com官网控制台执行，刷新页面后可自动登录成功（必须要先清空cookie 或 退出已登录的账号）
        # hook_js = '''(function(){'use strict';var Cookies=''' + str(self.Token[
        #                                                                 0] if cookie_set_code == 1 else cookie_token_dict) + ''';var d=new Date;d.setTime(d.getTime()+1e3*60*60*24*500000000);document.cookie="MAIL_PASSPORT="+Cookies['MAIL_PASSPORT']+";expires="+d.toGMTString()+";path=/;Domain=.mail.163.com";document.cookie="MAIL_PASSPORT_INFO="+Cookies['MAIL_PASSPORT_INFO']+";expires="+d.toGMTString()+";path=/;Domain=.mail.163.com"})();'''
        hook_js = '''(function(){'use strict';var Cookies=########;var d=new Date;d.setTime(d.getTime()+(5*24*60*60*1000));document.cookie="MAIL_PASSPORT="+Cookies['MAIL_PASSPORT']+";expires="+d.toGMTString()+"; Secure; SameSite=Lax; path=/;Domain=.163.com";document.cookie="MAIL_PASSPORT_INFO="+Cookies['MAIL_PASSPORT_INFO']+";expires="+d.toGMTString()+"; Secure; SameSite=Lax; path=/;Domain=.163.com"})();'''
        hook_js = hook_js.replace('########', json.dumps(self.core_cookie))
        print('【开发者测试】[Hook一键登录浏览器] -> ', hook_js)

    def py_utid(self):
        print('————————————【获取 utid】')
        self.utid = ''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz', k=32))
        # vfELgO2ONXmeRRhWyKpC92r0Ou6mtmPY
        self.print_('[生成][py_utid]|[utid]', self.utid)

    def fgw_mailsrvIpdetail_detail(self):
        print('————————————【获取 stats_session_id】 ')
        headers = {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "no-cache",
            "content-type": "application/json",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://mail.163.com/",
            "sec-ch-ua": self.sec_ch_ua,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
            "user-agent": self.user_agent
        }
        url = "https://mail.163.com/fgw/mailsrv-ipdetail/detail"
        response = self.reques(method='GET', url=url, headers=headers)
        self.code = response_data = response.json()
        response_cookies = response.cookies.get_dict()
        self.print_('[请求结果][fgw_mailsrvIpdetail_detail]|[response]', response_data)
        self.print_('[请求结果][fgw_mailsrvIpdetail_detail]|[cookie]', response_cookies)
        self.print_('[状态码解析][fgw_mailsrvIpdetail_detail]', self.code_analysis())
        self.stats_session_id = response_cookies.get('stats_session_id')
        self.print_('[状态码解析][fgw_mailsrvIpdetail_detail]|[stats_session_id]', self.stats_session_id)

    def fgw_mailsrvDeviceIdmapping_webapp_init(self):
        print('————————————【获取 deviceId | sdid】  授权【stats_session_id】')
        headers = {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "no-cache",
            "content-type": "application/json",
            "origin": "https://mail.163.com",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://mail.163.com/",
            "sec-ch-ua": self.sec_ch_ua,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
            "user-agent": self.user_agent
        }
        cookies = {
            "starttime": "",
            "stats_session_id": self.stats_session_id
        }
        url = "https://mail.163.com/fgw/mailsrv-device-idmapping/webapp/init"
        data = {
            "deviceId": self.deviceId,
            "appVersion": "1.0.0"
        }
        response = self.reques(method='POST', url=url, headers=headers, cookies=cookies, json=data)
        self.code = response_data = response.json()
        response_cookies = response.cookies.get_dict()
        self.print_('[请求结果][fgw_mailsrvDeviceIdmapping_webapp_init]|[response]', response_data)
        self.print_('[请求结果][fgw_mailsrvDeviceIdmapping_webapp_init]|[cookie]', response_cookies)
        self.print_('[状态码解析][fgw_mailsrvDeviceIdmapping_webapp_init]', self.code_analysis())
        self.sdid = response_data['result']['sdid']
        self.print_('[正文][fgw_mailsrvDeviceIdmapping_webapp_init]|[sdid]', self.sdid)
        self.print_('[正文][fgw_mailsrvDeviceIdmapping_webapp_init]|[deviceId]', self.deviceId)
        # # 对照表：19位 '122946681 2967034880'
        # self.sdid = [
        #     1,
        #     random.randint(0, 2),
        #     random.randint(0, 2),
        #     random.randint(0, 9),
        #     random.randint(0, 4),
        #     random.randint(0, 6),
        #     random.randint(0, 6),
        #     random.randint(0, 8),
        #     random.randint(0, 1),
        #     random.randint(0, 2),
        #     random.randint(0, 9),
        #     random.randint(0, 6),
        #     random.randint(0, 7),
        #     random.randint(0, 0),
        #     random.randint(0, 3),
        #     random.randint(0, 4),
        #     random.randint(0, 8),
        #     random.randint(0, 8),
        #     random.randint(0, 0),
        # ]
        # self.sdid = ''.join([str(num) for num in self.sdid])
        # # self.sdid = '1229466812967034880'
        # self.print_('[正文][fgw_mailsrvDeviceIdmapping_webapp_init]|[sdid计算]', self.sdid)
        # self.deviceId_v1 = '_v1'
        # self.print_('[正文][fgw_mailsrvDeviceIdmapping_webapp_init]|[deviceId]', self.deviceId)
        # self.print_('[正文][fgw_mailsrvDeviceIdmapping_webapp_init]|[deviceId_v1]', self.deviceId_v1)
        # self.print_('[正文][fgw_mailsrvDeviceIdmapping_webapp_init]|[stats_session_id]', self.stats_session_id)

    def dl_zj_mail_ini(self):
        print('————————————【获取 capId | l_s_mail163CvViHzl】')
        # 获取 encParams
        encParams = self.reques(method='GET', url=f'{self.node_host}/dl/zj/mail/ini',
                                headers={'Content-Type': 'application/json'}).json()
        self.print_('[加密][dl_zj_mail_ini]|[encParams]', encParams)
        # 获取 capId | l_s_mail163CvViHzl
        data = {"encParams": encParams['encParams']}
        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Origin": "https://dl.reg.163.com",
            "Pragma": "no-cache",
            "Referer": self.Referer,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-GPC": "1",
            "User-Agent": self.user_agent,
            "sec-ch-ua": self.sec_ch_ua,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        cookie = {'utid': self.utid}
        response = self.reques(method='POST', url="https://dl.reg.163.com/dl/zj/mail/ini", headers=headers, json=data, cookies=cookie)
        self.code = response_data = response.json()
        response_cookies = response.cookies.get_dict()
        self.print_('[请求结果][dl_zj_mail_ini]|[response]', response_data)
        self.print_('[请求结果][dl_zj_mail_ini]|[cookie]', response_cookies)
        self.print_('[状态码解析][dl_zj_mail_ini]', self.code_analysis())
        self.capId = response_data['capId']
        self.l_s_mail163CvViHzl = response_cookies['l_s_mail163CvViHzl']
        # self.l_s_mail163CvViHzl = '2BDA1093FDDA9283AD02B57FFFEC7E0E5CF63EC6EC94CB63D2223FB19FB56A25986919B9282C72B73EE307E2DD9A972E36F2E4270ADE27BE7EBBBFFE93ED2B55830E1B54302E4F7DD8DED8332E931DB1E87117AF3A377DC796DD602DBFCC0AA6C774DE2C626D30D682DC00E2BAFC6CD1'
        self.print_('[正文][dl_zj_mail_ini]|[capId]', self.capId)
        self.print_('[正文][dl_zj_mail_ini]|[l_s_mail163CvViHzl]', self.l_s_mail163CvViHzl)
        self.print_('[正文][dl_zj_mail_ini]|[l_s_mail163CvViHzl][提示信息]', '请等待8秒，等待令牌生效...')
        time.sleep(8)  # 等一会，等令牌生效

    def UA1435545636633_1(self):
        headers = {
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "image",
            "Referer": self.Referer,
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-GPC": "1",
            "User-Agent": self.user_agent,
            "sec-ch-ua": self.sec_ch_ua,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        cookies = {
            "utid": self.utid
        }
        params = {
            "useDefaultRegMail": "1",
            "from": "https://mail.163.com/",
            "promark": "CvViHzl",
            "product": "mail163"
        }
        response = self.reques(method='GET', url="https://dl.reg.163.com/UA1435545636633/__utm.gif", headers=headers, params=params, cookies=cookies)

    def UA1435545636633_2(self):
        headers = {
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Referer": self.Referer,
            "Sec-Fetch-Dest": "image",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-GPC": "1",
            "User-Agent": self.user_agent,
            "sec-ch-ua": self.sec_ch_ua,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        cookies = {
            "utid": self.utid,
            "NTES_WEB_FP": self.NTES_WEB_FP
        }
        params = {
            "from": "webzjwebworker",
            "ursfp": self.NTES_WEB_FP,
            "utid": self.utid,
            "name": "webzj_power_pv",
            "sp": "1",
            "ua": self.user_agent
        }
        response = self.reques(method='GET', url="https://dl.reg.163.com/UA1435545636633/__utm.gif", headers=headers, params=params, cookies=cookies)

    def dl_zj_mail_powGetP(self, type = 1):
        print('————————————【获取 pVInfo】')
        if type == 1:
            # 获取 encParams
            encParams = self.reques(method='GET', url=f'{self.node_host}/dl/zj/mail/powGetP', headers={'Content-Type': 'application/json'}).json()
            self.print_('[加密][dl_zj_mail_powGetP]|[encParams]', encParams)
        else:
            # 获取 encParams
            encParams = self.reques(method='POST', url=f'{self.node_host}/dl/zj/mail/powGetP_r',
                                    headers={'Content-Type': 'application/json'}, json={'email': self.email, 'pvSid': self.pVInfo['sid']}
                                    ).json()
            self.print_('[加密][dl_zj_mail_powGetP]|[encParams]', encParams)
        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Origin": "https://dl.reg.163.com",
            "Pragma": "no-cache",
            "Referer": self.Referer,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-GPC": "1",
            "User-Agent": self.user_agent,
            "sec-ch-ua": self.sec_ch_ua,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        cookies = {
            'utid': self.utid,
            "l_s_mail163CvViHzl": self.l_s_mail163CvViHzl,
            "NTES_WEB_FP": self.NTES_WEB_FP,
            "THE_LAST_LOGIN": self.email
        }
        data = {
            "encParams": encParams['encParams']
        }
        response = self.reques(method='POST', url="https://dl.reg.163.com/dl/zj/mail/powGetP", cookies=cookies,
                               headers=headers, json=data)
        self.code = response_data = response.json()
        response_cookies = response.cookies.get_dict()
        self.print_('[请求结果][dl_zj_mail_powGetP]|[response]', response_data)
        self.print_('[请求结果][dl_zj_mail_powGetP]|[cookie]', response_cookies)
        self.print_('[状态码解析][dl_zj_mail_powGetP]', self.code_analysis())
        self.pVInfo = response_data['pVInfo']
        self.print_('[正文][dl_zj_mail_powGetP]|[pVInfo]', self.pVInfo)
    def dl_zj_mail_gt(self):
        print('————————————【获取 tk】')
        # 获取 encParams
        encParams = self.reques(method='POST', url=f'{self.node_host}/dl/zj/mail/gt',
                                headers={'Content-Type': 'application/json'}, json={"email": self.email}).json()
        self.print_('[加密][dl_zj_mail_gt]|[encParams]', encParams)
        # 获取 tk
        data = {"encParams": encParams['encParams']}
        cookies = {
            'utid': self.utid,
            "l_s_mail163CvViHzl": self.l_s_mail163CvViHzl,
            "NTES_WEB_FP": self.NTES_WEB_FP
        }
        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Origin": "https://dl.reg.163.com",
            "Pragma": "no-cache",
            "Referer": self.Referer,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-GPC": "1",
            "User-Agent": self.user_agent,
            "sec-ch-ua": self.sec_ch_ua,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        response = self.reques(method='POST', url="https://dl.reg.163.com/dl/zj/mail/gt", cookies=cookies,
                               headers=headers, json=data)
        self.code = response_data = response.json()
        response_cookies = response.cookies.get_dict()
        self.print_('[请求结果][dl_zj_mail_gt]|[response]', response_data)
        self.print_('[请求结果][dl_zj_mail_gt]|[cookie]', response_cookies)
        self.print_('[状态码解析][dl_zj_mail_gt]', self.code_analysis())
        self.tk = response_data['tk']
        self.print_('[正文][dl_zj_mail_gt]|[tk]', self.tk)

    def dl_zj_mail_l(self):
        '''临时令牌权限'''
        print('————————————【获取 NTES_PASSPORT | NTES_SESS | P_INFO | S_INFO 临时权限(会话级别)】')
        # 获取 encParams
        encParams = self.reques(method='POST', url=f'{self.node_host}/dl/zj/mail/l',
                                headers={'Content-Type': 'application/json'},
                                json={"email": self.email, "password": self.password, "tk": self.tk, 'pVInfo': self.pVInfo}).json()
        self.print_('[加密][dl_zj_mail_l]|[encParams]', encParams)
        # 获取 ---
        data = {"encParams": encParams['encParams']}
        cookies = {
            'utid': self.utid,
            "l_s_mail163CvViHzl": self.l_s_mail163CvViHzl,
            "NTES_WEB_FP": self.NTES_WEB_FP
        }
        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Origin": "https://dl.reg.163.com",
            "Pragma": "no-cache",
            "Referer": "https://dl.reg.163.com/webzj/v1.0.1/pub/index_dl2_new.html?cd=%2F%2Fmimg.127.net%2Fp%2Ffreemail%2Findex%2Funified%2Fstatic%2F2025%2F%2Fcss%2F&cf=urs.163.918051fb.css&MGID=1752714639893.7065&wdaId=&pkid=CvViHzl&product=mail163",
            # "Referer": self.Referer,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-GPC": "1",
            "User-Agent": self.user_agent,
            "sec-ch-ua": self.sec_ch_ua,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        response = self.reques(method='POST', url="https://dl.reg.163.com/dl/zj/mail/l", cookies=cookies,
                               headers=headers, json=data)
        self.code = response_data = response.json()
        if self.code.get('ret') == '805':
            self.dl_zj_mail_powGetP(type=2)
            time.sleep(0.1)
            self.dl_zj_mail_gt()
            time.sleep(0.1)
            self.dl_zj_mail_l()
        response_cookies = response.cookies.get_dict()
        self.cookie = response_cookies
        self.print_('[请求结果][dl_zj_mail_l]|[response]', response_data)
        self.print_('[请求结果][dl_zj_mail_l]|[cookie]', response_cookies)
        self.print_('[状态码解析][dl_zj_mail_l]', self.code_analysis())
        # self.NTES_PASSPORT = response_cookies['NTES_PASSPORT']
        self.NTES_P_UTID = response_cookies['NTES_P_UTID']
        self.NTES_SESS = response_cookies['NTES_SESS']
        self.S_INFO = response_cookies['S_INFO']
        self.P_INFO = response_cookies['P_INFO']
        # self.print_('[正文][dl_zj_mail_l]|[NTES_PASSPORT]', self.NTES_PASSPORT)
        self.print_('[正文][dl_zj_mail_l]|[NTES_P_UTID]', self.NTES_P_UTID)
        self.print_('[正文][dl_zj_mail_l]|[NTES_SESS]', self.NTES_SESS)
        self.print_('[正文][dl_zj_mail_l]|[S_INFO]', self.S_INFO)
        self.print_('[正文][dl_zj_mail_l]|[P_INFO]', self.P_INFO)
        assert self.NTES_P_UTID and self.NTES_SESS and self.S_INFO and self.P_INFO, 'NTES_P_UTID, NTES_SESS, S_INFO, P_INFO 未获取到会话令牌'

    def entry_cgi_ntesdoor(self, types: int = 2, method: Union[Literal['GET', 'POST', 'HEAD']]='POST'):
        """
        @Params   :
            - types:
                -1: 获取 Coremail | sid，用于提取邮件
                -2: 获取 MAIL_PASSPORT | MAIL_PASSPORT_INFO 令牌，用于授权
        """
        if types == 1:
            print(f'————————————【获取 Coremail | sid】{types}')
            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "accept-language": "zh-CN,zh;q=0.9",
                "cache-control": "no-cache",
                "pragma": "no-cache",
                "priority": "u=0, i",
                "referer": "https://mail.163.com/",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\"",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-gpc": "1",
                "upgrade-insecure-requests": "1",
                "User-Agent": self.user_agent,
                "sec-ch-ua": self.sec_ch_ua
            }
            cookies = {
                'MAIL_PASSPORT': self.MAIL_PASSPORT,
                'MAIL_PASSPORT_INFO': self.MAIL_PASSPORT_INFO
            }
            url = "https://mail.163.com/entry/cgi/ntesdoor"
            # params = {
            #     "style": "-1",
            #     "df": "mail163_letter",
            #     "allssl": "true",
            #     "net": "",
            #     "deviceId": self.deviceId,
            #     "sdid": self.sdid,
            #     "language": "-1",
            #     "from": "web",
            #     "race": "",
            #     "iframe": "1",
            #     "url2": "https://mail.163.com/errorpage/error163.htm",
            #     "product": "mail163"
            # }
            params = {
                "lightweight": "1",
                "verifycookie": "1",
                "from": "web",
                "df": "mail163_letter",
                "allssl": "true",
                "deviceId": self.deviceId,
                "sdid": self.sdid,
                "style": "-1"
            }
            response = self.reques(method='HEAD', url=url, headers=headers, cookies=cookies, params=params)
            response_cookies = response.cookies.get_dict()
            self.print_('[请求结果][entry_cgi_ntesdoor]|[cookie]', response_cookies)
            self.Coremail = response_cookies.get('Coremail', '')
            self.sid = (re.findall('%(.*?)%', self.Coremail) + [''])[0]
            self.print_('[正文][entry_cgi_ntesdoor]|[Coremail]', self.Coremail)
            self.print_('[正文][entry_cgi_ntesdoor]|[sid]', self.sid)
            return self.Coremail and True or False
        elif types == 2:
            print(f'————————————【获取 MAIL_PASSPORT | MAIL_PASSPORT_INFO 30天令牌(持续){types}】')
            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "accept-language": "zh-CN,zh;q=0.9",
                "cache-control": "no-cache",
                "content-type": "application/x-www-form-urlencoded",
                "origin": "https://mail.163.com",
                "pragma": "no-cache",
                "priority": "u=0, i",
                "referer": "https://mail.163.com/",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\"",
                "sec-fetch-dest": "iframe",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "sec-gpc": "1",
                "upgrade-insecure-requests": "1",
                "User-Agent": self.user_agent,
                "sec-ch-ua": self.sec_ch_ua
            }
            cookies = {
                'starttime': '',
                "stats_session_id": self.stats_session_id,
                "NTES_SESS": self.NTES_SESS,
                "NTES_PASSPORT": self.NTES_PASSPORT,
                "S_INFO": self.S_INFO,
                "P_INFO": self.P_INFO,
                "nts_mail_user": f"{self.email}:-1:1",
                "df": "mail163_letter"
            }
            url = "https://mail.163.com/entry/cgi/ntesdoor?"
            data = {
                "style": "-1",
                "df": "mail163_letter",
                "allssl": "true",
                "net": "",
                "deviceId": self.deviceId,
                "sdid": self.sdid,
                "language": "-1",
                "from": "web",
                "race": "",
                "iframe": "1",
                "url2": "https://mail.163.com/errorpage/error163.htm",
                "product": "mail163"
            }
            self.cookie = {**self.cookie, **cookies}
            response = self.reques(method='POST', url=url, headers=headers, cookies=self.cookie, data=data)
            response_cookies = response.cookies.get_dict()
            self.print_('[请求结果][entry_cgi_ntesdoor]|[cookie]', response_cookies)
            self.MAIL_PASSPORT = response_cookies.get('MAIL_PASSPORT', '')
            self.MAIL_PASSPORT_INFO = response_cookies.get('MAIL_PASSPORT_INFO', '')
            self.print_('[正文][dl_zj_mail_l]|[MAIL_PASSPORT]', self.MAIL_PASSPORT)
            self.print_('[正文][dl_zj_mail_l]|[MAIL_PASSPORT_INFO]', self.MAIL_PASSPORT_INFO)
            assert self.MAIL_PASSPORT and self.MAIL_PASSPORT_INFO, '[MAIL_PASSPORT | MAIL_PASSPORT_INFO] 未获取到令牌，无法继续'
        elif types == 3:
            print(f'————————————【启动临时登陆临时获取邮件功能 （仅会话|非持续）{types} Coremail | sid】')
            # 需要【NTES_P_UTID | NTES_SESS | S_INFO | P_INFO】
            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "accept-language": "zh-CN,zh;q=0.9",
                "cache-control": "max-age=0",
                "content-type": "application/x-www-form-urlencoded",
                "origin": "https://mail.163.com",
                "priority": "u=0, i",
                "referer": "https://mail.163.com/",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\"",
                "sec-fetch-dest": "iframe",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-gpc": "1",
                "upgrade-insecure-requests": "1",
                "user-agent": self.user_agent,
                "sec-ch-ua": self.sec_ch_ua
            }
            cookies = {
                "starttime": "",
                "stats_session_id": self.stats_session_id,
                "nts_mail_user": f"{self.email}:-1:1",
                "df": "mail163_letter",
                **self.cookie
            }
            url = "https://mail.163.com/entry/cgi/ntesdoor"
            params = {
                "": ""
            }
            data = {
                "style": "-1",
                "df": "mail163_letter",
                "allssl": "true",
                "net": "",
                "deviceId": self.deviceId,
                "sdid": self.sdid,
                "language": "-1",
                "from": "web",
                "race": "",
                "iframe": "1",
                "url2": "https://mail.163.com/errorpage/error163.htm",
                "product": "mail163"
            }
            response = self.reques(method=method, url=url, headers=headers, cookies=cookies, data=data, params=params)
            response_cookies = response.cookies.get_dict()
            self.print_('[请求结果][entry_cgi_ntesdoor]|[cookie]', response_cookies)
            self.Coremail = response_cookies.get('Coremail', '')
            if not self.Coremail:
                self.EmailCookie(types=3)  # 移除cookie
                return False
            self.sid = (re.findall('%(.*?)%', self.Coremail) + [''])[0]
            self.print_('[正文][entry_cgi_ntesdoor]|[Coremail]', self.Coremail)
            self.print_('[正文][entry_cgi_ntesdoor]|[sid]', self.sid)
            return True
        else:
            raise ValueError('[entry_cgi_ntesdoor] types 参数错误')

    def js6_s(self, types: int = 1, limit: int = 30):
        cookies = {
            'Coremail': self.Coremail
        }
        headers = {
            'accept': 'text/javascript',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://mail.163.com',
            'priority': 'u=1, i',
            'sec-ch-ua': self.sec_ch_ua,
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'user-agent': self.user_agent,
        }
        # 【正常读取验证码】limit设置为30，从30个邮件内获取指定邮件且最新的邮件mid（设置30是为了防止短时间内有其他邮件信息把我们所需要的邮件顶下去）
        # 【删除邮件】limit设置为10000-20000，一次性读取所有的邮件mid,无序，然后传递给其他进行删除操作
        data = {
            'var': f'<?xml version="1.0"?><object><int name="fid">1</int><string name="order">date</string><boolean name="desc">true</boolean><int name="limit">{limit}</int></object>',
        }
        if types == 1:  # 获取邮件验证码
            print('————————————【获取邮件 mid 用于获取邮件验证码】')
            response = self.reques(method='POST',
                                   url=f'https://mail.163.com/js6/s?sid={self.sid}&func=mbox:listMessages',
                                   cookies=cookies, headers=headers, data=data)
            self.print_('[请求结果][js6_s]|[状态码]', response.status_code)
            data = json5.loads(self.date_change_str_time(response.text, 1))
            print(data)
            # mid占位
            self.dict_id = {}
            # 从 几封邮件中筛选出10分钟内最新的邮件并且是官方的邮件，并返回字典数据邮件mid
            for data_dict in data['var']:
                # 将字典内的时间字符串转换为 datetime 对象
                target_time = datetime.strptime(data_dict['receivedDate'], "%Y-%m-%d %H:%M:%S")
                # 计算邮件收到的时间和当前时间误差是多少秒（以秒为单位）
                time_difference = int((datetime.now() - target_time).total_seconds())
                # 1、判断 subject 标题是否一致
                # 2、判断邮件是否是10分钟内的  600秒，可自定义修改
                _ = any(keyword in data_dict['subject'] for keyword in self.platform_mapping[self.platform]['subject'])
                self.print_(f'时间|邮件mid|平台是否匹配且是否有验证码邮件{limit}', data_dict['receivedDate'],
                            data_dict['id'], _)
                if _ and time_difference <= 600:
                    # 存储字典为空的情况下，直接把当前合格的字典存储起来。如果有另一封合格邮件，则对比时间，取最新的邮件进行存储
                    if (not self.dict_id) or (
                            self.dict_id and target_time > datetime.strptime(self.dict_id['receivedDate'],
                                                                             "%Y-%m-%d %H:%M:%S")):
                        self.dict_id = {
                            'id': data_dict['id'],
                            'receivedDate': data_dict['receivedDate']
                        }
            # 最新的邮件mid编号： {'id': '168:1tbiqBsVxmfaXVIWmAAAsc', 'receivedDate': '2025-03-19 14:19:52'}
            self.print_('[正文][js6_s]|[最新的邮件 mid 编号]', self.dict_id)
            # 只返回一个 168:1tbiqBsVxmfaXVIWmAAAsc 邮件的编号，这个邮件就是有验证码的，如果没有编号，说明在10分钟内就没有接收到平台的验证码，则返回空字符串。
            # assert self.dict_id,
            if not self.dict_id:
                raise ValueError(f'未检测到10分钟内此平台发送的验证码 - {self.platform}')
            self.mid = self.dict_id['id']
            self.print_('[正文][js6_s]|[mid]', self.mid)
        elif types == 2:  # 删除所有邮件
            print('————————————【获取邮件 mid 用于删除所有邮件】')
            response = self.reques(method='POST',
                                   url=f'https://mail.163.com/js6/s?sid={self.sid}&func=mbox:listMessages',
                                   cookies=self.cookie, headers=headers, data=data)
            self.print_('[请求结果][js6_s]|[状态码]', response.status_code)
            mid_list = re.findall("'id':'(.*?)'", response.text)
            # 去重 并 转为 list[html代码]
            data_list = [f'<string>{data}</string>' for data in list(set(mid_list)) if data]
            data_str = ''.join(data_list)  # 转str
            self.print_(f'[正文][js6_s]|[数量|获取要删除邮件]', len(data_list), data_str[:200])
            self.mid = data_str
            self.print_('[正文][js6_s]|[mid]', data_str[:100])
        else:
            raise ValueError('[js6_s] types 参数错误')

    def js6_read_readhtmlJsp(self):
        print('————————————【读取 mid 邮件ID码】')
        cookies = {
            'Coremail': self.Coremail,
            'Coremail.sid': self.sid
        }
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-language': 'zh-CN,zh;q=0.9',
            'priority': 'u=0, i',
            'sec-ch-ua': self.sec_ch_ua,
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'iframe',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'sec-gpc': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': self.user_agent,
        }
        response = self.reques(method='GET',
                               url=f'https://mail.163.com/js6/read/readhtml.jsp?mid={self.mid}&userType=ud&font=15&color=3370FF',
                               cookies=cookies, headers=headers)
        self.print_('[请求结果][js6_read_readhtmlJsp]|[状态码]', response.status_code)
        req_data = str(response.text).replace('\n', '').replace('\n', '').replace('\t', '').replace('\r', '').replace('\f', '')

        # 提取验证码 Tiktok
        self.print_('re', self.platform_mapping[self.platform]['re'])
        Verification = re.findall(self.platform_mapping[self.platform]['re'], req_data) + ['']
        self.print_('邮箱验证码', Verification)
        Verification = (lambda x: x[0] if isinstance(x[0], str) else next((x[0] or x[1] for x in x), None))(
            Verification)
        Verification = Verification.strip()
        # 邮箱验证码： RW4Y8N
        self.print_('邮箱验证码剥离', Verification)
        assert Verification, f'验证码捕获失败，正则需修改 - {self.platform}'
        self.Verification = Verification

    # 官方接口 删除邮件功能，删除的主入口 【手动调用】
    def del_js6_s(self):
        '''删除所有邮件 至 已删除 [一次删除20000个邮件]'''
        headers = {
            "accept": "text/javascript",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "no-cache",
            "content-type": "application/x-www-form-urlencoded",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "sec-ch-ua": self.sec_ch_ua,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
            "user-agent": self.user_agent,
        }
        cookies = {
            'Coremail': self.Coremail
        }
        # 删除【正常的邮件】可一次性删除20000个，目前未发现需要身份验证
        data = {
            'var': f'<?xml version="1.0"?><object><array name="ids">{self.mid}</array><object name="attrs"><int name="fid">4</int></object></object>',
        }
        response = self.reques(method='POST',
                               url=f"https://mail.163.com/js6/s?sid={self.sid}&func=mbox:updateMessageInfos",
                               cookies=cookies, headers=headers, json=data)
        if response.status_code == 200:
            self.print_('[成功删除][del_js6_s]|[状态码]', response.status_code)
        else:
            self.print_('[删除失败][del_js6_s]|[状态码|正文]', response.status_code, response.text)
        # 执行【获取所有已删除的邮件mid】
        self.get_all_del_js6_s()

    # 官方接口 获取所有已删除的邮件mid
    def get_all_del_js6_s(self):
        '''获取所有已删除的邮件mid'''
        headers = {
            "accept": "text/javascript",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "no-cache",
            "content-type": "application/x-www-form-urlencoded",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "sec-ch-ua": self.sec_ch_ua,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
            "user-agent": self.user_agent,
        }
        cookies = {
            'Coremail': self.Coremail
        }
        # 一次性获取28000个，方便删除 这个固定不要修改，都是经过严格测试的
        data = {
            'var': f'<?xml version="1.0"?><object><int name="fid">4</int><string name="order">date</string><boolean name="desc">true</boolean><int name="limit">28000</int><int name="start">0</int><boolean name="skipLockedFolders">false</boolean><boolean name="returnTag">true</boolean><boolean name="returnTotal">true</boolean><string name="mrcid">{self.deviceId}</string></object>',
        }
        response = self.reques(method='POST',
                               url=f"https://mail.163.com/js6/s?sid={self.sid}&func=mbox:listMessages",
                               cookies=cookies, headers=headers, json=data)
        self.print_('[请求结果][get_all_del_js6_s]|[状态码]', response.status_code)
        mid_list = re.findall("'id':'(.*?)'", response.text)
        # data_list = [f'<string>{data}</string>' for data in list(set(mid_list)) if data]
        # data_str = ''.join(data_list)
        # self.mid = data_str
        # print(f'[获取所有已删除的邮件mid] -> 数量：{len(data_list)} 数据：{data_str[:200]}')
        # 去重
        mid_list = list(set(mid_list))
        self.print_('[获取所有已删除的邮件mid][get_all_del_js6_s]|[数量|数据]', len(mid_list), mid_list[:200])
        # 将列表数据分批，每次最多498条，避免一次性删除太多支撑不住
        mid_list = [mid_list[i:i + 498] for i in range(0, len(mid_list), 498)]
        self.print_('[分批删除][get_all_del_js6_s]', mid_list)
        # 转html并存储到列表内
        data_list = ['<string>' + ('</string><string>'.join(i) + '</string>') for i in mid_list]
        self.mid_list = data_list

        # 执行【删除所有已删除的邮件，彻底删除】
        self.del_all_deleted_emails_js6_s()

    # 官方接口 获取临时彻底删除邮件的权限token 此token为会话级，只能作为临时使用，有效期预估为1天左右，不适合存储
    def get_temporary_del_token(self) -> Union[dict, str]:
        '''
        获取临时彻底删除邮件的权限token
        注意：如果此token获取不到，则说明邮箱有异常，需要验证身份才能进行删除邮件，但不影响查看邮件和读取邮件内的验证码
        '''
        headers = {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "no-cache",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://mail.163.com",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://mail.163.com/js6/main.jsp?sid",
            "sec-ch-ua": self.sec_ch_ua,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
            "user-agent": self.user_agent
        }
        cookies = {
            "Coremail": self.Coremail
        }
        data = {
            "actionId": "eec599711e6041238d",  # 固定的id    b1c13ae21986484e86 这个是修改个人信息的id
            "environment": json.dumps({"mrcid": self.deviceId, "mrecp": {}, "mrvar": quote(
                f'<?xml version="1.0"?><object><array name="ids"></array><string name="mrcid">{self.deviceId}</string></object>'),
                                       "hl": "zh_CN"})
        }
        __hid = self.hash_encrypt(self.email, 'md5')[:4].upper()
        self.print_(f'[获取临时删除邮件权限令牌][自加密键值]', __hid)
        response = self.reques(method='POST',
                               url="https://mail.163.com/fgw/mailserv-risk-control/risk/action/token?1750225081591=",
                               cookies=cookies, headers=headers, data=data)
        response_cookies = response.cookies.get_dict()
        self.print_('[请求结果][get_temporary_del_token]|[cookie]', response_cookies)
        MAIL_RISK_CTRL = response_cookies.get(f'MAIL_RISK_CTRL_{__hid}', '')

        self.print_(f'[正文][get_temporary_del_token]|[MAIL_RISK_CTRL_{__hid}]', MAIL_RISK_CTRL)
        assert MAIL_RISK_CTRL, '[get_temporary_del_token] 获取临时删除邮件权限令牌失败'
        return {f'MAIL_RISK_CTRL_{__hid}': MAIL_RISK_CTRL}

    # 官方接口 删除所有已删除的邮件，彻底删除
    def del_all_deleted_emails_js6_s(self):
        '''删除所有已删除的邮件，彻底删除 此步骤执行预估消耗时间：2秒可用删除498封，28000封预估需要1分20秒左右'''
        headers = {
            "accept": "text/javascript",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "no-cache",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://mail.163.com",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://mail.163.com/js6/main.jsp?sid",
            "sec-ch-ua": self.sec_ch_ua,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
            "user-agent": self.user_agent
        }
        cookies = {
            'Coremail': self.Coremail,
            **self.get_temporary_del_token()
            # 获取删除【彻底删除权限】的token，这个token如果获取不了，说明邮箱是异常的，需要手机验证，还有一种情况是邮箱检测可能有盗号的风险，也是无法删除的
        }
        if len(cookies) < 2:
            return ''
        # 删除28000封邮件预估1分20秒内
        # 循环遍历删除，删除【已删除的邮件】每次最多只能删除498个，所以只能遍历删除
        for mid_str in self.mid_list:
            data = {
                'var': f'<?xml version="1.0"?><object><array name="ids">{mid_str}</array><string name="mrcid">{self.deviceId}</string></object>',
            }
            response = self.reques(method='POST',
                                   url=f"https://mail.163.com/js6/s?sid={self.sid}&func=mbox:deleteMessages",
                                   cookies=cookies, headers=headers, data=data)
            self.print_('[请求结果][del_all_deleted_emails_js6_s]|[状态码]', response.status_code)
            print(f'[彻底删除{mid_str.count("<string>")}] ->', json5.loads(response.text))
            time.sleep(round(random.uniform(0, 1), 2) or 1)

    def print_(self, *args: any) -> None:
        """开发者测试专用 可代替print打印"""
        formatted_time = datetime.fromtimestamp(time.time()).strftime("%H:%M:%S.%f")[:-3]  # %Y/%m/%d %H:%M:%S.%f
        if len(args) > 1:
            label, *values = args
            type_str = "".join(f"[{type(v).__name__}]" for v in values)
            value_str = " ".join(f"[{v}]" for v in values)
            print(f'[{formatted_time}][{label}] | {type_str} -> {value_str}')
            return
        elif len(args) == 1:
            # 打印单数值
            print(f'[{formatted_time}][{type(args[0]).__name__}] -> [{args[0]}]')

# email_163 = EmailService163(
#     email='vgregwds@163.com',   # 邮箱号
#     node_host='http://172.16.2.5:4000',  #  http://172.16.2.5:4000 'http://127.0.0.1:4001',  # nodejs逆向接口地址
#     servers_host='http://rpa.spocoo.com',  # 正式环境地址
#     platform='tiktok'    # 平台
# )
#
# email_163.get_verification()
# print(email_163.verification_code)

