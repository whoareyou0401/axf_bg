from flask import Blueprint, render_template, request

from myapp.util import get_no_sale, get_data
from .models import *
blue = Blueprint("axfbg", __name__)

def init_blue(app):
    app.register_blueprint(blue)


# 写一些视图函数
@blue.route("/")
def item_view():
    # print(request.host_url)
    # print(request.host)
    page = request.args.get('page', 1)
    pagination = Goods.query.paginate(int(page), 8)
    return render_template("item/item.html", pagination=pagination, show=True)

@blue.route("/item_search")
def item_search():
#     参数
    kw = request.args.get("kw")
    pagination = Goods.query.filter(Goods.productlongname.contains(kw)).paginate(1, 8)

    return render_template("item/item.html", pagination=pagination, kw=kw, show=False)

@blue.route("/oder_manage")
def order_manage():
    """
        (1, "待付款"),
        (2, "已付款"),
        (3, "已发货"),
        (4, "已收货"),
        (5, "待评价"),
        (6, "已评价")

    """
    # 查所有的订单
    status_map = {
        1: "待付款",
        2: "已付款",
        3: "已发货",
        4: "已收货",
        5: "待评价",
        6: "已评价"
    }
    all_orders = Order.query.all()
    # 遍历订单 格式化时间 算钱
    for i in all_orders:
        i.created_time = i.create_time.strftime("%Y年%m月%d日 %H:%M:%S")
    #     算钱
        sum_money = 0
        for j in i.order_items:
            sum_money = sum_money + j.num * j.buy_money
        i.sum_money = sum_money
    #     将订单的状态的数字变成文字
        i.ch_status = status_map.get(i.status)

    # for i in all_orders:
    #     print("订单的id", i.id)
    #     print("订单状态", i.ch_status)
    #     print("时间", i.created_time)
    #     print("钱", i.sum_money)
    #     for j in i.order_items:
    #         print(j.goods.productlongname)




    return render_template("order/order_index.html", all_orders=all_orders)

@blue.route("/nosale")
def nosale():
    get_no_sale()
    return render_template("nosale/nosale.html")


@blue.route("/auto_bh")
def auto_bh():
    get_data()
    return render_template("auto/auto.html")

@blue.route("/index")
def index():
    return render_template("index/index.html")

@blue.route("/register")
def register_view():
    return render_template("register/register.html")