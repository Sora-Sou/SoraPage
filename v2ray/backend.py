# version 1.1
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
        return "0"
    else:
        pattern = re.compile(r'\d+')
        traffic_str_tuple = pattern.findall(stdout_str)
        if len(traffic_str_tuple) == 0:
            return "0"
        else:
            return traffic_str_tuple[0]


def print_info(info):
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\t' + info)


def update_traffic():
    sql_connect, sql_cursor = connect_dictCursor()
    # user traffic query
    node_level_query = f"select node_level from v2ray_node where id = '{node_id}'"
    sql_cursor.execute(node_level_query)
    node_level = sql_cursor.fetchone()['node_level']
    user_list_query = f"select v.id, u.email from v2ray_user v inner join users u on v.id=u.id where v.user_level >= '{node_level}' "
    sql_cursor.execute(user_list_query)
    user_list = sql_cursor.fetchall()
    for user in user_list:
        # shell traffic query
        user_downlink_shell = f'''v2ctl api --server=127.0.0.1:20000 StatsService.GetStats 'name: "user>>>{user['email']}>>>traffic>>>downlink" reset: true' '''
        user_uplink_shell = f'''v2ctl api --server=127.0.0.1:20000 StatsService.GetStats 'name: "user>>>{user['email']}>>>traffic>>>uplink" reset: true' '''
        user_downlink = traffic_query(user_downlink_shell)
        user_uplink = traffic_query(user_uplink_shell)
        # sql traffic query
        user_current_traffic_query = f"select downlink,uplink from v2ray_user where id = '{user['id']}' "
        sql_cursor.execute(user_current_traffic_query)
        user_current_traffic = sql_cursor.fetchone()
        # sum of result
        user_uplink_sum = int(user_uplink) + int(user_current_traffic['uplink'])
        user_downlink_sum = int(user_downlink) + int(user_current_traffic['downlink'])
        # update sql user traffic
        user_traffic_update_query = f"update v2ray_user set uplink={user_uplink_sum},downlink={user_downlink_sum} where id='{user['id']}' "
        sql_cursor.execute(user_traffic_update_query)
        sql_connect.commit()
    # node outbound uplink query
    node_outbound_uplink_shell = '''v2ctl api --server=127.0.0.1:20000 StatsService.GetStats 'name: "outbound>>>direct>>>traffic>>>uplink" reset: false' '''
    node_outbound_uplink = traffic_query(node_outbound_uplink_shell)
    sql_cursor.execute(f" update v2ray_node set outbound_uplink='{node_outbound_uplink}' where id='{node_id}' ")
    sql_connect.commit()
    # node outbound downlink query
    node_outbound_downlink_shell = '''v2ctl api --server=127.0.0.1:20000 StatsService.GetStats 'name: "outbound>>>direct>>>traffic>>>downlink" reset: false' '''
    node_outbound_downlink = traffic_query(node_outbound_downlink_shell)
    sql_cursor.execute(f" update v2ray_node set outbound_downlink='{node_outbound_downlink}' where id='{node_id}' ")
    sql_connect.commit()
    # node inbound uplink query
    node_inbound_uplink_shell = '''v2ctl api --server=127.0.0.1:20000 StatsService.GetStats 'name: "inbound>>>tcp>>>traffic>>>uplink" reset: false' '''
    node_inbound_uplink = traffic_query(node_inbound_uplink_shell)
    sql_cursor.execute(f" update v2ray_node set inbound_uplink='{node_inbound_uplink}' where id='{node_id}' ")
    sql_connect.commit()
    # node inbound downlink query
    node_inbound_downlink_shell = '''v2ctl api --server=127.0.0.1:20000 StatsService.GetStats 'name: "inbound>>>tcp>>>traffic>>>downlink" reset: false' '''
    node_inbound_downlink = traffic_query(node_inbound_downlink_shell)
    sql_cursor.execute(f" update v2ray_node set inbound_downlink='{node_inbound_downlink}' where id='{node_id}' ")
    sql_connect.commit()
    sql_cursor.close()
    sql_connect.close()
    print_info('traffic updated')


def update_config_json():
    config_json = urlopen(f"http://sorapage.com/v2ray/node/config/{node_id}").read().decode('utf-8')
    v2ray_config_json_path = "/usr/local/etc/v2ray/config.json"
    with open(v2ray_config_json_path, 'w') as file_obj:
        file_obj.write(config_json)
    print_info('config updated')
    shell("systemctl stop v2ray")
    shell("systemctl start v2ray")
    print_info("v2ray started")


node_id = input('input the node id:')
update_config_json()

scheduler = BlockingScheduler()
scheduler.add_job(update_traffic, 'interval', seconds=10, jitter=5)
scheduler.add_job(update_config_json, 'cron', hour=0, minute=5, second=0, jitter=120)
scheduler.start()
