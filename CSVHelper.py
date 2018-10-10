from BaseObject import BaseObject
import datetime
from SendEmail import SendEmail
import os
import tempfile
import csv

class CSVHelper(BaseObject):

    def __init__(self,base_csv_file=None):
        super(CSVHelper,self).__init__()
        self._logger.do_message("CSVHelper initialised")
        file = "{0}.csv".format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f"))
        if base_csv_file:
            file = "NotInGIS_{0}_".format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f"))+os.path.basename(base_csv_file)

        self._out_file = os.path.join(tempfile.gettempdir(),file)
        self._logger.do_message("CSVHelper outfile:{0}".format(self._out_file))


    @property
    def out_file(self):
        if os.path.exists(self._out_file):
            return self._out_file
        else:
            return None

    def write_rows_to_csv(self,rows):
        if self._out_file:
            with open(self._out_file,'wb') as csvfile:
                writer = csv.writer(csvfile,delimiter=',')
                for row in rows:
                    writer.writerow(row)
        return self.out_file