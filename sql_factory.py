from typing import Optional

import pymysql
from pymysql.err import OperationalError, MySQLError


class SQLFactory:
    instance = None
    BACKEND = "MySQL"
    HOST = "localhost"
    PORT = 3306

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            cls.instance = SQLFactory()
        return cls.instance

    def __init__(self):
        self.db_root = pymysql.connect(host=SQLFactory.HOST, user='root', passwd='example', port=SQLFactory.PORT)
        self.db_user = None
        self.errno = 0
        self.errmsg = None

    def __del__(self):
        if self.db_root:
            self.db_root.close()
        if self.db_user:
            self.db_user.close()

    def get_root_cursor(self):
        return SQLCursor(self.db_root.cursor())

    def get_user_cursor(self):
        assert self.db_user is not None
        return SQLCursor(self.db_user.cursor())

    def user_login(self, user, passwd, autocommit=True):
        try:
            assert user and passwd and user != 'root'
            self.db_user = pymysql.connect(host=SQLFactory.HOST, user=user, passwd=passwd, port=SQLFactory.PORT)
            self.errno = 0
            self.db_user.autocommit(autocommit)
            return True
        except OperationalError as e:
            self.errno, self.errmsg = e.args
            return False
        except AssertionError:
            self.errno = -1
            self.errmsg = 'Access denied'
            return False


class SQLCursor:
    def __init__(self, cursor):
        self.errmsg = None
        self.errno = None
        self.execute_query = None
        self.cursor = cursor

    def execute(self, query, *args):
        self.execute_query = self.cursor.mogrify(query, args)
        try:
            rowcount = self.cursor.execute(self.execute_query)
        except MySQLError as e:
            self.errno, self.errmsg = e.args
            return -1
        return rowcount

    def all_results(self):
        for i in range(self.cursor.rowcount):
            yield self.cursor.fetchone()


if __name__ == "__main__":
    factory = SQLFactory()

    print(factory.user_login(None, None))
    print(factory.errno)
    print(factory.errmsg)

    cursor = factory.get_root_cursor()
    result = cursor.execute("SELECT VERSION()")
    print(result)
    for row in cursor.all_results():
        print(row)

    print(factory.user_login("student1", "123456"))
    cursor = factory.get_user_cursor()
    cursor.execute("select * from pub.sc")
    for row in cursor.all_results():
        print(row)


def __create_user(username, password):
    username = username.replace("`'% ", "")

    db = pymysql.connect(host='localhost', user='root', passwd='example', port=3306)
    cursor = db.cursor()

    query = cursor.mogrify("drop user if exists %s", (username,))
    cursor.execute(query)

    query = cursor.mogrify("create user %s@'%%' identified by %s", (username, password,))
    cursor.execute(query)

    query = cursor.mogrify("drop database if exists %s" % (username,))
    cursor.execute(query)

    # 我只能说转义字符并不是多么智能
    query = cursor.mogrify("create database if not exists `" + username + "`")
    cursor.execute(query)

    query = cursor.mogrify("grant all on `" + username + "`.* to %s with grant option", (username,))
    cursor.execute(query)
    db.close()
    return 'Success'
