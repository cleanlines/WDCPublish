from BaseObject import BaseObject
from AbstractPublishHelper import AbstractPublishHelper
import shelve
from TempFileName import TempFileName
from FileGeodatabaseHelper import FileGeodatabaseHelper
from FileHelper import FileHelper
from ArcGISOnlineHelper import ArcGISOnlineHelper
from ProximityLayerCreator import ProximityLayerCreator
import ZipArchive
import json


class PublishRAMMHelper(BaseObject, AbstractPublishHelper):

    # stub class to add an additional publisher once the roading stuff is done.
    def __init__(self):
        super(PublishRAMMHelper, self).__init__()
        self.log("PublishRAMMHelper initialised")

    def publish(self):
        #get the latest RAMM data - add to file geodatabase and run model
        # TODO put the shelf into common config
        s = None
        try:
            s = shelve.open("%s%s%s" % (TempFileName.get_temp_directory(), "/", self._config.shelf))
        except:
            raise Exception("Cannot publish RAMM FWP due to missing data")

        file_geodb = None
        if 'fwpgeodb' in s:
            file_geodb = s['fwpgeodb']
        s.close()

        if file_geodb:
            with FileGeodatabaseHelper() as file_geodb_helper:
                file_geodb_helper.clean_up = False # debug
                file_geodb_helper.current_file_geodb = file_geodb
                print file_geodb
                with ArcGISOnlineHelper() as agol_helper:
                    agol_helper.download_hosted_feature_service_layer(self._config.rammfwpdata, file_geodb, self._config.output_fc)

                with ProximityLayerCreator(file_geodb) as proximity_creator:
                    new_file_geodb = proximity_creator.create_proximity_layer(self._config.output_fc)

                    zip_file = TempFileName.generate_temporary_file_name(".zip")
                    ZipArchive.ZipArchive(zip_file, new_file_geodb)
                    publishparams = json.dumps(self._config.publishparams)
                    item_id, service_id = agol_helper.publish_file_item("WDC_RAMM_FWP", "File Geodatabase","fileGeodatabase ", zip_file, "filegeodbkeywords", publish_params={"publishParameters":publishparams})
    # dont pass through a dictonary - pass through a str for the vals - use eval maybe to ensure quotes!
                    # depending on the group type we may have to do one or the other - so I'm just going to do both
                    if service_id:
                        agol_helper.share_items("%s,%s" % (item_id, service_id), groups=self._config.fwpgroup)
                    else:
                        agol_helper.share(item_id, groups=self._config.fwpgroup)

            FileHelper().delete_file("%s%s%s" % (TempFileName.get_temp_directory(), "/", self._config.shelf))
        else:
            raise Exception("Cannot publish RAMM FWP due to missing data - missing key in shelf")



