import json
import imaplib
import email
import time
import pytz
import chardet
import re
from bs4 import BeautifulSoup
from email.header import decode_header
from datetime import datetime, timedelta

from rpa_common import Common
from rpa_common.exceptions import EmailException

common = Common()

class EmailService():
    def __init__(self):
        super().__init__()

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