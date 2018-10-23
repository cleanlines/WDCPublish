from BaseObject import BaseObject
from AbstractHelper import AbstractHelper
from TempFileName import TempFileName
import xml.dom.minidom as DOM
import requests
import arcpy
import os
import datetime

'''
We should use Python API for 10.6 so in the meantime will use requests
Since this class wraps all the updates we can change it without changing any of the other code.

'''

class ArcGISOnlineHelper(AbstractHelper, BaseObject):

    def __init__(self):
        super(ArcGISOnlineHelper, self).__init__()
        self.log("ArcGISOnlineHelper initialised")
        self._agol_token = None
        self._cleanups =[]
        self._current_service_name = ""

    def _get_agol_token(self):
        payload = {"request": "gettoken",
                   "Referer": "http://wdc.govt.nz",
                   "username": self._config.user,
                   "password": self._config.password}
        r = requests.post(self._config.agolurl+"/sharing/generateToken?f=json", params=payload,  verify=False) # verify setting for debug - fiddler
        if 'token' in r.json().keys():
            self._agol_token = r.json()['token']

    def _update_agol_file_item(self, item_id, item):
        path, file = os.path.split(item)
        payload = {
            "filename": file,
            "token": self._agol_token,
            "itemType": "file",
            "f": "json",
            "description": self._config.itemdescription+"<br/>Item updated on %s by automated script." % datetime.datetime.now().strftime("%d %B %Y %H:%M:%S")
        }
        # fix referer - put in config
        headers = {"Referer": "http://wdc.govt.nz"}
        files = {'file': (file, open(item, 'rb'), 'application/octet-stream')}
        r = requests.post(self._config.agolurl + "/sharing/rest/content/users/%s/items/%s/update" % (self._config.user, item_id),
                          data=payload, files=files, headers=headers, verify=False)
        self.log(r.text)
        return r.json()
        # TODO: check for success code and wrap error handling

    def _add_agol_file_item(self, item, filetype, keywords):
        self.log("Adding %s" % item)
        path, file = os.path.split(item)
        payload ={
            "title":self._config.itemname,
            "type":filetype,
            # "multipart":"true", # setting this breaks the code below.
            "filename":file,
            "tags": self._config.tagsfwp,
            "token":self._agol_token,
            "itemType":"file",
            "f":"json",
            "typeKeywords":self._config.filekeyworks[keywords],
            "async":"false",
            "description":self._config.itemdescription
        }
        headers={"Referer":"http://wdc.govt.nz"}
        files = {'file': (file, open(item, 'rb'), 'application/octet-stream')}

        r = requests.post(self._config.agolurl + "/sharing/rest/content/users/%s/addItem" % self._config.user, data=payload,files=files, headers=headers, verify=False)
        self.log(r.text)
        return r.json()['id']
        # TODO: check for success code and wrap error handling

    def agol_item_exists(self, name, type):
        search = self._search_for_item(name,type)
        if search['total'] > 0:
            return (True,search['results'][0]['id'])
        return (False,None)

    def _search_for_item(self,name,type):
        payload ={
            "f":"json",
            "token":self._agol_token,
            "q": 'title:"{0}" AND type:"{1}"'.format(name,type)
        }
        r = requests.get(self._config.agolurl+"/sharing/search?f=json", params=payload ,verify=False) #
        return r.json()

    def _publish_file_item(self, filetype, item_id, overwrite="false"):
        # pass through the item id of the object we are publishing from! IE the sd
        self.log("Publishing %s" % item_id)
        payload = {
            "title": self._config.itemname,
            "filetype": filetype,
            "description": self._config.itemdescription,
            "tags": self._config.tagsfwp,
            "itemId": item_id,
            # "multipart":"true", # setting this breaks the code below.
            # "filename": file,
            "buildInitialCache": "false",
            "overwrite":overwrite,
            "token": self._agol_token,
            "f": "json",
            "async": "false"
        }
        headers = {"Referer": "http://wdc.govt.nz"}
        r = requests.post(self._config.agolurl + "/sharing/rest/content/users/%s/publish" % self._config.user, data = payload, headers=headers, verify=False)
        self.log(r.text)
        return r.json()

    def _stage_service_sd(self,map_document):
        temp_sddraft = TempFileName.generate_temporary_file_name("HostedMS.sddraft", split=False)
        path, file = TempFileName.generate_temporary_file_name("", split=True)
        service_definition = os.path.join(path, self._config.itemname + ".sd")
        if os.path.exists(service_definition):
            os.remove(service_definition)
        service = self._config.itemname
        arcpy.mapping.CreateMapSDDraft(map_document, temp_sddraft, service, 'MY_HOSTED_SERVICES', summary="FWP", tags='FWP')
        updated_draft = self._prep_sddraft(temp_sddraft)
        analysis = arcpy.mapping.AnalyzeForSD(updated_draft)
        arcpy.StageService_server(updated_draft, service_definition)
        self.log("Draft analysis:"+str(analysis))
        self._cleanups += [service_definition, temp_sddraft, updated_draft]
        return service_definition

    def _prep_sddraft(self,sddraft):
        doc = DOM.parse(sddraft)
        #  Read the sddraft xml. doc = DOM.parse(sddraft)
        #  Change service from map service to feature service
        typeNames = doc.getElementsByTagName('TypeName')
        for typeName in typeNames:
            if typeName.firstChild.data == "MapServer":
                typeName.firstChild.data = "FeatureServer"
        # #Turn off caching
        configProps = doc.getElementsByTagName('ConfigurationProperties')[0]
        propArray = configProps.firstChild
        propSets = propArray.childNodes
        for propSet in propSets:
            keyValues = propSet.childNodes
            for keyValue in keyValues:
                if keyValue.tagName == 'Key':
                    if keyValue.firstChild.data == "isCached":
                        # turn on caching
                        keyValue.nextSibling.firstChild.data = "false"
        # #Turn on feature access capabilities
        configProps = doc.getElementsByTagName('Info')[0]
        propArray = configProps.firstChild
        propSets = propArray.childNodes
        for propSet in propSets:
            keyValues = propSet.childNodes
        for keyValue in keyValues:
            if keyValue.tagName == 'Key':
                if keyValue.firstChild.data == "WebCapabilities":
                    keyValue.nextSibling.firstChild.data = "Query,Create,Update,Delete,Uploads,Editing"

        updated_sddraft = TempFileName.generate_temporary_file_name("HostedMSNew.sddraft", split=False)
        f = open(updated_sddraft, 'w')
        doc.writexml(f)
        f.close()
        return updated_sddraft

    def publish_map_doc(self, map_doc,service_name="XXX"):
        self._config.itemname = self._config.itemname % service_name
        self._get_agol_token()
        self._current_service_name = service_name
        fs_id = None
        service_definition = self._stage_service_sd(map_doc)
        # now we have the SD we need to add it or update it
        exists, item_id = self.agol_item_exists(self._config.itemname, "Service Definition") #"Existing_sewer","service definition")
        if not exists:
            item_id = self._add_agol_file_item(service_definition, "Service Definition", "sdfilekeywords")
            self.log(self._publish_file_item("serviceDefinition", item_id))
        else:
            self.log(self._update_agol_file_item(item_id, service_definition))
            self.log(self._publish_file_item("serviceDefinition", item_id, "true"))

        # an update doesn't return the item id - only yhr url
        exists, fs_id = self.agol_item_exists(self._config.itemname, "Feature Service")
        return fs_id

    def share(self,item_id, everyone="false", org="false", groups=" "):
        payload = {
            "everyone":everyone,
            "org":org,
            "groups":groups,
            "token": self._agol_token,
            "f": "json",
            "async": "false"
        }
        headers = {"Referer": "http://wdc.govt.nz"}
        r = requests.post(self._config.agolurl + "/sharing/rest/content/users/%s/items/%s/share" % (self._config.user, item_id),
                          data=payload, headers=headers, verify=False)
        self.log(r.text)
        return (r.json()['itemId'], r.json()['notSharedWith'])

    def share_items(self, items, everyone="false", org="false", groups=" "):
        payload = {
            "org":org,
            "everyone":everyone,
            "groups": groups,
            "token": self._agol_token,
            "f": "json",
            "items": items,
            "confirmItemControl": "true"
        }
        headers = {"Referer": "http://wdc.govt.nz"}
        r = requests.post(
            self._config.agolurl + "/sharing/rest/content/users/%s/shareItems" % self._config.user,
            data=payload, headers=headers, verify=False)
        self.log(r.text)
        return r.json()["results"][0]["success"] == "true"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        for file in self._cleanups:
            # just do an import and delete the file using os mmm.
            if arcpy.Exists(file):
                arcpy.Delete_management(file)


# if __name__ == "__main__":
#     agol = ArcGISOnlineHelper()
#     agol.clean_up = False
#     doc = arcpy.mapping.MapDocument("C:/Users/fsh/AppData/Local/Temp/_ags_20181011161311305000npyqdp.mxd")
#     agol.publish_FWP(doc)
