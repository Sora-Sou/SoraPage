from flask import Blueprint, make_response, redirect, request, session, current_app, render_template, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from sql import connect_dictCursor

user = Blueprint('user', __name__, template_folder='user_html', static_folder='user_static')


@user.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        response = make_response(render_template('login.html'))
        response.set_cookie('referrer', request.referrer)
        return response
    elif request.method == 'POST':
        sql_connect, sql_cursor = connect_dictCursor()
        sql_cursor.execute(f'''SELECT * FROM users WHERE email='{request.form['email']}' ''')
        sql_fetch = sql_cursor.fetchone()
        sql_cursor.close()
        sql_connect.close()
        if sql_fetch is None:
            return render_template('login.html', fail='no_email', email=request.form['email'])
        else:
            if check_password_hash(sql_fetch['password'], request.form['password']):
                response = make_response(redirect(request.cookies.get('referrer')))
                response.delete_cookie('referrer')
                session['uid'] = str(sql_fetch['id'])
                session['name'] = sql_fetch['name']
                session['email'] = sql_fetch['email']
                if request.form.get('keep_login_switch'):
                    current_app.permanent_session_lifetime = current_app.config['SESSION_LIFETIME']
                    session.permanent = True
                return response
            else:
                return render_template('login.html', fail='wrong_password', email=request.form['email'])


@user.route('/logout')
def logout():
    session.clear()
    return redirect(request.referrer)


@user.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        fail = []
        blank = []
        # 是否有未填项
        for element, value in request.form.items():
            if value == '':
                blank.append(element)
                fail.append('blank')
        # 用户名和邮箱是否重复
        sql_connect, sql_cursor = connect_dictCursor()
        sql_cursor.execute(f'''SELECT * FROM users WHERE name='{request.form['name']}' ''')
        sql_fetch_name = sql_cursor.fetchone()
        sql_cursor.execute(f'''SELECT * FROM users WHERE email='{request.form['email']}' ''')
        sql_fetch_email = sql_cursor.fetchone()
        if sql_fetch_name is not None:
            fail.append('used_name')
        if sql_fetch_email is not None:
            fail.append('used_email')
        # 两次密码输入是否一致
        if request.form['password'] != request.form['confirm_password']:
            fail.append('different_password')
        # 返回
        if fail:
            sql_cursor.close()
            sql_connect.close()
            return render_template('register.html', fail=fail, blank=blank, form=request.form)
        else:
            password_hash = generate_password_hash(request.form['password'])
            sql_cursor.execute(
                f'''INSERT INTO users(name,email,password) VALUES('{request.form['name']}','{request.form['email']}','{password_hash}')'''
            )
            sql_connect.commit()
            sql_cursor.execute(f'''SELECT id FROM users WHERE name='{request.form['name']}' ''')
            session['uid'] = sql_cursor.fetchone()[0]
            session['user_name'] = request.form['name']
            sql_cursor.close()
            sql_connect.close()
            if request.cookies.get('referrer'):
                return redirect(request.cookies.get('referrer'))
            else:
                return redirect(url_for('index'))
