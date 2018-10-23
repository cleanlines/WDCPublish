
from abc import ABCMeta, abstractmethod


class AbstractPublishHelper(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def publish(self):
        raise NotImplementedError()