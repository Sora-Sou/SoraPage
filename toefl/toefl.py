from flask import Blueprint, render_template, request, redirect
from sql import connect_dictCursor

toefl = Blueprint('toefl', __name__, template_folder='toefl_html', url_prefix='/toefl')


@toefl.route('/speaking')
def toefl_speaking():
    sql_connect, sql_cursor = connect_dictCursor()
    sql_cursor.execute('''select * from toefl_speaking''')
    sql_fetch = sql_cursor.fetchall()
    sql_cursor.close()
    sql_connect.close()
    return render_template('speaking.html', fetch=sql_fetch, length=len(sql_fetch))


@toefl.route('/speaking/add', methods=['GET', 'POST'])
def toefl_speaking_add():
    if request.method == 'GET':
        return render_template('speaking_add.html')
    elif request.method == 'POST':
        form = request.form
        sql_connect, sql_cursor = connect_dictCursor()
        sql_cursor.execute(
            f'''insert into toefl_speaking(sort,origin,question,answer)
                values('{form['sort']}','{form['origin']}','{form['question']}','{form['answer']}')''')
        sql_connect.commit()
        sql_cursor.close()
        sql_connect.close()
        return redirect('/toefl/speaking')
