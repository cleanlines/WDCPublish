import Logger
import inspect
from JSONConfig import JSONConfig
from BaseLogger import BaseLogger


class BaseObject(BaseLogger):

    def __init__(self):
        super(BaseObject, self).__init__()
        self._file = inspect.getsourcefile(self.__class__)
        self._class_name = inspect.getmoduleinfo(self._file).name
        self._config = JSONConfig(class_name=self._class_name)
