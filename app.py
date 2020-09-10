from flask import Flask, redirect
from acgn.acgn import acgn
from user.user import user
from comment import comment
from toefl.toefl import toefl
from ledger.ledger import ledger
from admin.admin import admin_c

app = Flask(__name__)
app.register_blueprint(acgn)
app.register_blueprint(user)
app.register_blueprint(comment)
app.register_blueprint(toefl)
app.register_blueprint(ledger)
app.register_blueprint(admin_c)

app.config.from_pyfile('config.py')
app.secret_key = app.config['SECRET_KEY']
app.send_file_max_age_default = app.config['SEND_FILE_MAX_AGE_DEFAULT']


@app.route('/')
def index():
    return redirect("/ledger")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
