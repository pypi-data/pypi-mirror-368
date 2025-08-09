# eny.py
import os

# 获取当前环境，默认为 development
ENV = os.getenv("RPA_ENV", "development")

# 根据当前环境加载配置
if ENV == "development":
    from rpa_common.config.development import rabbitmq
    from rpa_common.config.development.server import server
elif ENV == "test":
    from rpa_common.config.test.rabbitmq import rabbitmq
    from rpa_common.config.test.server import server
elif ENV == "production":
    from rpa_common.config.production.rabbitmq import rabbitmq
    from rpa_common.config.production.server import server
else:
    raise ValueError(f"❌ 不支持的环境变量: {ENV}，请设置为 'development', 'test' 或 'production'。")

class Env:
    def __init__(self):
        super().__init__()

    def get(self):
        server_data = server.default()

        api = server_data['api']
        cdn = server_data['cdn']

        data = {
            "api": api,
            "cdn": cdn,
            "version": "1.0.0",
            "rabbitmq": rabbitmq.default(),
        }

        return data