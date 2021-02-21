from sql import connect_dictCursor
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler


def print_info(info):
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\t' + info)


def v2ray_database_update():
    sql_connect, sql_cursor = connect_dictCursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_level_update = f"update v2ray_user set user_level = '0' where level_expire<='{now}' "
    sql_cursor.execute(user_level_update)
    print_info("user level updated")
    sql_connect.commit()
    user_today_traffic_update = f"update v2ray_user set today_up='0',today_down='0'"
    sql_cursor.execute(user_today_traffic_update)
    sql_connect.commit()
    print_info("user today's traffic updated")
    node_today_traffic_update = f"update v2ray_node set today_in_up='0',today_in_down='0',today_out_up='0',today_out_down='0'"
    sql_cursor.execute(node_today_traffic_update)
    sql_connect.commit()
    print_info("node today's traffic updated")
    sql_cursor.close()
    sql_connect.close()


v2ray_database_update()

scheduler = BlockingScheduler()
scheduler.add_job(v2ray_database_update, 'cron', hour=0, minute=0, second=0)
scheduler.start()
