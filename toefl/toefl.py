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
