from math import ceil

import hashlib
import uuid

from flask import render_template
from flask_mail import Message
from sqlalchemy import create_engine
from datetime import datetime, timedelta

engine = create_engine("mysql+pymysql://root:liuda6015?@127.0.0.1:3306/hzaxf1806")

def enc_pwd(pwd):
    sha256 = hashlib.sha256()
    sha256.update(pwd.encode("utf-8"))
    return sha256.hexdigest()

def create_unique_str():
    uuid_str = str(uuid.uuid4()).encode("utf-8")

    md5 = hashlib.md5()
    md5.update(uuid_str)

    return md5.hexdigest()

def send_emails(reciver, url, u_id, cache, mail):

    msg = Message("欢迎注册爱鲜蜂后台管理",
                  [reciver],
                  sender="493024318@qq.com"
        )
    msg.html = render_template("active.html", url=url)
    mail.send(msg)

    key = url.split("/")[-1]
    cache.set(key, u_id, timeout=60*60)


def data_to_dict(cursor):
    heads = [i[0] for i in cursor.description]
    return [ dict(zip(heads, col)) for col in cursor.fetchall()]


def get_no_sale():
    # 创建数据库的连接
    con = engine.connect()
    # 获取十五天之前的时间
    five_ten_days = datetime.now() - timedelta(days=15)

    sql = """
        SELECT 
          DISTINCT i.goods_id 
        FROM 
          myaxf_order AS o 
        LEFT JOIN 
          myaxf_orderitem AS i
        ON 
          o.id = i.order_id
        WHERE 
          o.create_time > '{my_time}'
        AND 
          o.create_time<now()
    """.format(my_time=str(five_ten_days))

    res = con.execute(sql)
    goods_ids = data_to_dict(res.cursor)
    print(goods_ids)
    # 有一个集合
    goods_tmp = []
    for i in goods_ids:
        goods_tmp.append(list(i.values())[0])

    all_goods_sql = '''
        select  id, storenums,price from axf_goods;
    '''
    all_goods = data_to_dict(con.execute(all_goods_sql).cursor)
    print(all_goods)
    # all_goods_tmp = []
    # for i in all_goods:
    #     all_goods_tmp.append(list(i.values())[0])
    # {
    #   商品的id:{"storenums":200, "name": "tome"},
    #   商品的id:{"storenums":200, "name": "tome"},
    #   商品的id: {"storenums": 200, "name": "tome"},
    #   }
    goods_maps = {}
    for i in all_goods:
        goods_maps[i.get("id")] = {
            "storenums": i.get("storenums"),
            "price": i.get("price")
        }
    # print(goods_maps)
    # 转成结合 然后相减
    result = list(set(goods_maps.keys()) - set(goods_tmp))
    # print(result)


def get_data():
    get_goods_day = 3
    my_time = datetime.now() - timedelta(days=get_goods_day*5)

    sql = """
        SELECT 
          i.goods_id, sum(i.num) AS sum_num, ag.storenums, ag.productlongname, ag.productimg
        FROM
          myaxf_order as o 
        LEFT JOIN 
          myaxf_orderitem AS i
        ON 
          o.id=i.order_id
        LEFT JOIN 
          axf_goods as ag
        ON 
          i.goods_id=ag.id
        WHERE 
          o.create_time>"{my_time}"
        AND 
          o.create_time<now()
        GROUP BY 
          i.goods_id
    """.format(my_time=my_time)

    con = engine.connect()
    res = con.execute(sql)
    result = data_to_dict(res.cursor)
    bh_map = {}
    print(result)
    # 求平均销量 然后乘以get_goods_day就得到了未来三天需要的商品数量
    for i in result:
        i['need'] = ceil((float(i.get("sum_num")) / (get_goods_day * 5)) * get_goods_day)
        if i['need'] >= i['storenums']:
            bh_map[i.get("goods_id")] = {
                "need": i["need"],
                "storenums": i['storenums'],
                "img": i['productimg'],
                "name": i["productlongname"]
            }

    print(bh_map)
    return bh_map