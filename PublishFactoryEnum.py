
class PublishFactoryEnum(object):
    __classes = ["PublishFWPServicesHelper", "PublishGeodbServicesHelper","PublishRAMMHelper"]
    FWP, GEODB, RAMM = __classes

    @classmethod
    def type_valid(cls, item_type):
        return item_type in cls.__classes
