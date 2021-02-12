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
        value_reg = re.compile(r'value: \d+')
        num_in_value_reg = re.compile(r"\d+")
        traffic_str_tuple = value_reg.findall(stdout_str)
        if len(traffic_str_tuple) == 0:
            return "0"
        else:
            return num_in_value_reg.findall(traffic_str_tuple[0])[0]


def print_info(info):
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\t' + info)


def int_covert(param):
    if param is None:
        return 0
    else:
        return int(param)


def update_traffic():
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
        user_downlink_shell = f'''v2ctl api --server=127.0.0.1:20000 StatsService.GetStats 'name: "user>>>{user['email']}>>>traffic>>>downlink" reset: true' '''
        user_uplink_shell = f'''v2ctl api --server=127.0.0.1:20000 StatsService.GetStats 'name: "user>>>{user['email']}>>>traffic>>>uplink" reset: true' '''
        user_downlink = traffic_query(user_downlink_shell)
        user_uplink = traffic_query(user_uplink_shell)
        # SQL traffic query
        user_current_traffic_query = f"select downlink,uplink from v2ray_user where uid = '{user['uid']}' "
        sql_cursor.execute(user_current_traffic_query)
        user_current_traffic = sql_cursor.fetchone()
        # sum of result
        user_uplink_sum = int_covert(user_uplink) + int_covert(user_current_traffic['uplink'])
        user_downlink_sum = int_covert(user_downlink) + int_covert(user_current_traffic['downlink'])
        # update SQL user traffic
        user_traffic_update_query = f"update v2ray_user set uplink={user_uplink_sum},downlink={user_downlink_sum} where uid='{user['uid']}' "
        sql_cursor.execute(user_traffic_update_query)
        sql_connect.commit()

    def node_update(traffic_type, api_shell):
        added_traffic = traffic_query(api_shell)
        sql_cursor.execute(f"select {traffic_type} from v2ray_node where id='{node_id}' ")
        pre_traffic = sql_cursor.fetchone()[traffic_type]
        traffic_sum = int_covert(added_traffic) + int_covert(pre_traffic)
        sql_cursor.execute(f"update v2ray_node set {traffic_type}='{traffic_sum}' where id='{node_id}' ")
        sql_connect.commit()

    traffic_type_arr = ['outbound_uplink', 'outbound_downlink', 'inbound_uplink', 'inbound_downlink']
    api_shell_arr = [
        '''v2ctl api --server=127.0.0.1:20000 StatsService.GetStats 'name: "outbound>>>direct>>>traffic>>>uplink" reset: true' ''',
        '''v2ctl api --server=127.0.0.1:20000 StatsService.GetStats 'name: "outbound>>>direct>>>traffic>>>downlink" reset: true' ''',
        '''v2ctl api --server=127.0.0.1:20000 StatsService.GetStats 'name: "inbound>>>tcp>>>traffic>>>uplink" reset: true' ''',
        '''v2ctl api --server=127.0.0.1:20000 StatsService.GetStats 'name: "inbound>>>tcp>>>traffic>>>downlink" reset: true' '''
    ]
    for i in range(4):
        node_update(traffic_type_arr[i], api_shell_arr[i])
    sql_cursor.close()
    sql_connect.close()
    print_info('traffic updated')


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
scheduler.add_job(update_traffic, 'interval', seconds=10)
scheduler.add_job(update_config_json, 'interval', seconds=10)
scheduler.start()
