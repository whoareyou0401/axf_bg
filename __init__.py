from flask import Flask
from myapp.ext import init_ext
from myapp.settings import config
from myapp.ulrs_apis import init_api
from myapp.views import init_blue


def create_app(env):
    app = Flask(__name__)

    # 配置
    app.config.from_object(config.get(env))

    # 做初始化第三方的插件
    init_ext(app)

    # 注册蓝图
    init_blue(app)
    # 注册restful的路由
    init_api(app)
    return app