from BaseObject import BaseObject
from AbstractPublishHelper import AbstractPublishHelper


class GenericPublishHelper(BaseObject, AbstractPublishHelper):

    # stub class to add an additional publisher once the roading stuff is done.
    def __init__(self):
        super(GenericPublishHelper, self).__init__()
        self.log("GenericPublishHelper initialised")

    def publish(self):
        return