from BaseObject import BaseObject
from AbstractHelper import AbstractHelper
from TempFileName import TempFileName
import arcpy


class MapDocumentHelper(AbstractHelper, BaseObject):

    def __init__(self, template):
        super(MapDocumentHelper, self).__init__()
        self.__mixin_config(template)
        self._current_map_doc = None
        self.log("MapDocumentHelper initialised")

    def __mixin_config(self, template):
        try:
            [setattr(self, k, v) for k, v in template.items()]
        except Exception:
            raise

    @property
    def current_map_doc(self):
        return self._current_map_doc

    def prepare_map_document(self, data_location):
        self.log("taking temp geodb and repointing temp template mxd")
        self.log("{0},{1}".format(map,data_location))
        if hasattr(self, "map") and arcpy.Exists(self.map):
            try:
                a_map = arcpy.mapping.MapDocument(self.map)
                temp_map = TempFileName.generate_temporary_file_name(".mxd", split=False)
                a_map.saveACopy(temp_map)
                del a_map
                temp_map_doc = arcpy.mapping.MapDocument(temp_map)
                # fix broken datas sources and return
                df = arcpy.mapping.ListDataFrames(temp_map_doc)[0]
                for lyr in arcpy.mapping.ListLayers(temp_map_doc, "", df):
                    # the below only works if the layers are called the same thing
                    if lyr.name in self.layertofclookup.keys():
                        self.log("Repointing data: {0},{1},{2},{3}".format(data_location,self.workspacetype,lyr.name, self.layertofclookup[lyr.name]))
                        lyr.replaceDataSource(data_location,self.workspacetype,self.layertofclookup[lyr.name])
                # this will work ok if we use the Zorko file geodb where the fc names match. But we can't be sure of this so should really use the lookup.
                # some_lyr = arcpy.mapping.ListLayers(temp_map_doc, "", df)[0]
                # temp_map_doc.findAndReplaceWorkspacePaths(some_lyr.workspacePath,data_location)
                temp_map_doc.save()
                self._current_map_doc = temp_map_doc
                self.log("Publishing doc for FWP saved out")
            except Exception:
                raise

    def _delete_current_map_document(self):
        if self._current_map_doc and self._clean_up:
            try:
                self.log("Cleaning up publishing map doc %s" % str(self._current_map_doc.filePath))
                # close any connections to the map
                file_path = self._current_map_doc.filePath
                del self._current_map_doc
                arcpy.Delete_management(file_path )
            except Exception as e:
                self.errorlog(e.message)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._delete_current_map_document()
