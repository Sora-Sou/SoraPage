from flask import Flask, redirect, url_for, request, make_response, render_template
from ACGN.ACGN import ACGN
from user.user import user
from comment import comment

app = Flask(__name__)
app.register_blueprint(ACGN)
app.register_blueprint(user)
app.register_blueprint(comment)

app.config.from_pyfile('config.py')
app.secret_key = app.config['SECRET_KEY']


@app.route('/')
def index():
    return redirect(url_for('ACGN.acgn'))


if __name__ == '__main__':
    app.run(debug=True)
