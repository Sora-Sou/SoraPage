from flask import Blueprint, render_template, request, redirect, jsonify
from datetime import datetime, timedelta
from sql import connect_dictCursor

ledger = Blueprint('ledger', __name__, template_folder='ledger_html', static_folder='ledger_static')


@ledger.route('/ledger/father')
def father_ledger():
    return render_template('f_ledger.html')


@ledger.route('/ledger/father/ajax/<ajax_type>')
def father_ledger_ajax(ajax_type):
    sql_connect, sql_cursor = connect_dictCursor()
    if ajax_type == 'load':
        year_int = datetime.now().year
        month_int = datetime.now().month
        # handle offset
        offset = int(request.args.get('offset', '0'))
        year_offset = 0
        while offset > month_int:
            year_offset += 1
            month_int += 12
        month_int = month_int - offset
        year_int = year_int - year_offset

        next_month_int = month_int + 1
        year = str(year_int)
        month = str(month_int)
        next_month = str(next_month_int)
        sql_cursor.execute(
            f"select * from ledger_father where time>'{year + '-' + month + '-1'}' and time<'{year + '-' + next_month + '-1'}' order by time desc ,id desc")
        fetch = sql_cursor.fetchall()
        for i in range(0, len(fetch)):
            fetch[i]['amount'] = str(fetch[i]['amount'])
            fetch[i]['time'] = fetch[i]['time'].strftime("%Y-%m-%d")
        sql_cursor.close()
        sql_connect.close()
        return jsonify(fetch)


@ledger.route('/ledger/father/modify', methods=['POST', 'GET'])
def father_leger_modify():
    if request.method == 'GET':
        return render_template('f_ledger_form.html')
    elif request.method == 'POST':
        form = request.form
        time = form['year'] + '-' + form['month'] + '-' + form['date']
        sql_connect, sql_cursor = connect_dictCursor()
        sql_cursor.execute(
            f'''insert into ledger_father(amount,sort,item,time,first_hand,cashier,auditor,remark) 
                values('{form['amount']}','{form['sort']}','{form['item']}','{time}','{form['first_hand']}','{form['cashier']}','{form['auditor']}','{form['remark']}')
            '''
        )
        sql_connect.commit()
        sql_cursor.close()
        sql_connect.close()
        return redirect('/ledger/father')
