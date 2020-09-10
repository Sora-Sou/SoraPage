from flask import Blueprint, render_template, request, redirect
from sql import connect_dictCursor

admin_c = Blueprint("admin", __name__, template_folder="./", static_folder="./")


@admin_c.route("/admin")
def admin_():
    return render_template('admin.html')


@admin_c.route("/toefl/speaking/modify", methods=['POST'])
def toefl_speaking():
    form = request.form
    sql_connect, sql_cursor = connect_dictCursor()
    sql_cursor.execute(
        f'''insert into toefl_speaking(sort,origin,question,answer)
            values('{form['sort']}','{form['origin']}','{form['question']}','{form['answer']}')''')
    sql_connect.commit()
    sql_cursor.close()
    sql_connect.close()
    return redirect('/toefl/speaking')
