from flask import Blueprint, make_response, redirect, request, session, current_app, render_template, url_for
import pymysql
from config import SQL


def load_comment():
    sql_connect, sql_cursor = SQL().connect_Dict()
    sql_cursor.execute(f'''SELECT * FROM comment WHERE url='{request.path}' ''')
    sql_fetch = sql_cursor.fetchall()
    comment_root = []
    comment_reply = []
    for item in sql_fetch:
        if item['replyTo'] is None:
            comment_root.append(item)
        else:
            comment_reply.append(item)
    comment_root.sort(key=lambda x: x['time'])
    comment_reply.sort(key=lambda x: (x['root'], x['time']))
    return comment_root, comment_reply


comment = Blueprint('comment', __name__)


@comment.route('/comment', methods=['POST'])
def comments():
    return request.form['comment']
