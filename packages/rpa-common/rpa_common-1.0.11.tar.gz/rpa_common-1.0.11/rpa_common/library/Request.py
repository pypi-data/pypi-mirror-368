import json
import time
import requests
import requests
import mimetypes
import pandas as pd
from io import BytesIO, StringIO
from urllib.parse import urlparse
from typing import Union, Dict, Literal, List
from rpa_common.library.Decorator import retry

class Request():
    def __init__(self):
        super().__init__()

    def get(self, url, data, headers=None):
        '''
        @描述    : GET 请求
        @作者    : 钟水洲
        @时间    : 2024/05/31 10:20:48
        '''
        try:
            res = requests.get(url, params=data, headers=headers)
            res.raise_for_status()  # 如果响应状态码是 4xx 或 5xx，则抛出 HTTPError 异常
            return res.json()  # 如果响应是 JSON 格式，返回 JSON 数据
        except requests.exceptions.HTTPError as http_err:
            print(f"发生 HTTP 错误: {http_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"发生请求错误: {req_err}")
        except ValueError as json_err:
            print(f"JSON 解码失败: {json_err}")
            return res.text  # 如果 JSON 解码失败，返回原始文本响应
        return None  # 如果发生错误，返回 None

    def post(self, url, data, files=None, headers=None):
        '''
        @描述    : POST 请求
        @作者    : 钟水洲
        @时间    : 2024/05/31 10:20:53
        '''
        try:
            if files:
                res = requests.post(url, data=data, files=files, headers=headers)
            else:
                res = requests.post(url, data=data, headers=headers)

            res.raise_for_status()  # 如果响应状态码不正确，则抛出 HTTPError 异常
            return res.json()  # 如果响应是 JSON 格式，返回 JSON 数据
        except requests.exceptions.HTTPError as http_err:
            print(f"发生 HTTP 错误: {http_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"发生请求错误: {req_err}")
        except ValueError as json_err:
            print(f"JSON 解码失败: {json_err}")
            return res.text  # 如果 JSON 解码失败，返回原始文本响应
        return None  # 如果发生错误，返回 None

    def reques(self, *, max_retries=3, delay=1, exceptions=(Exception,), status_code: Union[None, List[int]]=None,
               method: Literal['GET', 'POST', 'HEAD'],
               url,
               data=None,
               json=None,
               cookies=None,
               headers=None,
               params=None,
               timeout=None,
               files=None
               ) -> requests.Response:
        """
        @Desc     : requests请求方法封装
        @Author   : 祁国庆
        @Time     : 2025/07/21 10:44:10
        @Params   :
            - max_retries: 最大重试次数
            - delay: 重试间隔时间(秒)
            - exceptions: 需要重试的异常类型
            - status_code: 白名单状态码条件重试，非白名单的状态码会进行重试，None为不开启
        @Returns  : 返回此方法 requests.Response
        用法示例：reques(method='GET', url='https://www.xxx.com', params={'t': 1752681600})
        支持自定义重试次数、条件重试
        """
        @retry(max_retries=max_retries, delay=delay, exceptions=exceptions)
        def _(*,
               method: Literal['GET', 'POST', 'HEAD'],
               url,
               data = None,
               json = None,
               cookies = None,
               headers = None,
               params = None,
               timeout = None,
               files = None
               ):
            assert method in ['GET', 'POST', 'HEAD'], '[reques]method参数错误'
            assert url, '[reques]url参数不能为空'
            request = getattr(requests, method.lower())
            response = request(**{
                'url': url,
                'data': data,
                'json': json,
                'cookies': cookies,
                'headers': headers,
                'params': params,
                'timeout': timeout,
                'files': files
            })
            if status_code and response.status_code not in status_code:
                raise Exception(f'[reques]当前状态码:{response.status_code} | 白名单状态码:{status_code}')
            return response
        return _(**{
            'method': method,
            'url': url,
            'data': data,
            'json': json,
            'cookies': cookies,
            'headers': headers,
            'params': params,
            'timeout': timeout,
            'files': files
        })

    @retry(max_retries=5, delay=2, exceptions=(ValueError))
    def downloadExcel(self, url, head={}):
        '''
        @Desc    : 获取远程表格文件内容（支持xlsx/xls/csv）
        @Author  : 黄豪杰
        @return  : 多维数组或JSON字符串
        @Time    : 2025/03/28 09:55:13
        '''
        if not url:
            return []

        cookies = head.get('cookies', {})
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            **head.get('headers', {})
        }
        
        try:
            # 发送 GET 请求获取文件内容
            response = requests.get(url, cookies=cookies, headers=headers, stream=True)
            response.raise_for_status()
            
            # 获取文件类型
            content_type = response.headers.get('Content-Type', '').lower()
            parsed_url = urlparse(url)
            file_ext = parsed_url.path.split('.')[-1].lower() if '.' in parsed_url.path else ''
            
            # 根据类型处理不同格式
            content = response.content
            
            if 'excel' in content_type or file_ext in ('xls', 'xlsx'):
                return self._process_excel(content)
            elif 'csv' in content_type or file_ext == 'csv':
                return self._process_csv(content)
            else:
                # 尝试自动检测类型
                try:
                    return self._process_excel(content)
                except Exception:
                    return self._process_csv(content)
                    
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"下载文件失败: {e}")
        except Exception as e:
            raise ValueError(f"处理表格文件时出错: {e}")

    def _process_excel(self, content):
        """处理Excel文件（xlsx/xls）"""
        with BytesIO(content) as buffer:
            with pd.ExcelFile(buffer) as xls:
                excel_data = {}
                for sheet_name in xls.sheet_names:
                    df = pd.read_excel(xls, sheet_name=sheet_name)
                    df.fillna("", inplace=True)
                    excel_data[sheet_name] = df.to_dict(orient='records')
                return excel_data

    def _process_csv(self, content):
        """处理CSV文件"""
        # 尝试常见编码
        encodings = ['utf-8', 'gbk', 'latin1', 'iso-8859-1']
        for encoding in encodings:
            try:
                with StringIO(content.decode(encoding)) as buffer:
                    df = pd.read_csv(buffer)
                    df.fillna("", inplace=True)
                    return {'Sheet1': df.to_dict(orient='records')}
            except UnicodeDecodeError:
                continue
        raise ValueError("无法解析CSV文件的编码")