import datetime
import re

from flask import Flask, render_template, session, redirect, request
from pymysql import MySQLError

from data_format import Problem, Submission, Table, ProblemList, TableList
from sql_factory import SQLFactory

app = Flask(__name__,
            static_folder='static',
            static_url_path='/'
            )
app.config['SECRET_KEY'] = '\x0fW\xdc\x13\xeel(\xe9\xb5\xbaa\xa4\xc0\xb5\xaaK^\xd1Y\x81)#\x92T'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=7)

@app.route('/homepage')
def homepage():
    return render_template("homepage.html")




@app.route('/')
def index():
    if session.get("username") is not None:
        factory = SQLFactory()
        cursor = factory.get_root_cursor()
        cursor.execute("select set_id,test_id from manage.test_table limit 1")
        result = cursor.fetchone()
        return redirect(f"/question/{result[0]}/{result[1]}")
    return redirect('/login')


@app.route('/login')
def login():
    failed = request.args.get("failed", 'false') == 'true'
    return render_template("login.html", failed=failed)


@app.route('/login/action', methods=["POST"])
def login_action():
    session.clear()
    factory = SQLFactory()
    username = request.form.get('username')
    password = request.form.get('password')
    if factory.user_login(username, password):
        session['username'] = username
        session['password'] = password
        return redirect("/")
    else:
        return redirect("/login?failed=true")


@app.route('/user/execute', methods=["POST"])
def run_sql():
    if 'username' not in session:
        return {
                   "result": "failure",
                   "errno": -1,
                   "errmsg": "Access denied",
               }, 401

    query = request.form.get("sql", "")
    page_size = request.form.get("page-size", "")
    page_size = int(page_size) if page_size.isdigit() else 15

    factory = SQLFactory()
    if not factory.user_login(session['username'], session['password']):
        factory.closeAll()
        return {
                   "result": "failure",
                   "errno": -2,
                   "errmsg": "Password changed",
               }, 401

    try:
        cursor = factory.get_user_cursor()
        rowcount = cursor.execute(query)
        return {
            "result": "success",
            "rowcount": rowcount,
            "data": cursor.fetchmany(min(rowcount, page_size)),
            "description": cursor.description,
        }
    except MySQLError as e:
        errno, errmsg = e.args
        return {
            "result": "failure",
            "errno": errno,
            "errmsg": errmsg,
        }
    finally:
        factory.closeAll()


@app.route('/user/verify', methods=["POST"])
def verify():
    if 'username' not in session:
        return {
                   "result": "failure",
                   "errno": -1,
                   "errmsg": "Access denied",
               }, 401
    test = request.form.get("test", "test0_0")
    username = session.get("username")
    factory = SQLFactory()
    try:
        cursor = factory.get_root_cursor()
        message = check_same_table(username, test, cursor)
        cursor.execute("select result from manage.record where sid=%s and test_id=%s", (username, test))
        if cursor.rowcount == 0:
            cursor.execute("insert into manage.record values (%s,now(),%s,%s)", (username, test, message))
        else:
            cursor.execute("update manage.record set result=%s,submission_time=now() where sid=%s and test_id=%s",
                           (message, username, test))

        return {
            "result": "success" if message == "success" else "failure",
            "message": message,
        }
    except MySQLError as e:
        errno, errmsg = e.args
        return {
            "result": "failure",
            "errno": errno,
            "errmsg": errmsg,
        }
    finally:
        factory.closeAll()


@app.route('/search/test', methods=["POST"])
def search_t():
    ask = request.form.get("the_search_test", "")
    factory = SQLFactory()

    try:
        cursor = factory.get_root_cursor()
        answer = cursor.execute("select set_id,test_id from manage.test_table where test_id=%s", (ask,))
        if answer:
            result = cursor.fetchone()
            return {
                "resp": "success",
                "url": "/question/{}/{}".format(result[0], result[1]),
                "info": "成功搜索到题目{}".format(ask),
            }
        else:
            return {
                "resp": "failure",
                "url": "",
                "info": "失败搜索到题目{}".format(ask),
            }
    except MySQLError as e:
        errno, errmsg = e.args
        return {
            "resp": "failure",
            "url": "",
            "info": "失败搜索到题目{}".format(ask),
        }
    finally:
        factory.closeAll()


def check_same_table(user_db, test, cursor):
    cursor.execute(f"select * from answer.{test}")
    std_rownum = cursor.rowcount
    std_description = set([desc[0] for desc in cursor.description])
    std_description_list = [desc[0] for desc in cursor.description]
    std_rows = set(cursor.fetchall())

    cursor.execute(f"select TABLE_NAME from INFORMATION_SCHEMA.TABLES "
                   f"where TABLE_SCHEMA='{user_db}' and TABLE_NAME='{test}'")
    if cursor.rowcount == 0:
        return f"用户表 {test} 不存在。"

    cursor.execute(f"select * from {user_db}.{test}")
    user_rownum = cursor.rowcount
    user_description = cursor.description
    user_description = set([desc[0] for desc in user_description])

    leak = std_description - user_description
    more = user_description - std_description
    if len(leak) or len(more):
        return f"缺少表头 {','.join(leak)}， 多余表头 {','.join(more)}。"

    if std_rownum < user_rownum:
        return f"比标准答案多 {user_rownum - std_rownum} 行。"
    if std_rownum > user_rownum:
        return f"比标准答案少 {std_rownum - user_rownum} 行。"

    cursor.execute(f"select {','.join(std_description_list)} from {user_db}.{test}")
    err_rownum = 0
    for row in cursor.fetchall():
        if row not in std_rows:
            err_rownum += 1
    if err_rownum > 0:
        return f"与标准答案相比错 {err_rownum} 行。"

    return "success"


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/question/<set_id>/<test_id>')
def test(set_id, test_id):
    if session.get("username") is not None:
        factory = SQLFactory()
        cursor = factory.get_root_cursor()
        problem = Problem(test_id, cursor)
        submit = Submission(session.get("username"), test_id, cursor)
        table = Table("username", "pub.sc", cursor)
        path = {"set": set_id, "test": test_id}
        problem_list = ProblemList(cursor)
        factory.user_login(session['username'], session['password'])
        user_cursor = factory.get_user_cursor()
        table_list = TableList(user_cursor)
        return render_template("index.html",
                               problem=problem,
                               problem_list=problem_list,
                               submit=submit,
                               table=table,
                               path=path,
                               table_list=table_list,
                               )
    return redirect('/login')


@app.route('/profile')
def profile():
    return render_template("profile.html")


@app.route('/user/find_table', methods=["POST"])
def find_table():
    if 'username' not in session:
        return {
                   "result": "failure",
                   "errno": -1,
                   "errmsg": "Access denied",
               }, 401
    regex = re.compile(r"^[a-zA-Z_.]+$")
    name = request.form.get('name')
    name = regex.match(name).group()
    page_size = request.form.get("page-size", "")
    page_size = int(page_size) if page_size.isdigit() else 15

    factory = SQLFactory()
    if not factory.user_login(session['username'], session['password']):
        factory.closeAll()
        return {
                   "result": "failure",
                   "errno": -2,
                   "errmsg": "Password changed",
               }, 401

    try:
        cursor = factory.get_user_cursor()
        rowcount = cursor.execute("select * from " + name)
        return {
            "result": "success",
            "rowcount": rowcount,
            "data": cursor.fetchmany(min(rowcount, page_size)),
            "description": cursor.description,
        }
    except MySQLError as e:
        errno, errmsg = e.args
        return {
            "result": "failure",
            "errno": errno,
            "errmsg": errmsg,
        }
    finally:
        factory.closeAll()


if __name__ == '__main__':
    app.run(debug=True)
