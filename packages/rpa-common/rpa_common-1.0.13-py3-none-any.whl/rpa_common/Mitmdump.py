import os
import io
import hashlib
import base64
import json
import sys
from pathlib import Path
from mitmproxy import http

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

CACHEABLE_EXTS = ['.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.woff', '.woff2', '.ttf']

params = {}
if len(sys.argv) > 1:
    try:
        decoded_str = base64.b64decode(sys.argv[-1]).decode('utf-8')
        params.update(json.loads(decoded_str))
        print("✅ 参数加载成功：", params)
    except Exception as e:
        print("❌ 参数解析失败：", e)

CACHE_DIR = Path(__file__).resolve().parent / "cache" / "cdn"
os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_path(url):
    url_hash = hashlib.sha256(url.encode('utf-8')).hexdigest()
    return CACHE_DIR / url_hash

def request(flow: http.HTTPFlow):
    url = flow.request.pretty_url
    ext = os.path.splitext(url.split("?")[0])[1].lower()

    if ext not in CACHEABLE_EXTS:
        return

    cache_path = get_cache_path(url)
    if cache_path.exists():
        try:
            with open(cache_path, 'rb') as f:
                raw_data = f.read()
            flow.response = http.HTTPResponse.make(
                200,
                raw_data,
                {"Content-Type": flow.response.headers.get("Content-Type", "application/octet-stream")}
            )
            print(f"📦 从缓存读取：{url}")
        except Exception as e:
            print(f"❌ 读取缓存失败：{e}")
    else:
        print(f"📥 缓存未命中，准备请求真实资源：{url}")

def response(flow: http.HTTPFlow):
    url = flow.request.pretty_url
    ext = os.path.splitext(url.split("?")[0])[1].lower()

    if ext not in CACHEABLE_EXTS:
        return
    if flow.response.status_code != 200:
        return

    cache_path = get_cache_path(url)
    content = flow.response.raw_content or b""
    current_md5 = hashlib.md5(content).hexdigest()

    # 判断是否需要更新缓存
    need_update = True
    if cache_path.exists():
        try:
            with open(cache_path, 'rb') as f:
                old_content = f.read()
            old_md5 = hashlib.md5(old_content).hexdigest()
            if old_md5 == current_md5:
                need_update = False
        except Exception as e:
            print(f"❌ 读取旧缓存失败：{e}")

    if need_update:
        try:
            with open(cache_path, 'wb') as f:
                f.write(content)
            print(f"✅ 缓存已更新：{url}")
        except Exception as e:
            print(f"❌ 缓存失败：{e}")
    else:
        print(f"🟡 内容未变，无需更新缓存：{url}")
