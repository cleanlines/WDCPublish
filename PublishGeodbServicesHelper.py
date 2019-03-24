from BaseObject import BaseObject
from MapDocumentHelper import MapDocumentHelper
from ArcGISOnlineHelper import ArcGISOnlineHelper
from AbstractPublishHelper import AbstractPublishHelper
import os


class PublishGeodbServicesHelper(BaseObject, AbstractPublishHelper):

    def __init__(self):
        super(PublishGeodbServicesHelper, self).__init__()
        self.log("PublishGeodbServicesHelper initialised")

    def publish(self):
        try:
            for a_template in self._config.templates:
                try:
                    with MapDocumentHelper(a_template) as map_doc_helper:
                        map_doc_helper.prepare_map_document(self._config.sdeconnection)
                        with ArcGISOnlineHelper() as agol_helper:
                            service_name = os.path.basename(os.path.splitext(a_template["map"])[0])
                            fs_id = agol_helper.publish_map_doc(map_doc_helper.current_map_doc, service_name)
                            agol_helper.share_items(fs_id, groups=a_template["groupids"])
                except Exception as e:
                    self.errorlog(e)
                    self.log("Publishing %s data failed Error below:" % a_template['map'])
        except Exception:
            self.log("Publishing Geodb data failed Error below:")
            raise


# if __name__ == "__main__":
#     PublishGeodbServicesHelper().publish()