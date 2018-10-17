from abc import ABCMeta, abstractmethod


class AbstractHelper(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        super(AbstractHelper, self).__init__()
        self._clean_up = True

    @property
    def clean_up(self):
        return self._clean_up

    @clean_up.setter
    def clean_up(self, value):
        self._clean_up = bool(value)


    @abstractmethod
    def __enter__(self):
        raise NotImplementedError()

    @abstractmethod
    def __exit__(self,exc_type,exc_value,traceback):
        raise NotImplementedError()