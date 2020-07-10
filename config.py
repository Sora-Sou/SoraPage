from datetime import timedelta
import pymysql

SECRET_KEY = 'SoraPage-Project'
SESSION_LIFETIME = timedelta(days=7)


class SQL:
    host = '127.0.0.1'
    port = 3306
    user = 'root'
    password = None
    database = 'sorapage'

    def connect_Dict(self):
        sql_connect = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                      database=self.database)
        sql_cursor = sql_connect.cursor(cursor=pymysql.cursors.DictCursor)
        return sql_connect, sql_cursor

    def connect(self):
        return pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                               database=self.database)
