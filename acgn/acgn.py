from flask import Blueprint, render_template, request, redirect, jsonify
import json
from sql import connect_dictCursor

acgn = Blueprint('acgn', __name__, template_folder='acgn_html', static_folder='acgn_static', url_prefix='/acgn')


@acgn.route('/galgame')
def galgame():
    return render_template('galgame.html')


@acgn.route('/galgame/ajax/<ajax_type>', methods=['GET', 'POST'])
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
        sql_cursor.close()
        sql_connect.close()
        return jsonify(sql_cursor.fetchall())

    if ajax_type == 'add':
        form = request.form
        date = form['gal_year'] + '-' + form['gal_month'] + '-' + form['gal_day']
        sql_cursor.execute("insert into galgame(name,imgLen,overall,plot,characterRank,music,CG,date)" +
                           f"values('{form['gal_name']}',{form['gal_imgLen']},'{form['gal_overall']}','{form['gal_plot']}',"
                           f"'{form['gal_characterRank']}','{form['gal_music']}','{form['gal_CG']}','{date}')")
        sql_connect.commit()
        sql_cursor.close()
        sql_connect.close()
        return redirect('/acgn/galgame')

    if ajax_type == 'add_detail':
        detail_list = request.json
        for i in range(0, len(detail_list)):
            detail = detail_list[i]
            content_json = json.dumps(detail['content'])
            sql_cursor.execute(
                f"insert into galgame_detail(name,target,content) values('{detail['name']}','{detail['target']}','{content_json}')")
            sql_connect.commit()
            sql_cursor.close()
            sql_connect.close()
        return 'accepted'
