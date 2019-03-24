
from BaseObject import BaseObject
from FileGeodatabaseHelper import FileGeodatabaseHelper
import arcpy


# TODO: the parent class should inject the config - it is creating the ramm layer so should tell this class what fields to use etc.
class ProximityLayerCreator(BaseObject):

    def __init__(self,file_geodb):
        super(ProximityLayerCreator,self).__init__()
        self._file_geodb = file_geodb
        self.log("ProximityLayerCreator initialised")

    def create_proximity_layer(self,ramm_fc_name):
        self.log("Creating Proximity Layer")
        # we are using the current file geodb - make the layer copy the final layer into new filegeodb and publish
        sewer = "{0}/{1}".format(self._file_geodb,self._config.sewer)
        water ="{0}/{1}".format(self._file_geodb,self._config.water)
        storm ="{0}/{1}".format(self._file_geodb,self._config.storm)
        ramm ="{0}/{1}".format(self._file_geodb,ramm_fc_name)

        try:
            self.add_fields([sewer, water, storm])
            self._create_3_waters(self._file_geodb, [sewer, water, storm])
            # now we have to get the RAMM data by year, 1 up and 1 down, find the associated water features
            # get all years and group RAMM layers to year blocks, then split year and get 3 waters features based on year
            break_down = self._process_ramm_data("%s/%s" % (self._file_geodb, ramm_fc_name))
            arcpy.env.overwriteOutput = True  # make sure any existing temp layers don't trip us up
            for k, v in break_down.items():
                ramm_layer = "ramm_filtered_lyr"
                waters_layer = "waters_filtered_lyr"
                arcpy.MakeFeatureLayer_management(ramm, ramm_layer, "{0} = '{1}'".format(self._config.rammyear, k))
                arcpy.MakeFeatureLayer_management("%s/%s" % (self._file_geodb, self._config.threewaters_fc_name), waters_layer, v)
                self._process_spatial_selection(ramm_layer, waters_layer, k)
            # finish the process by doing the 'double' dissolve
            publish_filegeodb = FileGeodatabaseHelper().new_file_geodatabase()
            arcpy.Dissolve_management("%s/%s" % (self._file_geodb, self._config.proximity_fc_name), "%s/%s_dissolve" % (self._file_geodb, self._config.proximity_fc_name), "AssetId;fw_year", "AssetId COUNT", "MULTI_PART", "UNSPLIT_LINES")
            arcpy.Dissolve_management("%s/%s_dissolve" % (self._file_geodb, self._config.proximity_fc_name), "%s/%s_dissolve_2" % (self._file_geodb, self._config.proximity_fc_name), "AssetId;fw_year", "COUNT_AssetId SUM", "MULTI_PART", "DISSOLVE_LINES")
            arcpy.FeatureToPoint_management("%s/%s_dissolve_2" % (self._file_geodb, self._config.proximity_fc_name), "%s/%s" % (publish_filegeodb,self._config.proximity_point_fc_name), "INSIDE")
            return publish_filegeodb
        except Exception as e:
            self.errorlog(e.message)
            raise

    def _process_spatial_selection(self,r_lyr,w_lyr,ramm_year):
        # we are just following the process as per model builder
        asset_ids = []
        with arcpy.da.SearchCursor(r_lyr, self._config.rammassetid) as search_cursor:
            for row in search_cursor:
                if row[0] not in asset_ids:
                    asset_ids.append(row[0])
        for an_id in asset_ids:
            temp_lyr = "ramm_single_feat_lyr"
            arcpy.MakeFeatureLayer_management(r_lyr, temp_lyr, "{0} = '{1}'".format(self._config.rammassetid, an_id))
            arcpy.SelectLayerByLocation_management(w_lyr, "INTERSECT", temp_lyr, 20)
            self._add_to_proximity_layer(w_lyr, an_id,ramm_year)
            arcpy.Delete_management(temp_lyr)
        arcpy.Delete_management(r_lyr)
        arcpy.Delete_management(w_lyr)

    def _add_to_proximity_layer(self, a_lyr, an_id, ramm_year):
        insert_fields = [k for k in self._config.proximity_staging.keys()]
        # these are the old 10.1 cursors - need to be updated @ 10.6.1
        cursor = arcpy.da.InsertCursor("%s/%s" % (self._file_geodb, self._config.proximity_fc_name), insert_fields + ["SHAPE@"])
        search_fields = [k for k in self._config.threewaters.keys()]
        with arcpy.da.SearchCursor(a_lyr, search_fields + ["SHAPE@"]) as search_cursor:
            for row in search_cursor:
                # add the additional fields to the row !!! HERE HERE HERE
                ins_row = list(row)
                ins_row.insert(0, an_id)
                ins_row.insert(2, ramm_year)
                try:
                    cursor.insertRow(ins_row)
                except Exception as e:
                    self.errorlog(e.message)
        del cursor

    def _process_ramm_data(self, ramm_layer):
        years = {}
        with arcpy.da.SearchCursor(ramm_layer, self._config.rammyear) as search_cursor:
            for row in search_cursor:
                if row[0] not in years.keys():
                    years[row[0]] = "Year IN ({0})".format(self._year_string(row[0]))
        return years

    def _year_string(self,year_string):
        up, down = [int(i) for i in year_string.split("/")]
        return ",".join(str(i) for i in [up-1, up, 2000+down, 2001+down])

    def add_fields(self,some_fcs):
        for fc in some_fcs:
            try:
                arcpy.AddField_management(fc, self._config.assetfield, "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
                arcpy.CalculateField_management(fc ,self._config.assetfield, "'%s'" % fc.split('/')[-1], "PYTHON")
            except Exception as e:
                self.log(e.message)

    def _create_fc_layer(self, file_geodb, fc_name):
        try:
            arcpy.CreateFeatureclass_management(file_geodb,fc_name,"POLYLINE","", "DISABLED", "DISABLED","PROJCS['NZGD_2000_New_Zealand_Transverse_Mercator',GEOGCS['GCS_NZGD_2000',DATUM['D_NZGD_2000',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',1600000.0],PARAMETER['False_Northing',10000000.0],PARAMETER['Central_Meridian',173.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]];-4020900 1900 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision")
        except Exception as e:
            # feature class already exists.
            self.errorlog(e.message)
            try:
                arcpy.TruncateTable_management("%s/%s" % (file_geodb, fc_name))
            except Exception as e:
                self.errorlog(e.message)
        for k, v in getattr(self._config, fc_name).items():
            try:
                arcpy.AddField_management("%s/%s" % (file_geodb, fc_name), k, v)
            except Exception as e:
                self.errorlog(e.message)
                raise

    def _create_3_waters(self,file_geodb, fcs):
        self._create_fc_layer(file_geodb, self._config.threewaters_fc_name)
        self._create_fc_layer(file_geodb, self._config.proximity_fc_name)
        # load data - this will need to be updated for 10.6.1
        insert_fields = [k for k in self._config.threewaters.keys()]
        # these are the old 10.1 cursors - need to be updated @ 10.6.1
        cursor = arcpy.da.InsertCursor("%s/%s" % (file_geodb, self._config.threewaters_fc_name), insert_fields+["SHAPE@"])
        try:
            for fc in fcs:
                self.log(fc)
                field_names = getattr(self._config, fc.split('/')[-1])
                self.log(str(field_names))
                # the fields don't actually reflect the alias - esp for the joined CSV - we need to get the actual field names
                fds = arcpy.ListFields(fc)
                for desc_fd in fds:
                    if desc_fd.aliasName in field_names:
                        self.log(desc_fd.aliasName+","+desc_fd.name)
                        field_names[field_names.index(desc_fd.aliasName)] = desc_fd.name
                self.log(str(field_names))
                with arcpy.da.SearchCursor(fc, field_names) as search_cursor:
                    for row in search_cursor:
                        cursor.insertRow(row)
        except Exception as e:
            self.errorlog(e.message)
            del cursor
            raise

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


# if __name__ == '__main__':
#     try:
#         ProximityLayerCreator("C:/Users/fsh/AppData/Local/Temp/_ags_20181130114443421000cebycw.gdb").create_proximity_layer("RAMM_FW")
#     except:
#         pass