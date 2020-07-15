from flask import Blueprint, request, session
import json
from urllib.parse import urlparse
from config import SQL
from datetime import datetime


def format_time(datetime_obj):
    timedelta_obj = datetime.now() - datetime_obj
    if timedelta_obj.days == 0:
        time_str = str(timedelta_obj)
        time_str_list = time_str.split(':')
        time_str_list[2] = time_str_list[2][0:2]
        time_list = []
        for value in time_str_list:
            time_list.append(int(value))

        if time_list[0] == time_list[1] == time_list[2] == 0:
            return '刚刚'
        elif time_list[0] == time_list[1] == 0:
            return str(time_list[2]) + '秒前'
        elif time_list[0] == 0:
            return str(time_list[1]) + '分钟前'
        else:
            return str(time_list[0]) + '小时前'
    elif timedelta_obj.days <= 7:
        return str(timedelta_obj)[0:1] + '天前'
    else:
        return datetime_obj.strftime("%Y-%m-%d %H:%M:%S")


def load(url):
    sql_connect, sql_cursor = SQL().connect_Dict()
    sql_cursor.execute(f"SELECT * FROM comment WHERE url='{url}'")
    sql_fetch = sql_cursor.fetchall()
    comment_parent = []
    comment_child = []
    for item in sql_fetch:
        if item['replyTo'] is None:
            comment_parent.append(item)
        else:
            comment_child.append(item)
    comment_parent.sort(key=lambda x: x['time'])
    comment_child.sort(key=lambda x: (x['parent'], x['time']))
    for i in range(len(comment_parent)):
        comment_parent[i]['time'] = format_time(comment_parent[i]['time'])
    for i in range(len(comment_child)):
        comment_child[i]['time'] = format_time(comment_child[i]['time'])
    comment_obj = {
        'parent': comment_parent,
        'child': comment_child
    }
    try:
        comment_obj['login_user'] = {'name': session['name'], 'email': session['email']}
    except KeyError:
        pass
    comment_json = json.dumps(comment_obj)
    sql_cursor.close()
    sql_connect.close()
    return comment_json


comment = Blueprint('comment', __name__)


@comment.route('/comment', methods=['GET', 'POST'])
def comment_ajax():
    url = urlparse(request.referrer).path
    if request.method == 'GET':
        return load(url)
    elif request.method == 'POST':
        sql_connect, sql_cursor = SQL().connect_Dict()
        form = {}
        for value, key in request.form.items():
            if key == '':
                form[value] = 'NULL'
            else:
                form[value] = key
        if request.form['parent'] == '':
            sql_cursor.execute(f"SELECT * FROM comment WHERE url='{url}' AND parent IS NULL ")
            sequence = f"{len(sql_cursor.fetchall()) + 1}"
        else:
            sql_cursor.execute(f"SELECT sequence FROM comment WHERE id={form['parent']}")
            sequence = f"{sql_cursor.fetchone()['sequence']}-"
            sql_cursor.execute(f"SELECT * FROM comment WHERE url='{url}' AND parent={form['parent']}")
            sequence += str(len(sql_cursor.fetchall()) + 1)
        sql_cursor.execute(
            f"INSERT INTO comment (url,name,email,comment,time,parent,replyTo,sequence,replyToSeq) VALUES ('{url}','{form['name']}','{form['email']}','{form['comment']}','{form['time']}',{form['parent']},{form['replyTo']},'{sequence}','{form['replyToSeq']}')")
        sql_connect.commit()
        sql_cursor.close()
        sql_connect.close()
        return load(url)
