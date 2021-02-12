import os
from io import BytesIO
from datetime import datetime, timedelta
import base64

from flask import Blueprint, request, current_app, redirect, flash
from alipay import AliPay
from alipay.utils import AliPayConfig
import qrcode

from sql import connect_dictCursor


def alipay_ini():
    with open(os.path.join(current_app.root_path, 'trade/app_private_key.pem')) as f:
        app_private_key_string = f.read()
    with open(os.path.join(current_app.root_path, 'trade/alipay_public_key.pem')) as f:
        alipay_public_key_string = f.read()
    alipay = AliPay(
        appid="2021001146618124",
        app_notify_url="http://sorapage.com/alipay/callback",
        app_private_key_string=app_private_key_string,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2",
        debug=False,  # 默认False
        verbose=False,  # 输出调试数据
        config=AliPayConfig(timeout=15)  # 可选, 请求超时时间
    )
    return alipay


def to_decimal(param):
    if param is None:
        return 0
    else:
        return float(param)


def generate_tid(datetime_now, uid, amount):
    if datetime_now is None:
        tid_now = datetime.now().strftime("%Y%m%d%H%M%S")
    else:
        tid_now = datetime_now.strftime("%Y%m%d%H%M%S")
    return "time" + tid_now + "_uid" + str(uid) + "_amount" + str(amount)


trade = Blueprint('trade', __name__, template_folder='', static_folder='', url_prefix='/trade')


@trade.route('/f2fpay/callback', methods=['POST'])
def callback():
    alipay = alipay_ini()
    data = request.form.to_dict()
    signature = data.pop("sign")
    # verify
    success = alipay.verify(data, signature)
    if success and data["trade_status"] == "TRADE_SUCCESS":
        tid = data['out_trade_no']
        amount = to_decimal(data['total_amount'])
        sql_connect, sql_cursor = connect_dictCursor()
        sql_cursor.execute(f"update trade set trade_succeed='1' where tid='{tid}' ")
        sql_connect.commit()
        sql_cursor.execute(f"select uid from trade where tid='{tid}'")
        uid = sql_cursor.fetchone()['uid']
        sql_cursor.execute(f"select balance from users where uid='{uid}'")
        balance = to_decimal(sql_cursor.fetchone()['balance'])
        balance += amount
        sql_cursor.execute(f"update users set balance='{balance}' where uid='{uid}' ")
        sql_connect.commit()
        sql_cursor.close()
        sql_connect.close()
        return "success"
    else:
        return "fail"


@trade.route('/f2fpay/create', methods=['POST'])
def f2fpay():
    alipay = alipay_ini()
    dt_now = datetime.now()
    sql_now = dt_now.strftime("%Y-%m-%d %H:%M:%S")
    f = request.form
    tid = generate_tid(dt_now, f['uid'], f['amount'])
    t = {
        'uid': f['uid'],
        'tid': tid,  # <=64chars only alphabet & num & _
        'subject': f['subject'],  # no / =
        'amount': f['amount'],  # two decimal places eg:10.00
    }
    sql_connect, sql_cursor = connect_dictCursor()
    sql_cursor.execute(f"insert into trade (tid,uid,trade_subject,trade_sort,trade_amount,trade_time,trade_succeed)"
                       f"values ('{t['tid']}','{t['uid']}','{t['subject']}','income','{t['amount']}','{sql_now}','0') ")
    sql_connect.commit()
    sql_cursor.close()
    sql_connect.close()
    result = alipay.api_alipay_trade_precreate(
        subject=t['subject'],
        total_amount=t['amount'],
        out_trade_no=t['tid'],
        notify_url='http://sorapage.com/trade/f2fpay/callback'
    )
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=1
    )
    qr.add_data(result['qr_code'])
    qr_img = qr.make_image()
    buffer = BytesIO()
    qr_img.save(buffer, 'png')
    return base64.b64encode(buffer.getvalue())


@trade.route('/v2ray')
def v2ray_trade():
    purchase = request.args.get("purchase")
    uid = request.args.get("uid")
    if purchase is not None and uid is not None:
        sql_connect, sql_cursor = connect_dictCursor()
        sql_cursor.execute(f"select level_expire from v2ray_user where uid='{uid}' ")
        expire_time = sql_cursor.fetchone()['level_expire']
        sql_cursor.execute(f"select balance from users where uid='{uid}' ")
        balance = to_decimal(sql_cursor.fetchone()['balance'])
        if purchase == "monthly":
            expire_time += timedelta(days=30)
            trade_subject = "v2ray monthly"
            cost = 8.88
        elif purchase == "quarterly":
            expire_time += timedelta(days=90)
            trade_subject = "v2ray quarterly"
            cost = 23.33
        elif purchase == "semiannually":
            expire_time += timedelta(days=180)
            trade_subject = "v2ray semiannually"
            cost = 45.00
        balance = balance - cost
        if balance >= 0:
            expire_time = expire_time.strftime("%Y-%m-%d %H:%M:%S")
            dt_now = datetime.now()
            sql_now = dt_now.strftime("%Y-%m-%d %H:%M:%S")
            tid = generate_tid(dt_now, uid, cost)
            sql_cursor.execute(f"update v2ray_user set level_expire='{expire_time}' where uid='{uid}' ")
            sql_cursor.execute(f"update users set balance='{balance}' where uid='{uid}' ")
            sql_cursor.execute(
                f"insert into trade(tid,uid,trade_subject,trade_sort,trade_amount,trade_time,trade_succeed)"
                f"values('{tid}','{uid}','{trade_subject}','outcome','{cost}','{sql_now}','1')"
            )
            sql_connect.commit()
            sql_cursor.close()
            sql_connect.close()
            flash("购买成功", "success")
            return redirect('/v2ray')
        else:
            sql_cursor.close()
            sql_connect.close()
            flash("余额不足", "fail")
            return redirect('/v2ray')
