import pymysql
from config import SQL
from datetime import datetime


# from sql import connect_dictCursor
# sql_connect, sql_cursor = connect_dictCursor()

def connect_dictCursor():
    sql_connect = pymysql.connect(host=SQL['host'], port=SQL['port'], database=SQL['database'],
                                  user=SQL['user'], password=SQL['password'])
    sql_cursor = sql_connect.cursor(cursor=pymysql.cursors.DictCursor)
    return sql_connect, sql_cursor


def sql_now(precision=""):
    if precision == "" or precision == "seconds":
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elif precision == "days":
        return datetime.now().strftime("%Y-%m-%d")


def page_initial():
    sql_connect, sql_cursor = connect_dictCursor()
    sql_cursor.execute(
        '''CREATE TABLE if not exists page(
            id INT NOT NULL AUTO_INCREMENT,
            url VARCHAR(128),
            createTime TIMESTAMP,
            lastUpdate TIMESTAMP,
            visitCount INT,
            authorization INT,
            PRIMARY KEY(id)
            )'''
    )
    sql_connect.commit()
    sql_cursor.close()
    sql_connect.close()


def comment_initial():
    sql_connect, sql_cursor = connect_dictCursor()
    sql_cursor.execute(
        '''CREATE TABLE if not exists comment(
            id INT NOT NULL AUTO_INCREMENT,
            url VARCHAR(128),
            uid INT,
            name VARCHAR(20),
            email VARCHAR(30),
            comment VARCHAR(200),
            time TIMESTAMP,
            parent INT,
            replyTo INT,
            sequence VARCHAR(4),
            replyToSeq VARCHAR(4),
            PRIMARY KEY(id)
        )'''
    )
    sql_connect.commit()
    sql_cursor.close()
    sql_connect.close()


def galgame_initial():
    sql_connect, sql_cursor = connect_dictCursor()
    sql_cursor.execute(
        '''create table if not exists galgame(
            id int not null AUTO_INCREMENT primary key,
            name varchar(20),
            imgLen int,
            overall varchar(2),
            plot varchar(2),
            characterRank varchar(2),
            music varchar(2),
            CG varchar(2),
            date timestamp
        )'''
    )
    sql_connect.commit()
    sql_cursor.execute(
        '''create table if not exists galgame_detail(
            id int not null AUTO_INCREMENT primary key,
            name varchar(20),
            target varchar(20),
            content json
        )'''
    )
    sql_connect.commit()
    sql_cursor.close()
    sql_connect.close()


def ledger_father_initial():
    sql_connect, sql_cursor = connect_dictCursor()
    sql_cursor.execute(
        '''create table if not exists ledger_father(
            id int not null AUTO_INCREMENT primary key,
            amount DEC(10,2),
            sort varchar(2),
            item varchar(400),
            insert_time timestamp,
            first_hand varchar(10),
            cashier varchar(10),
            auditor varchar(10),
            remark varchar(200)
        )'''
    )
    sql_connect.commit()
    sql_cursor.close()
    sql_connect.close()


def ledger_initial():
    sql_connect, sql_cursor = connect_dictCursor()
    sql_cursor.execute(
        '''create table if not exists ledger(
            id int not null AUTO_INCREMENT primary key,
            sort varchar(10),
            sort_detail varchar(20),
            amount DEC(10,2),
            time_ timestamp,
            note varchar(200)
        )'''
    )
    sql_connect.commit()
    sql_cursor.close()
    sql_connect.close()


def users_initial():
    sql_connect, sql_cursor = connect_dictCursor()
    sql_cursor.execute(
        '''create table if not exists users(
            id int not null auto_increment primary key,
            name_ varchar(20),
            email varchar(20),
            password varchar(128),
            register_date timestamp,
            balance decimal(7,2)
        )'''
    )
    sql_connect.commit()
    sql_cursor.close()
    sql_connect.close()


def v2ray_initial():
    sql_connect, sql_cursor = connect_dictCursor()
    sql_cursor.execute(
        '''create table if not exists v2ray_node(
            id int not null auto_increment primary key,
            node_name varchar(30),
            node_status int default 0,
            address varchar(30),
            port int,
            relay_address varchar(30),
            relay_port int,
            order_ int,
            node_level int,
            in_up bigint,
            in_down bigint,
            out_up bigint,
            out_down bigint,
            today_in_up bigint,
            today_in_down bigint,
            today_out_up bigint,
            today_out_down bigint
        )'''
    )
    sql_connect.commit()
    sql_cursor.execute(
        '''create table if not exists v2ray_user(
            uid int not null primary key,
            uuid varchar(40),
            last_v2ray_login timestamp,
            user_level int,
            level_expire timestamp,
            up bigint,
            down bigint,
            today_up bigint,
            today_down bigint
        )
        '''
    )
    sql_connect.commit()
    sql_cursor.close()
    sql_connect.close()


def trade_initial():
    sql_connect, sql_cursor = connect_dictCursor()
    sql_cursor.execute(
        '''create table if not exists trade(
            tid varchar(64) not null primary key,
            uid int,
            trade_subject varchar(64),
            trade_sort varchar(10),
            trade_amount decimal (7,2),
            trade_time timestamp,
            trade_succeed int
        )
        '''
    )
    sql_connect.commit()
    sql_cursor.close()
    sql_connect.close()
