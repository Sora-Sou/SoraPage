from flask import Blueprint, redirect, session, render_template, request, send_file, url_for, current_app
from urllib.request import urlopen
from datetime import datetime, timedelta
import json
import os
import base64

from sql import connect_dictCursor
from config import v2ray_config

v2ray = Blueprint('v2ray', __name__, template_folder='', static_folder='', url_prefix='/v2ray')


@v2ray.route('/')
def interface():
    if session.get('id') is None:
        return redirect('/login?success=v2ray')
    else:
        sql_connect, sql_cursor = connect_dictCursor()
        sql_id = session['id']
        sql_cursor.execute(f'select * from v2ray_user where id ="{sql_id}"')
        fetch = sql_cursor.fetchone()
        # first login
        trail_expire = (datetime.now() + timedelta(days=v2ray_config['trail_duration'])).strftime('%Y-%m-%d')
        if fetch is None:
            v2ray_id = urlopen("https://www.uuidgenerator.net/api/version4").read().decode()
            sql_cursor.execute(
                f'''insert into v2ray_user values('{sql_id}','{v2ray_id}','0','1','{trail_expire}','0','0')'''
            )
            sql_connect.commit()
            user_info = {
                'id': sql_id,
                'uid': v2ray_id,
                'name': session['name'],
                'email': session['email'],
                'balance': 0,
                'user_level': 1,
                'level_expire': trail_expire,
                'uplink': 0,
                'downlink': 0
            }
        else:
            user_info = {
                'id': sql_id,
                'uid': fetch['uid'],
                'name': session['name'],
                'email': session['email'],
                'balance': fetch['balance'],
                'user_level': fetch['user_level'],
                'level_expire': fetch['level_expire'],
                'uplink': fetch['uplink'],
                'downlink': fetch['downlink']
            }
        sql_cursor.execute('select * from v2ray_node order by order_ asc')
        node_info = sql_cursor.fetchall()
        sql_cursor.execute('select * from v2ray_user inner join users on v2ray_user.id = users.id')
        all_user_list = sql_cursor.fetchall()
    return render_template('interface.html', user_info=user_info, node_info=node_info, all_user_list=all_user_list)


@v2ray.route('/subscribe/<uid>')
def subscribe(uid):
    sql_connect, sql_cursor = connect_dictCursor()
    sql_cursor.execute(f"select user_level from v2ray_user where uid='{uid}' ")
    user_level = sql_cursor.fetchone()['user_level']
    sql_cursor.execute(f"select * from v2ray_node where node_level<='{user_level}' order by order_ asc")
    node_list = sql_cursor.fetchall()
    vmess_collection = ""
    subscribe_content = ""

    def base64encode(string):
        bytes_str = base64.b64encode(string.encode('utf-8'))
        return str(bytes_str)[2:-1]

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
            "id": uid,
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
    sql_cursor.execute(f"select * from v2ray_node where id = {node_id}")
    sql_connect.commit()
    node_info = sql_cursor.fetchone()
    sql_cursor.execute(
        f"select * from v2ray_user inner join users on v2ray_user.id = users.id "
        f"where user_level >= '{node_info['node_level']}' "
    )
    sql_connect.commit()
    user_info = sql_cursor.fetchall()
    with open(os.path.join(current_app.root_path, 'v2ray/template.json')) as template_json_file:
        config_json = json.load(template_json_file)
        config_json['inbounds'][0]['port'] = node_info['port']
        client_array = config_json['inbounds'][0]['settings']['clients']
        for user in user_info:
            client_array.append({
                "email": user['email'],
                "id": user['uid'],
                "level": 0,
                "alterId": 64
            })
        with open(os.path.join(current_app.root_path, 'v2ray/config.json'), 'w') as config_json_file:
            json.dump(config_json, config_json_file)
    return send_file(os.path.join(current_app.root_path, 'v2ray/config.json'))


@v2ray.route('/backend/<file_name>')
def send_backend_file(file_name):
    if file_name == "python":
        return send_file(os.path.join(current_app.root_path, 'v2ray/v2ray_backend.py'))
    elif file_name == "requirements":
        return send_file(os.path.join(current_app.root_path, 'v2ray/requirements.txt'))
