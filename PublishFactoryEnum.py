
class PublishFactoryEnum(object):
    __classes = ["PublishFWPServicesHelper", "PublishGeodbServicesHelper"]
    FWP, GEODB = __classes

    @classmethod
    def type_valid(cls, item_type):
        return item_type in cls.__classes
