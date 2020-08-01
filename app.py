from flask import Flask, redirect, url_for, abort
from acgn.acgn import acgn
from user.user import user
from comment import comment
from toefl.toefl import toefl
from ledger.ledger import ledger

app = Flask(__name__)
app.register_blueprint(acgn)
app.register_blueprint(user)
app.register_blueprint(comment)
app.register_blueprint(toefl)
app.register_blueprint(ledger)

app.config.from_pyfile('config.py')
app.secret_key = app.config['SECRET_KEY']


@app.route('/')
def index():
    return abort(404)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
