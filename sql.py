import pymysql
from config import sql


def connect_dictCursor():
    sql_connect = pymysql.connect(host=sql['host'], port=sql['port'], database=sql['database'],
                                  user=sql['user'], password=sql['password'])
    sql_cursor = sql_connect.cursor(cursor=pymysql.cursors.DictCursor)
    return sql_connect, sql_cursor


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
    print("comment table created")


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
    print("galgame table created")


def toefl_speaking_initial():
    sql_connect, sql_cursor = connect_dictCursor()
    sql_cursor.execute(
        '''create table if not exists toefl_speaking(
            id int not null AUTO_INCREMENT primary key,
            sort int,
            origin varchar(10),
            question varchar(1000),
            answer varchar(1500)
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
