from flask import Blueprint, render_template, request, redirect, jsonify, flash
from datetime import datetime
from sql import connect_dictCursor
from collections import OrderedDict

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


@ledger.route('/ledger')
def ledger_():
    sql_connect, sql_cursor = connect_dictCursor()
    sql_cursor.execute('select * from ledger order by time_ asc limit 1')
    oldest_time = sql_cursor.fetchone()
    if oldest_time is not None:
        oldest_year = int(oldest_time['time_'].strftime('%Y'))
        oldest_month = int(oldest_time['time_'].strftime('%m'))
        current_year = int(datetime.now().strftime('%Y'))
        current_month = int(datetime.now().strftime('%m'))
        max_month_interval = (current_year - oldest_year) * 12 + current_month - oldest_month
        # monthly_data_collection的元素为monthly_data
        monthly_data_collection = []
        for i in range(max_month_interval + 1):
            query_year = current_year
            while i > current_month:
                i = i - 12
                query_year = query_year - 1
            query_month = current_month - i
            query_next_month = query_month + 1
            query_year = str(query_year)
            query_month = str(query_month)
            query_next_month = str(query_next_month)
            sql_cursor.execute(
                f"select * from ledger where time_ >='{query_year + '-' + query_month + '-1'}' and time_ < '{query_year + '-' + query_next_month + '-1'}' order by time_ desc")
            month_data_fetch = sql_cursor.fetchall()
            if len(month_data_fetch) != 0:
                monthly_data = {
                    'month_time': query_year + '年' + query_month + '月',
                    # daily_data_collection_sample = {
                    #     '9月30日': [{'id': 1, 'sort': '支出', 'sort_detail': '食堂', 'amount': 233,'time_': datetime.datetime(2020, 9, 29, 0, 0),'note': ''},
                    #                 {'id': 1, 'sort': '支出', 'sort_detail': '食堂', 'amount': 233,'time_': datetime.datetime(2020, 9, 29, 0, 0),'note': ''}]},
                    #     '9月29日': [{'id': 1, 'sort': '支出', 'sort_detail': '食堂', 'amount': 233,'time_': datetime.datetime(2020, 9, 29, 0, 0), 'note': ''},
                    #                 {'id': 1, 'sort': '支出', 'sort_detail': '食堂', 'amount': 233,'time_': datetime.datetime(2020, 9, 29, 0, 0), 'note': ''}]},
                    # }
                    # 'daily_data_collection': OrderedDict()
                }
                daily_data_collection = OrderedDict()
                for e in month_data_fetch:
                    key = e['time_'].strftime('%m月%d日')
                    if key not in daily_data_collection.keys():
                        daily_data_collection[key] = []
                    daily_data_collection[key].append(e)
                monthly_data['daily_data_collection'] = daily_data_collection
                monthly_data_collection.append(monthly_data)
        sql_cursor.close()
        sql_connect.close()
        return render_template('ledger.html', monthly_data_collection=monthly_data_collection)
    else:
        sql_cursor.close()
        sql_connect.close()
        return render_template('ledger.html')


@ledger.route('/ledger/ajax/<ajax_type>', methods=['GET', 'POST'])
def ledger_add(ajax_type):
    sql_connect, sql_cursor = connect_dictCursor()
    if ajax_type == 'add':
        f = request.form
        time = f['year'] + '-' + f['month'] + '-' + f['date']
        sql_cursor.execute(f'''insert into ledger(sort,sort_detail,amount,time_,note) 
                               values('{f['sort']}','{f['sort_detail']}','{f['amount']}','{time}','{f['note']}')
                            ''')
        sql_connect.commit()
        sql_cursor.close()
        sql_connect.close()
        return 'success'
    if ajax_type == 'delete':
        delete_id = request.form['delete_id']
        sql_cursor.execute(f"delete from ledger where id='{delete_id}'")
        sql_connect.commit()
        sql_cursor.close()
        sql_connect.close()
        return 'success'
    if ajax_type == 'modify':
        f = request.form
        time = f['year'] + '-' + f['month'] + '-' + f['date']
        sql_cursor.execute(
            f'''update ledger set sort='{f['sort']}', sort_detail='{f['sort_detail']}', amount='{f['amount']}', time_='{time}',note='{f['note']}'
                where id={f['data-id']} ''')
        sql_connect.commit()
        sql_cursor.close()
        sql_connect.close()
        return 'success'
