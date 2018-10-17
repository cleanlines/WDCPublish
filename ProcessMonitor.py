from BaseObject import BaseObject
import sqlite3
import datetime

class ProcessMonitor(BaseObject):

    def __init__(self):
        super(ProcessMonitor, self).__init__()
        self.log("ProcessMonitor initialised")
        self._connection = sqlite3.connect(self._config.db)

    def log_success(self,processname):
        c = self._connection.cursor()
        c.execute(self._config.insert, (None,processname,datetime.datetime.now(),True,None))
        self._connection.commit()

    def log_failure(self,processname,error):
        c = self._connection.cursor()
        c.execute(self._config.insert, (None, processname, datetime.datetime.now(), False, error))
        self._connection.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # clean up the file geodb
        self._connection.close()


# if __name__ == "__main__":
#     with ProcessMonitor() as pm:
#         pm.log_success("TEST")
#         try:
#             raise Exception("This is a test exception")
#         except Exception as e:
#             pm.log_failure("TESTERROR",e.message)
