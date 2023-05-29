import re


class Problem:
    def __init__(self, test_id, cursor):
        cursor.execute("select test_name, test_desc from manage.test_table where test_id=%s", (test_id,))
        result = cursor.fetchone()
        self.idx = test_id
        self.title, self.description = result


class Submission:
    def __init__(self, sid, test_id, cursor):
        cursor.execute("select submission_time, result from manage.record where sid=%s and test_id=%s", (sid, test_id))
        if cursor.rowcount == 0:
            self.time = "N/A"
            self.message = ""
            self.status = "default"
            pass
        else:
            result = cursor.fetchone()
            self.time, self.message = result
            self.status = "success" if self.message == "success" else "danger"


class Table:
    def __init__(self, user, table_id, cursor):
        # if re.match('^pub', table_id):
        sql = """ select * from {} """.format(table_id)
        cursor.execute(sql)
        # else:
        #     cursor.execute("select * from %s.%s", (user, table_id))
        description = cursor.description
        result = cursor.fetchall()
        self.description = []
        for i in range(len(description)):
            self.description.append(description[i][0])
        self.result = result
        self.name = table_id
        self.len = len(result)


class ProblemList:
    def __init__(self, cursor):
        cursor.execute("select test_id,set_id from manage.test_table where set_id!='-1' ")
        result = cursor.fetchall()
        self.result = result


class TableList:
    def __init__(self, cursor):
        cursor.execute("show tables")
        user_tables = cursor.fetchall()
        cursor.execute("show tables from pub")
        pub_tables = cursor.fetchall()
        self.tables = [x[0] for x in user_tables] + ["pub."+x[0] for x in pub_tables]
        self.create_tables = {}
        for table in self.tables:
            cursor.execute("show create table " + table)
            result = cursor.fetchone()
            self.create_tables[table] = result[1]

