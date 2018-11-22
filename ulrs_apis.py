from flask_restful import Api
from .apis import *
api = Api()

def init_api(app):
    api.init_app(app)

# 写一堆路由了
api.add_resource(RegisterAPI, "/api/register")
api.add_resource(ItemAPI, "/api/item")
api.add_resource(OrderStatusAPI, "/api/order/status")