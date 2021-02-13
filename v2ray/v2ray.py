from flask import Blueprint, redirect, session, render_template, request, send_file, jsonify, current_app
from urllib.request import urlopen
from datetime import datetime, timedelta
import json
import os
import base64

from sql import connect_dictCursor
from config import V2RAY_CONFIG, SQL

v2ray = Blueprint('v2ray', __name__, template_folder='', static_folder='', url_prefix='/v2ray')


@v2ray.route('/')
def interface():
    def traffic_unit_convert(t_sum):
        if t_sum is None:
            return "0"
        else:
            if t_sum < 1e3:
                return str(t_sum) + "B"
            elif 1e3 <= t_sum < 1e6:
                return str(round(t_sum / 1e3)) + "KB"
            elif 1e6 <= t_sum < 1e9:
                return str(round(t_sum / 1e6)) + "MB"
            elif t_sum >= 1e9:
                return str(round(t_sum / 1e9, 2)) + "GB"

    if session.get('uid') is None:
        return redirect('/login?success=v2ray')
    else:
        sql_connect, sql_cursor = connect_dictCursor()
        uid = session['uid']
        sql_cursor.execute(f"select * from v2ray_user where uid ='{uid}'")
        fetch = sql_cursor.fetchone()
        # first login
        trail_expire = (datetime.now() + timedelta(days=V2RAY_CONFIG['trail_duration'])).strftime('%Y-%m-%d')
        if fetch is None:
            uuid = urlopen("https://www.uuidgenerator.net/api/version4").read().decode()
            sql_cursor.execute(
                f'''insert into v2ray_user values('{uid}','{uuid}','0','1','{trail_expire}','0','0')'''
            )
            sql_connect.commit()
            user_info = {
                'uid': uid,
                'uuid': uuid,
                'name': session['user_name'],
                'email': session['user_email'],
                'balance': 0,
                'user_level': 1,
                'level_expire': trail_expire,
                'up': 0,
                'down': 0,
                'today_up': 0,
                'today_down': 0
            }
        else:
            sql_cursor.execute(f"select balance from users where uid='{uid}' ")
            balance = sql_cursor.fetchone()['balance']
            user_info = {
                'uid': uid,
                'uuid': fetch['uuid'],
                'name': session['user_name'],
                'email': session['user_email'],
                'balance': balance,
                'user_level': fetch['user_level'],
                'level_expire': fetch['level_expire'],
                'up': traffic_unit_convert(fetch['up']),
                'down': traffic_unit_convert(fetch['down']),
                'today_up': traffic_unit_convert(fetch['today_up']),
                'today_down': traffic_unit_convert(fetch['today_down'])
            }
        sql_cursor.execute('select * from v2ray_node order by order_ asc')
        node_info = sql_cursor.fetchall()
        node_traffic_unit_convert = ['in_up', 'in_down', 'out_up', 'out_down',
                                     'today_in_up', 'today_in_down', 'today_out_up', 'today_out_down']
        for node in node_info:
            for nt in node_traffic_unit_convert:
                node[nt] = traffic_unit_convert(node[nt])
        sql_cursor.execute('select * from v2ray_user inner join users on v2ray_user.uid = users.uid')
        all_user_list = sql_cursor.fetchall()
        user_traffic_unit_convert = ['up', 'down', 'today_up', 'today_down']
        for user in all_user_list:
            for ut in user_traffic_unit_convert:
                user[ut] = traffic_unit_convert(user[ut])
        sql_cursor.close()
        sql_connect.close()
    return render_template('interface.html', user_info=user_info, node_info=node_info, all_user_list=all_user_list)


@v2ray.route('/subscribe/<uuid>')
def subscribe(uuid):
    sql_connect, sql_cursor = connect_dictCursor()
    sql_cursor.execute(f"select user_level from v2ray_user where uuid='{uuid}' ")
    user_level = sql_cursor.fetchone()['user_level']
    sql_cursor.execute(f"select * from v2ray_node where node_level<='{user_level}' order by order_ asc")
    node_list = sql_cursor.fetchall()
    sql_cursor.close()
    sql_connect.close()
    vmess_collection = ""
    subscribe_content = ""

    def base64encode(string):
        return base64.b64encode(string.encode('utf-8')).decode('utf-8')

    for i in range(len(node_list)):
        node = node_list[i]
        if node['relay_address'] is None:
            address = node['address']
            port = node['port']
        else:
            address = node['relay_address']
            port = node['relay_port']
        node_link = {
            "v": "2",
            "ps": node['node_name'],
            "add": address,
            "port": port,
            "id": uuid,
            "aid": "64",
            "net": "tcp",
            "type": "none",
            "host": "www.baidu.com",
            # "path": "/",
            # "tls": "tls"
        }
        # node_json ---> base64str ---> vmess://base64str
        # vmess://base64str |
        # vmess://base64str | ---> base64str
        # vmess://base64str |
        node_json = json.dumps(node_link)
        base64str = base64encode(node_json)
        vmess_str = "vmess://" + base64str + '\n'
        vmess_collection += vmess_str
        subscribe_content = base64encode(vmess_collection)
    return subscribe_content


@v2ray.route('/node/add', methods=['POST'])
def add_node():
    form = request.form
    sql_connect, sql_cursor = connect_dictCursor()
    sql_cursor.execute('select order_ from v2ray_node order by order_ desc')
    fetch = sql_cursor.fetchone()
    if fetch is None:
        order = 1
    else:
        order = int(fetch['order_']) + 1
    if form.get('relay_address') is None:
        sql_cursor.execute(
            f"insert into v2ray_node (node_name, address, port, order_, node_level)"
            f"values ('{form['node_name']}','{form['node_address']}','{form['node_port']}','{order}','{form['node_level']}')"
        )
    else:
        sql_cursor.execute(
            f"insert into v2ray_node (node_name, address, port, relay_address, relay_port, order_, node_level) "
            f"values ('{form['node_name']}','{form['node_address']}','{form['node_port']}','{form['relay_address']}','{form['relay_port']}','{order}','{form['node_level']}')"
        )
    sql_connect.commit()
    sql_cursor.close()
    sql_connect.close()
    return redirect('/v2ray')


@v2ray.route('/node/delete', methods=['GET'])
def delete_node():
    delete_id = request.args.get('id')
    if delete_id is not None:
        sql_connect, sql_cursor = connect_dictCursor()
        sql_cursor.execute(f"delete from v2ray_node where id = '{delete_id}'")
        sql_connect.commit()
        sql_cursor.close()
        sql_connect.close()
    return redirect('/v2ray')


@v2ray.route('/node/modify', methods=['POST'])
def modify_node():
    f = request.form
    sql_connect, sql_cursor = connect_dictCursor()
    if f.get('relay_address_m') is None:
        sql_cursor.execute(
            f"update v2ray_node set node_name='{f['node_name_m']}', address='{f['node_address_m']}', "
            f"port='{f['node_port_m']}', node_level='{f['node_level_m']}',"
            f"relay_address=null, relay_port=null "
            f"where id='{f['node_id']}' "
        )
    else:
        sql_cursor.execute(
            f"update v2ray_node set node_name='{f['node_name_m']}', address='{f['node_address_m']}', "
            f"port='{f['node_port_m']}', node_level='{f['node_level_m']}',"
            f"relay_address='{f['relay_address_m']}', relay_port='{f['relay_port_m']}'"
            f"where id='{f['node_id']}' "
        )
    sql_connect.commit()
    sql_cursor.close()
    sql_connect.close()
    return redirect('/v2ray')


@v2ray.route('/node/reorder', methods=['GET'])
def reorder_node():
    node_id = request.args.get('id')
    node_order = int(request.args.get('order'))
    action = request.args.get('action')
    sql_connect, sql_cursor = connect_dictCursor()
    if action == "up":
        sql_cursor.execute(f"update v2ray_node set order_='{node_order}' where order_ ='{node_order - 1}' ")
        sql_connect.commit()
        sql_cursor.execute(f"update v2ray_node set order_='{node_order - 1}' where id ='{node_id}' ")
        sql_connect.commit()
    elif action == 'down':
        sql_cursor.execute(f"update v2ray_node set order_='{node_order}' where order_ ='{node_order + 1}' ")
        sql_connect.commit()
        sql_cursor.execute(f"update v2ray_node set order_='{node_order + 1}' where id ='{node_id}' ")
        sql_connect.commit()
    sql_cursor.close()
    sql_connect.close()
    return redirect('/v2ray')


@v2ray.route('/node/config/<node_id>')
def node_api(node_id):
    sql_connect, sql_cursor = connect_dictCursor()
    sql_cursor.execute(f"select address from v2ray_node where id ='{node_id}'")
    node_address = sql_cursor.fetchone()['address']
    sql_cursor.execute(f"select * from v2ray_node where address='{node_address}'")
    node_list = sql_cursor.fetchall()
    inbounds = []
    outbounds = []
    rules = []
    for i in range(len(node_list)):
        node = node_list[i]
        inbound_tag = "in" + str(node['port'])
        outbound_tag = "out" + str(node['port'])
        sql_cursor.execute(
            f"select u.email,v.uuid from users u inner join v2ray_user v on u.uid=v.uid where v.user_level>='{node['node_level']}' "
        )
        user_list = sql_cursor.fetchall()
        clients = []
        for user in user_list:
            clients.append({
                'email': user['email'],
                'id': user['uuid'],
                'level': 0,
                'alterId': 64
            })
        inbound_e = {
            "tag": inbound_tag,
            "port": node['port'],
            "protocol": "vmess",
            "settings": {
                "clients": clients
            }
        }
        inbounds.append(inbound_e)
        outbound_e = {
            "tag": outbound_tag,
            "protocol": "freedom",
            "settings": {}
        }
        outbounds.append(outbound_e)
        rule_e = {
            "inboundTag": [inbound_tag],
            "outboundTag": outbound_tag,
            "type": "field"
        }
        rules.append(rule_e)
    inbounds.append({
        "listen": "127.0.0.1",
        "port": 20000,
        "protocol": "dokodemo-door",
        "settings": {
            "address": "127.0.0.1"
        },
        "tag": "api"
    })
    rules.append({
        "inboundTag": ["api"],
        "outboundTag": "api",
        "type": "field"
    })
    # other config settings
    config_json = {
        "log": {
            "loglevel": "warning",
            "access": "/var/log/v2ray/access.log",
            "error": "/var/log/v2ray/error.log"
        },
        "stats": {},
        "api": {
            "tag": "api",
            "services": [
                "StatsService"
            ]
        },
        "policy": {
            "levels": {
                "0": {
                    "statsUserUplink": True,
                    "statsUserDownlink": True
                }
            },
            "system": {
                "statsInboundUplink": True,
                "statsInboundDownlink": True,
                "statsOutboundUplink": True,
                "statsOutboundDownlink": True
            }
        },
        "inbounds": inbounds,
        "outbounds": outbounds,
        "routing": {
            "rules": rules,
            "domainStrategy": "AsIs"
        }
    }
    return jsonify(config_json)


@v2ray.route('/backend/<file_name>')
def send_backend_file(file_name):
    if file_name == "python":
        file_content = ""
        with open(os.path.join(current_app.root_path, 'v2ray/backend_template.py'), 'r') as backend:
            for line in backend:
                if "sql_connect = pymysql.connect()" in line:
                    line = line.replace("sql_connect = pymysql.connect()",
                                        f"sql_connect = pymysql.connect(host='{SQL['host']}', port={SQL['port']}, database='{SQL['database']}', user='{SQL['user']}', password='{SQL['password']}') ")
                file_content += line
        with open(os.path.join(current_app.root_path, 'v2ray/backend.py'), 'w') as backend:
            backend.write(file_content)
        return send_file(os.path.join(current_app.root_path, 'v2ray/backend.py'))
    elif file_name == "requirements":
        return send_file(os.path.join(current_app.root_path, 'v2ray/requirements.txt'))
