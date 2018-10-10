import Logger

class BaseLogger(object):

    def __init__(self):
        self._logger = Logger.Logger(loglevel="info", log_to_file=True)
