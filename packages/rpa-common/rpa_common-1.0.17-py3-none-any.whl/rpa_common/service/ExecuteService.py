import json
import urllib.parse

class ExecuteService():
    def __init__(self):
        super().__init__()

    def request(self, driver, url, method="POST", params=None, data=None, headers=None):
        '''
        @Desc    : 请求
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 请求方式转大写
        method = method.upper()

        # 拼接URL参数
        if params:
            query_string = urllib.parse.urlencode(params)
            separator = '&' if '?' in url else '?'
            url = f"{url}{separator}{query_string}"

        # 默认请求内容
        if data is None:
            data = {}

        # 请求头
        if headers is None:
            headers = {
                "content-type": "application/json"
            }

        # 请求内容
        body = json.dumps(json.dumps(data, ensure_ascii=False), ensure_ascii=False)

        js_script = f"""
            const done = arguments[0];
            (async () => {{
                try {{
                    const res = await fetch("{url}", {{
                        method: "{method}",
                        credentials: "include",
                        mode: "cors",
                        headers: {headers},
                        referrer: document.referrer,
                        referrerPolicy: "strict-origin-when-cross-origin",
                        {"body: " + body + "," if method != "GET" else ""}
                    }});
                    const text = await res.text();
                    done(text);
                }} catch (e) {{
                    done("ERROR: " + e.toString());
                }}
            }})();
        """

        return driver.execute_async_script(js_script)

    def request_file(self, driver, url, file_url, method="POST", params=None, data=None, headers=None):
        '''
        @Desc    : 请求
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        method = method.upper()

        # 拼接 URL 查询参数
        if params:
            query_string = urllib.parse.urlencode(params)
            url = f"{url}?{query_string}" if "?" not in url else f"{url}&{query_string}"

        if data is None:
            data = {}

        # 默认请求头（浏览器会自动设置 multipart/form-data 的 boundary）
        if headers is None:
            headers = {}  # 不要手动设置 Content-Type，浏览器会自动处理

        # 构造 JS 可用的 data 键值对
        form_data_entries = [f'["{key}", "{value}"]' for key, value in data.items()]

        js_script = f"""
            const done = arguments[0];
            (async () => {{
                try {{
                    // 获取文件
                    let formData = new FormData();
                    const fileResponse = await fetch("{file_url}");
                    const blob = await fileResponse.blob();
                    formData.append("data", blob);

                    // 添加表单参数
                    const formParams = [{", ".join(form_data_entries)}];
                    formParams.forEach(([key, value]) => {{
                        formData.append(key, value);
                    }});

                    // 发送请求
                    const res = await fetch("{url}", {{
                        method: "{method}",
                        headers: {headers},
                        body: formData,
                    }});
                    const text = await res.text();
                    done(text);
                }} catch (e) {{
                    done("ERROR: " + e.toString());
                }}
            }})();
        """
        return driver.execute_async_script(js_script)