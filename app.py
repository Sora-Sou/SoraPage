from flask import Flask
from acgn.acgn import acgn
from user.user import user
from comment import comment
from ledger.ledger import ledger
from admin.admin import admin_c
from v2ray.v2ray import v2ray

app = Flask(__name__)
app.register_blueprint(acgn)
app.register_blueprint(user)
app.register_blueprint(comment)
app.register_blueprint(ledger)
app.register_blueprint(admin_c)
app.register_blueprint(v2ray)

app.config.from_pyfile('config.py')


@app.route('/')
def index():
    return "SoraPage Project presents"


if __name__ == '__main__':
    app.run()
