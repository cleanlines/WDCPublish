
from BaseObject import BaseObject

class PublishFWPServicesHelper(BaseObject):

    def __init__(self):
        super(PublishFWPServicesHelper,self).__init__()
        self._logger.do_message("PublishFWPServicesHelper initialised")



    def publish(self):
        self._out_temp_db = FileGeodatabaseHelper()