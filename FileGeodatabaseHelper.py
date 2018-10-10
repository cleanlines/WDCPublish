from BaseObject import BaseObject
import arcpy
import tempfile

class FileGeodatabaseHelper(BaseObject):
    def __init__(self):
        super(FileGeodatabaseHelper,self).__init__()
        self._logger.do_message("FileGeodatabaseHelper initialised")

    def new_file_geodatabase(self):

        result = arcpy.CreateFileGDB_management(temploc, an_uuid)[0]