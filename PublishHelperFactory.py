from PublishFactoryEnum import PublishFactoryEnum
import importlib


class PublishHelperFactory(object):

    @staticmethod
    def factory(an_enum):
        if PublishFactoryEnum.type_valid(an_enum):
            a_module = importlib.import_module(an_enum)
            return getattr(a_module, an_enum)()
        else:
            raise Exception("%s is not a valid publisher type" % an_enum)
