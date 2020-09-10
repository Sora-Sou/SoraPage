from flask import Blueprint, render_template, request, jsonify, redirect
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
        date = form['year'] + '-' + form['month'] + '-' + form['day']
        sql_cursor.execute("insert into galgame(name,imgLen,overall,plot,characterRank,music,CG,date)" +
                           f"values('{form['name']}',{form['imgLen']},'{form['overall']}','{form['plot']}','{form['characterRank']}','{form['music']}','{form['CG']}','{date}')")
        sql_connect.commit()
        detail_list = ['overall', 'plot', 'characterRank', 'music', 'CG']
        for element in detail_list:
            detail_dict = {}
            selector = 'detail_' + element
            if form[selector] != '':
                detail_dict['name'] = form['name']
                detail_dict['target'] = element
                detail_dict['content'] = {}

        return redirect('/acgn/galgame')
