from flask import Blueprint, render_template, request, redirect, jsonify, flash
from datetime import datetime
from sql import connect_dictCursor

ledger = Blueprint('ledger', __name__, template_folder='ledger_html', static_folder='ledger_static')


@ledger.route('/ledger/father')
def father_ledger():
    sql_connect, sql_cursor = connect_dictCursor()
    sql_cursor.execute("select insert_time from ledger_father order by insert_time desc ")
    fetch = sql_cursor.fetchall()
    all_offset = []
    for i in range(0, len(fetch)):
        year = fetch[i]['insert_time'].year
        month = fetch[i]['insert_time'].month
        c_year = datetime.now().year
        c_month = datetime.now().month
        offset = (c_year - year) * 12 + c_month - month
        if offset not in all_offset:
            all_offset.append(offset)
    sql_cursor.close()
    sql_connect.close()
    return render_template('f_ledger.html', all_offset=all_offset)


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
            f"select * from ledger_father where insert_time>='{year + '-' + month + '-1'}' and insert_time<'{year + '-' + next_month + '-1'}' order by insert_time desc ,id desc")
        fetch = sql_cursor.fetchall()
        for i in range(0, len(fetch)):
            fetch[i]['amount'] = str(fetch[i]['amount'])
            fetch[i]['insert_time'] = fetch[i]['insert_time'].strftime("%Y-%m-%d")
        sql_cursor.close()
        sql_connect.close()
        return jsonify(fetch)


@ledger.route('/ledger/father/modify/<modify_type>', methods=['POST', 'GET'])
def father_leger_modify(modify_type):
    sql_connect, sql_cursor = connect_dictCursor()

    if modify_type == 'add' and request.method == 'GET':
        return render_template('f_ledger_form.html')
    elif modify_type == 'add' and request.method == 'POST':
        form = request.form
        time = form['year'] + '-' + form['month'] + '-' + form['day']
        sql_cursor.execute(
            f'''insert into ledger_father(amount,sort,item,insert_time,first_hand,cashier,auditor,remark) 
                values('{form['amount']}','{form['sort']}','{form['item']}','{time}','{form['first_hand']}','{form['cashier']}','{form['auditor']}','{form['remark']}')
            '''
        )
        sql_connect.commit()
        sql_cursor.close()
        sql_connect.close()
        flash('添加成功！')
        return redirect('/ledger/father')

    if modify_type == 'change' and request.method == 'GET':
        change_id = request.args.get('id')
        sql_cursor.execute(f"select * from ledger_father where id='{change_id}'")
        fetch = sql_cursor.fetchone()
        fetch['year'] = fetch['insert_time'].year
        fetch['month'] = fetch['insert_time'].month
        fetch['day'] = fetch['insert_time'].day
        sql_cursor.close()
        sql_connect.close()
        return render_template('f_ledger_form.html', fetch=fetch)
    elif modify_type == 'change' and request.method == 'POST':
        form = request.form
        time = form['year'] + '-' + form['month'] + '-' + form['day']
        sql_cursor.execute(
            f'''update ledger_father set amount='{form['amount']}', sort='{form['sort']}', item='{form['item']}', insert_time='{time}', 
                    first_hand='{form['first_hand']}', cashier='{form['cashier']}', auditor='{form['auditor']}', 
                    remark='{form['remark']}' where id='{form['change_id']}'; '''
        )
        sql_connect.commit()
        sql_cursor.close()
        sql_connect.close()
        flash('修改成功!')
        return redirect('/ledger/father')

    if modify_type == 'delete':
        delete_id = request.args.get('id')
        sql_cursor.execute(f"delete from ledger_father where id='{delete_id}'")
        sql_connect.commit()
        flash('删除成功!')
        sql_cursor.close()
        sql_connect.close()
        return redirect('/ledger/father')
