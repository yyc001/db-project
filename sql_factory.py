import pymysql
from pymysql.err import OperationalError


class SQLFactory:
    instance = None
    BACKEND = "MySQL"
    HOST = "localhost"
    PORT = 3306

    def __init__(self):
        self.db_root = pymysql.connect(host=SQLFactory.HOST, user='root', passwd='example', port=SQLFactory.PORT)
        self.db_root.autocommit(True)
        self.db_user = None
        self.errno = 0
        self.errmsg = None

    def closeAll(self):
        if self.db_root and not self.db_root._closed:
            self.db_root.cursor().close()
            self.db_root.close()
        if self.db_user and not self.db_user._closed:
            self.db_user.cursor().close()
            self.db_user.close()

    def __del__(self):
        self.closeAll()

    def get_root_cursor(self):
        return self.db_root.cursor()

    def get_user_cursor(self):
        assert self.db_user is not None
        return self.db_user.cursor()

    def user_login(self, user, passwd, autocommit=True):
        try:
            assert user and passwd and user != 'root'
            self.db_user = pymysql.connect(
                host=SQLFactory.HOST,
                user=user,
                passwd=passwd,
                port=SQLFactory.PORT,
                database=user
            )
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
    username = username.replace(r"[^a-zA-Z0-9]", "")

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
