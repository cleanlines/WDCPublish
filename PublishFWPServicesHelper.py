from BaseObject import BaseObject
from FileGeodatabaseHelper import FileGeodatabaseHelper
from MapDocumentHelper import MapDocumentHelper
from ArcGISOnlineHelper import ArcGISOnlineHelper
from AbstractPublishHelper import AbstractPublishHelper
import arcpy


class PublishFWPServicesHelper(BaseObject, AbstractPublishHelper):

    def __init__(self):
        super(PublishFWPServicesHelper, self).__init__()
        self.log("PublishFWPServicesHelper initialised")

    def publish(self):
        try:
            with FileGeodatabaseHelper() as file_geodb_helper:
                self.log("Creating temp file geodatabase")
                self._out_temp_db = file_geodb_helper.new_file_geodatabase()
                # file_geodb_helper.clean_up = False  # DEBUG
                self.log("Copying features to temp file geodatabase")
                self._copy_features_with_join()
                self.log("Features copied - preparing map document")
                with MapDocumentHelper(self._config.template) as map_doc_helper:
                    # pass through the temp geodb with new data and get new map
                    # DEBUG map_doc_helper.clean_up = False
                    map_doc_helper.prepare_map_document(self._out_temp_db)
                    self.log("Map document prepared - publishing to ArcGIS Online")
                    with ArcGISOnlineHelper() as agol_helper:
                        fs_id = agol_helper.publish_map_doc(map_doc_helper.current_map_doc,"FWP")
                        # depending on the group type we may have to do one or the other - so I'm just going to do both
                        agol_helper.share(fs_id, groups=self._config.fwpgroup)
                        agol_helper.share_items(fs_id, groups=self._config.fwpgroup)
        except Exception:
            self.log("Publishing FWP data failed Error below:")
            raise

    def _copy_features_with_join(self):
        for k, v in self._config.tablecsvlookup.items():
            self.log("Copying: %s -> %s" % (k, v))
            self.log("Out database: %s" % self._out_temp_db)
            sde = self._config.sdeconnection
            fl = r"in_memory\%s" % (self._config.FWPFCname % v.split('.')[-1])
            arcpy.MakeFeatureLayer_management(sde + "/" + v, fl)
            # join to csv
            arcpy.AddJoin_management(fl, self._config.csvsdejoinfield, k, self._config.csvsdejoinfield,
                                     self._config.jointype)
            arcpy.CopyFeatures_management(fl, self._out_temp_db + "/" + self._config.FWPFCname % v.split('.')[-1])

# if __name__ == "__main__":
#     pfwph = PublishFWPServicesHelper()
#     pfwph.publish()
