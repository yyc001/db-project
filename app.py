from flask import Flask, render_template
import pymysql

app = Flask(__name__)
app.config['SECRET_KEY'] = '\x0fW\xdc\x13\xeel(\xe9\xb5\xbaa\xa4\xc0\xb5\xaaK^\xd1Y\x81)#\x92T'


@app.route('/hello')
def hello_world():  # put application's code here
    # 打开数据库连接
    db = pymysql.connect(host='localhost', user='root', passwd='example', port=3306)
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    # 使用 execute()  方法执行 SQL 查询
    cursor.execute("SELECT VERSION()")
    # 使用 fetchone() 方法获取单条数据.
    data = cursor.fetchone()
    ret = "Database version : %s " % data
    # 关闭数据库连接
    db.close()
    return ret


@app.route('/')
def index():
    return render_template("index.html", util="首页")


@app.route('/new')
def create_user():
    username = "student3".replace("`'% ", "")
    password = "123456"
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

    query = cursor.mogrify("grant all on `" + username + "`.* to %s with grant option", (username, ))
    cursor.execute(query)
    # (('information_schema',), ('madb',), ('mbdb',), ('mysql',), ('performance_schema',), ('pub',), ('student1',),
    #  ('student2',), ('student3',), ('sys',))
    db.close()
    return 'Success'


if __name__ == '__main__':
    app.run()
