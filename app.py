import datetime

from flask import Flask, render_template, session, redirect, request, json
from pymysql import MySQLError

from data_format import Problem, Submission, Table, ProblemList
from sql_factory import SQLFactory

app = Flask(__name__,
            static_folder='static',
            static_url_path='/'
            )
app.config['SECRET_KEY'] = '\x0fW\xdc\x13\xeel(\xe9\xb5\xbaa\xa4\xc0\xb5\xaaK^\xd1Y\x81)#\x92T'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=7)


@app.route('/')
def index():
    if session.get("username") is not None:
        factory = SQLFactory()
        cursor = factory.get_root_cursor()
        problem = Problem("start", cursor)
        submit = Submission(session.get("username"), "test0_0", cursor)
        table = Table("username", "pub.sc", cursor)
        problem_list = ProblemList(cursor)
        path = {}
        return render_template("index.html", problem=problem, submit=submit, table=table, problem_list=problem_list, path=path)
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


@app.route('/user/verify')
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

        return json.dumps({
            "result": "success",
            "message": message,
        }).encode().decode("unicode_escape")
    except MySQLError as e:
        errno, errmsg = e.args
        return {
            "result": "failure",
            "errno": errno,
            "errmsg": errmsg,
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
        problem = Problem("test0_0", cursor)
        submit = Submission(session.get("username"), "test0_0", cursor)
        table = Table("username", "pub.sc", cursor)
        path = {"set": set_id, "test": test_id}
        problem_list = ProblemList(cursor)
        return render_template("index.html", problem=problem, problem_list=problem_list, submit=submit, table=table, path=path)
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)
