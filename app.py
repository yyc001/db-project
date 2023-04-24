import datetime

from flask import Flask, render_template, session, redirect, request, json
from pymysql import MySQLError

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
        return render_template("index.html")
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
    query = request.form.get("sql", "")
    page_size = request.form.get("page-size", "")
    page_size = int(page_size) if page_size.isdigit() else 0

    factory = SQLFactory.get_instance()
    factory.user_login(session['username'], session['password'])

    ret = {}

    try:
        cursor = factory.get_user_cursor()
        rowcount = cursor.execute(query)    # TODO record queries
        ret["result"] = "success"
        ret["rowcount"] = rowcount
        ret["data"] = cursor.fetchmany(min(rowcount, page_size))
        ret["description"] = cursor.description

    except MySQLError as e:
        errno, errmsg = e.args
        ret["result"] = "failure"
        ret["errno"] = errno
        ret["errmsg"] = errmsg

    print(ret)
    return json.dumps(ret)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run()
