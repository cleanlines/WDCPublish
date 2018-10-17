from TempFileName import TempFileName
from BaseObject import BaseObject
import arcpy

from AbstractHelper import AbstractHelper

class FileGeodatabaseHelper(AbstractHelper, BaseObject):
    def __init__(self):
        super(FileGeodatabaseHelper,self).__init__()
        # self._clean_up = False
        self._current_file_geodb = None
        self.log("FileGeodatabaseHelper initialised")


    def new_file_geodatabase(self):
        self._delete_current_file_geodb()
        path,file_geodb_name = TempFileName.generate_temporary_file_name(".gdb",split=True)
        self._current_file_geodb = arcpy.CreateFileGDB_management(path,file_geodb_name)[0]
        self.log("File geodb created at: %s" % self._current_file_geodb)
        return self._current_file_geodb

    def _delete_current_file_geodb(self):
        if self._current_file_geodb and self._clean_up:
            try:
                self.log("Cleaning up file geodb %s" % str(self._current_file_geodb))
                arcpy.Delete_management(self._current_file_geodb)
            except Exception as e:
                self.errorlog(e.message)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # clean up the file geodb
        self._delete_current_file_geodb()