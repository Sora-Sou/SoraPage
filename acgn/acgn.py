from flask import Blueprint, render_template, request, jsonify
from sql import connect_dictCursor
from datetime import datetime

acgn = Blueprint('acgn', __name__, template_folder='acgn_html', static_folder='acgn_static', url_prefix='/acgn')


@acgn.route('/galgame')
def galgame():
    return render_template('galgame.html')


@acgn.route('/galgame/ajax/<ajax_type>')
def galgame_ajax(ajax_type):
    sql_connect, sql_cursor = connect_dictCursor()
    if ajax_type == 'card':
        offset = request.args.get('offset')
        sql_cursor.execute("select * from galgame limit 4 offset " + offset)
        fetch = sql_cursor.fetchmany(4)
        for i in range(0, len(fetch)):
            fetch[i]['date'] = fetch[i]['date'].strftime("%Y-%m-%d")
        sql_cursor.close()
        sql_connect.close()
        return jsonify(fetch)
    if ajax_type == 'detail':
        sql_cursor.execute("select * from galgame_detail")
        return jsonify(sql_cursor.fetchall())
