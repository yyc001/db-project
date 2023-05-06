
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
