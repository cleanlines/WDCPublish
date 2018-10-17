from BaseObject import BaseObject
import datetime
from FileHelper import FileHelper
import csv
import os
from TempFileName import TempFileName


class CSVHelper(BaseObject):

    def __init__(self,base_csv_file=None):
        super(CSVHelper,self).__init__()
        file = "{0}.csv".format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f"))
        if base_csv_file:
            file = "_ags_NotInGIS_{0}_".format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f"))+os.path.basename(base_csv_file)

        self._out_file = os.path.join(TempFileName.get_temp_directory(),file)
        self.log("CSVHelper outfile:{0}".format(self._out_file))
        self.log("CSVHelper initialised")

    @property
    def out_file(self):
        if os.path.exists(self._out_file):
            return self._out_file
        else:
            return None

    def write_rows_to_csv(self, rows):
        if self._out_file:
            with open(self._out_file,'wb') as csvfile:
                writer = csv.writer(csvfile,delimiter=',')
                for row in rows:
                    writer.writerow(row)
        return self.out_file

    def clean_up_temp_csvs(self):
        # for python 2.7 - use glob for 3
        self.log("Cleaning up temp csvs")
        FileHelper().remove_all_temp_files("csv")

    def reader(self, file, delim):
        with open(file, 'rb') as csv_file:
            reader = csv.reader(csv_file, delimiter=str(delim))
            for row in reader:
                yield row

# if __name__ == "__main__":
#     rma = CSVHelper()
#     for y in rma.reader("C:/ZZCloud/Dropbox/Work/WDC/Python/data/Water_FWV_Sept_2018.csv",','):
#         print y
