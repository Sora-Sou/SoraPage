from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess
import re
import pymysql
from urllib.request import urlopen
from datetime import datetime


def connect_dictCursor():
    sql_connect = pymysql.connect()
    sql_cursor = sql_connect.cursor(cursor=pymysql.cursors.DictCursor)
    return sql_connect, sql_cursor


def shell(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.communicate()
    # return data type = bytes tuple
    # p.communicate[0]=stdout   !bytes datatype
    # p.communicate[1]=stderr   !bytes datatype


def traffic_query(cmd):
    std_bytes_tuple = shell(cmd)
    stdout_str = std_bytes_tuple[0].decode('utf-8')
    if len(stdout_str) == 0:
        return 0
    else:
        value_reg = re.compile(r'value: \d+')
        num_in_value_reg = re.compile(r"\d+")
        traffic_str_tuple = value_reg.findall(stdout_str)
        if len(traffic_str_tuple) == 0:
            return 0
        else:
            return num_in_value_reg.findall(traffic_str_tuple[0])[0]


def print_info(info):
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\t' + info)


def int_covert(param):
    if param is None:
        return 0
    else:
        return int(param)


def update_user_traffic():
    sql_connect, sql_cursor = connect_dictCursor()
    # user traffic query
    node_level_query = f"select node_level from v2ray_node where id = '{node_id}'"
    sql_cursor.execute(node_level_query)
    node_level = sql_cursor.fetchone()['node_level']
    user_list_query = f"select v.uid, u.email from v2ray_user v inner join users u on v.uid=u.uid where v.user_level >= '{node_level}' "
    sql_cursor.execute(user_list_query)
    user_list = sql_cursor.fetchall()
    for user in user_list:
        # shell traffic query
        down_shell = f'''v2ctl api --server=127.0.0.1:20000 StatsService.GetStats 'name: "user>>>{user['email']}>>>traffic>>>downlink" reset: true' '''
        up_shell = f'''v2ctl api --server=127.0.0.1:20000 StatsService.GetStats 'name: "user>>>{user['email']}>>>traffic>>>uplink" reset: true' '''
        shell_down_traffic = traffic_query(down_shell)
        shell_up_traffic = traffic_query(up_shell)
        # SQL traffic query
        sql_traffic_query = f"select down,up,today_down,today_up from v2ray_user where uid = '{user['uid']}' "
        sql_cursor.execute(sql_traffic_query)
        sql_traffic = sql_cursor.fetchone()
        # sum of result
        up_sum = int_covert(shell_up_traffic) + int_covert(sql_traffic['up'])
        down_sum = int_covert(shell_down_traffic) + int_covert(sql_traffic['down'])
        today_up_sum = int_covert(shell_up_traffic) + int_covert(sql_traffic['today_up'])
        today_down_sum = int_covert(shell_down_traffic) + int_covert(sql_traffic['today_down'])
        # update SQL user traffic
        update_query = f"update v2ray_user set up={up_sum},down={down_sum}," \
                       f"today_up={today_up_sum},today_down={today_down_sum} where uid='{user['uid']}' "
        sql_cursor.execute(update_query)
        sql_connect.commit()
    sql_cursor.close()
    sql_connect.close()
    print_info('user traffic updated')


def update_node_traffic():
    sql_connect, sql_cursor = connect_dictCursor()
    sql_cursor.execute(f"select address from v2ray_node where id='{node_id}' ")
    address = sql_cursor.fetchone()['address']
    sql_cursor.execute(f"select * from v2ray_node where address='{address}' ")
    node_list = sql_cursor.fetchall()
    for i in range(len(node_list)):
        node = node_list[i]
        inbound_tag = "in" + str(node['port'])
        outbound_tag = "out" + str(node['port'])
        shell_list = [
            f'''v2ctl api --server=127.0.0.1:20000 StatsService.GetStats 'name: "outbound>>>{outbound_tag}>>>traffic>>>uplink" reset: true' ''',
            f'''v2ctl api --server=127.0.0.1:20000 StatsService.GetStats 'name: "outbound>>>{outbound_tag}>>>traffic>>>downlink" reset: true' ''',
            f'''v2ctl api --server=127.0.0.1:20000 StatsService.GetStats 'name: "inbound>>>{inbound_tag}>>>traffic>>>uplink" reset: true' ''',
            f'''v2ctl api --server=127.0.0.1:20000 StatsService.GetStats 'name: "inbound>>>{inbound_tag}>>>traffic>>>downlink" reset: true' '''
        ]
        shell_traffic = {
            # property data type is int
            "out_up": int_covert(traffic_query(shell_list[0])),
            "out_down": int_covert(traffic_query(shell_list[1])),
            "in_up": int_covert(traffic_query(shell_list[2])),
            "in_down": int_covert(traffic_query(shell_list[3])),
        }
        sql_traffic = {
            # property data type is int
            "out_up": int_covert(node['out_up']),
            "out_down": int_covert(node['out_down']),
            "in_up": int_covert(node['in_up']),
            "in_down": int_covert(node['in_down']),
            "today_out_up": int_covert(node['today_out_up']),
            "today_out_down": int_covert(node['today_out_down']),
            "today_in_up": int_covert(node['today_in_up']),
            "today_in_down": int_covert(node['today_in_down']),
        }
        update_traffic = {
            "out_up": shell_traffic['out_up'] + sql_traffic['out_up'],
            "out_down": shell_traffic['out_down'] + sql_traffic['out_down'],
            "in_up": shell_traffic['in_up'] + sql_traffic['in_up'],
            "in_down": shell_traffic['in_down'] + sql_traffic['in_down'],
            "today_out_up": shell_traffic['out_up'] + sql_traffic['today_out_up'],
            "today_out_down": shell_traffic['out_down'] + sql_traffic['today_out_down'],
            "today_in_up": shell_traffic['in_up'] + sql_traffic['today_in_up'],
            "today_in_down": shell_traffic['in_down'] + sql_traffic['today_in_down'],
        }
        sql_cursor.execute(
            f"update v2ray_node set out_up='{update_traffic['out_up']}',out_down='{update_traffic['out_down']}',"
            f"in_up='{update_traffic['in_up']}',in_down='{update_traffic['in_down']}',"
            f"today_out_up='{update_traffic['today_out_up']}',today_out_down='{update_traffic['today_out_down']}',"
            f"today_in_up='{update_traffic['today_in_up']}',today_in_down='{update_traffic['today_in_down']}'"
            f"where id='{node['id']}'"
        )
        sql_connect.commit()
    sql_cursor.close()
    sql_connect.close()
    print_info('node traffic updated')


last_update_user_num = 0


def update_config_json():
    sql_connect, sql_cursor = connect_dictCursor()
    sql_cursor.execute(f"select node_level from v2ray_node where id='{node_id}' ")
    node_level = sql_cursor.fetchone()['node_level']
    sql_cursor.execute(f"select uid from v2ray_user where user_level>='{node_level}' ")
    this_update_user_num = len(sql_cursor.fetchall())
    global last_update_user_num
    if this_update_user_num != last_update_user_num:
        config_json = urlopen(f"http://sorapage.com/v2ray/node/config/{node_id}").read().decode('utf-8')
        v2ray_config_json_path = "/usr/local/etc/v2ray/config.json"
        with open(v2ray_config_json_path, 'w') as file_obj:
            file_obj.write(config_json)
        print_info('config updated')
        shell("systemctl stop v2ray")
        shell("systemctl start v2ray")
        print_info("v2ray started")
    last_update_user_num = this_update_user_num
    sql_cursor.close()
    sql_connect.close()


node_id = input('input the node id:')

scheduler = BlockingScheduler()
scheduler.add_job(update_user_traffic, 'interval', seconds=10)
scheduler.add_job(update_node_traffic, 'interval', seconds=10)
scheduler.add_job(update_config_json, 'interval', seconds=10)
scheduler.start()
