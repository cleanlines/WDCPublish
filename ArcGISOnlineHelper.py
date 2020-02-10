from BaseObject import BaseObject
from AbstractHelper import AbstractHelper
from TempFileName import TempFileName
import xml.dom.minidom as DOM
import requests
import arcpy
import os
import datetime
import math
import subprocess
import json
import urllib

'''
We should use Python API for 10.6 so in the meantime will use requests
Since this class wraps all the updates we can change it without changing any of the other code.

'''

class ArcGISOnlineHelper(AbstractHelper, BaseObject):

    def __init__(self):#tick
        super(ArcGISOnlineHelper, self).__init__()
        self.log("ArcGISOnlineHelper initialised")
        self._agol_token = None
        self._cleanups = []
        self._current_service_name = ""

    def _get_agol_token(self): #tick
        #payload = "request=gettoken\"&\"Referer=http://wdc.govt.nz\"&\"username="+self._config.user+"\"&\"password="+self._config.password
        payload = "request=gettoken&Referer=http://wdc.govt.nz&username=" + self._config.user + "&password=" + self._config.password
        result = self.run_via_powershell("https://wdc.maps.arcgis.com/sharing/generateToken?f=json", payload,"post")
        if result:
            jsonobj = json.loads(result)
            if 'token' in jsonobj:
                self._agol_token = jsonobj['token']
        else:
            raise Exception("Cannot acquire arcgis online token")

    def _update_agol_file_item(self, item_id, item): #tick
        path, file = os.path.split(item)
        payload = {
            "filename": file,
            "token": self._agol_token,
            "itemType": "file",
            "f": "json",
            "description": self._config.itemdescription+"<br/>Item updated on %s by automated script." % datetime.datetime.now().strftime("%d %B %Y %H:%M:%S")
        }
        payload = "^".join(["{0}={1}".format(k, v) for k, v in payload.items()])
        #payload = "filename={0}^token={1}^itemType=file^f=json^{2}".format(file,self._agol_token,urllib.urlencode({"description":self._config.itemdescription+"<br/>Item updated on %s by automated script." % datetime.datetime.now().strftime("%d %B %Y %H:%M:%S")}))
        url = self._config.agolurl + "/sharing/rest/content/users/%s/items/%s/update" % (self._config.user, item_id)
        file = item
        result = self.upload_via_powershell(url,payload,file)
        if result:
            jsonobj = json.loads(result)
            return jsonobj

        # fix referer - put in config
        # item is the sd file, file is the name
        #headers = {"Referer": "http://wdc.govt.nz"}
        # files = {'file': (file, open(item, 'rb'), 'application/octet-stream')}
        # r = requests.post(self._config.agolurl + "/sharing/rest/content/users/%s/items/%s/update" % (self._config.user, item_id), data=payload, files=files, headers=headers, verify=False)
        # self.log(r.text)
        # return r.json()
        # TODO: check for success code and wrap error handling

    def _add_agol_file_item(self, item, filetype, keywords,title=None):#tick
        self.log("Adding %s" % item)
        path, file = os.path.split(item)
        title = self._config.itemname if title is None else title
        payload ={
            "title":title,
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
        #payload = "title={0}^type={1}^filename={2}^tags={3}^token={4}^itemType=file^f=json^typeKeywords={5}^async=false^description={6}".format(title,filetype,file,self._config.tagsfwp,self._agol_token,self._config.filekeyworks[keywords],self._config.itemdescription)
        payload = "^".join(["{0}={1}".format(k, v) for k, v in payload.items()])
        url = self._config.agolurl + "/sharing/rest/content/users/%s/addItem" % self._config.user
        file = item
        result = self.upload_via_powershell(url, payload, file)
        if result:
            jsonobj = json.loads(result)
            return jsonobj['id']

        # #headers={"Referer":"http://wdc.govt.nz"}
        # files = {'file': (file, open(item, 'rb'), 'application/octet-stream')}
        #
        # r = requests.post(self._config.agolurl + "/sharing/rest/content/users/%s/addItem" % self._config.user, data=payload,files=files, headers=headers, verify=False)
        # self.log(r.text)
        #return r.json()['id']
        # TODO: check for success code and wrap error handling

    def agol_item_exists(self, name, type): #tick
        search = self._search_for_item(name,type)
        if search['total'] > 0:
            return (True,search['results'][0]['id'])
        return (False,None)

    def _search_for_item(self,name,type):#tick
        payload = "f=json^token="+self._agol_token+"^q="+"title:\"{0}\" AND type:\"{1}\"".format(name,type)
        url = self._config.agolurl+"/sharing/search"
        result = self.run_via_powershell(url, payload, "get")
        if result:
            jsonobj = json.loads(result)
            return jsonobj
        else:
            return {}
        # r = requests.get(self._config.agolurl+"/sharing/search?f=json", params=payload ,verify=False) #
        # return r.json()

    def _publish_file_item(self, filetype, item_id, overwrite="false",title=None, publish_params=None): #tick
        # pass through the item id of the object we are publishing from! IE the sd
        self.log("Publishing %s" % item_id)
        if title:
            try:
                a_title = self._config.itemname % title
            except Exception as e:
                self.errorlog(e.message)
        else:
            a_title = self._config.itemname

        payload = {
            "title": a_title,
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
        if publish_params:
            payload.update(publish_params)

        payload = "&".join(["{0}={1}".format(k,v) for k,v in payload.items()])
        url = self._config.agolurl + "/sharing/rest/content/users/%s/publish" % self._config.user
        result = self.run_via_powershell(url, payload, "post")
        if result:
            jsonobj = json.loads(result)
            return jsonobj
        #headers = {"Referer": "http://wdc.govt.nz"}
        # r = requests.post(self._config.agolurl + "/sharing/rest/content/users/%s/publish" % self._config.user, data = payload, headers=headers, verify=False)
        # self.log(r.text)
        # return r.json()

    def _stage_service_sd(self,map_document): #tick
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

    def _prep_sddraft(self,sddraft): #tick
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

    def publish_file_item(self,item_name, item_type,item_file_type, file_item,keywords,publish_params=None): #tick
        self._get_agol_token()
        exists, item_id = self.agol_item_exists(item_name, item_type)

        if not exists:
            item_id = self._add_agol_file_item(file_item, item_type, keywords,item_name)
            publish_json = self._publish_file_item(item_file_type, item_id,title=item_name,publish_params=publish_params)
            self.log(publish_json)
        else:
            self.log(self._update_agol_file_item(item_id, file_item))
            publish_json = self._publish_file_item(item_file_type, item_id, overwrite="true",title=item_name,publish_params=publish_params)
            self.log(publish_json)

        if 'services' in publish_json:
            if 'serviceItemId' in publish_json['services'][0]:
                # we are expecting one service back
                return (item_id, publish_json['services'][0]['serviceItemId'])
        else:
            return (item_id, None)

    def publish_map_doc(self, map_doc,service_name="XXX"): #tick
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

    def share(self,item_id, everyone="false", org="false", groups=" "): #tick
        # payload = {
        #     "everyone":everyone,
        #     "org":org,
        #     "groups":groups,
        #     "token": self._agol_token,
        #     "f": "json",
        #     "async": "false"
        # }
        payload = "everyone="+everyone+"&org="+org+"&groups="+groups+"&token="+self._agol_token+"&f=json&async=false"
        url = self._config.agolurl + "/sharing/rest/content/users/%s/items/%s/share" % (self._config.user, item_id)
        result = self.run_via_powershell(url, payload, "post")
        #headers = {"Referer": "http://wdc.govt.nz"}
        #r = requests.post(self._config.agolurl + "/sharing/rest/content/users/%s/items/%s/share" % (self._config.user, item_id), data=payload, headers=headers, verify=False)
        #self.log(r.text)
        if result:
            jsonobj = json.loads(result)
            return jsonobj['itemId'], jsonobj['notSharedWith']

    def share_items(self, items, everyone="false", org="false", groups=" "):#tick
        # payload = {
        #     "org":org,
        #     "everyone":everyone,
        #     "groups": groups,
        #     "token": self._agol_token,
        #     "f": "json",
        #     "items": items,
        #     "confirmItemControl": "true"
        # }
        payload = "org="+org+"&everyone="+everyone+"&groups="+groups+"&token="+ self._agol_token+"&f=json&items="+items+"&confirmItemControl=true"
        url = self._config.agolurl + "/sharing/rest/content/users/%s/shareItems" % self._config.user
        result = self.run_via_powershell(url, payload, "post")
        if result:
            jsonobj = json.loads(result)
            return jsonobj["results"][0]["success"] == "true"

        #headers = {"Referer": "http://wdc.govt.nz"}
        # r = requests.post(
        #     self._config.agolurl + "/sharing/rest/content/users/%s/shareItems" % self._config.user,
        #     data=payload, headers=headers, verify=False)
        # self.log(r.text)
        #return r.json()["results"][0]["success"] == "true"

    # adapted from https://community.esri.com/docs/DOC-6496-download-arcgis-online-feature-service-or-arcgis-server-featuremap-service
    # doesn't download attachments though the original code does
    def download_hosted_feature_service_layer(self, hosted_feature_layer, temp_db, output_fc): #tick
        # note this doesn't do attachments for this project
        self._get_agol_token()
        base_hfl_url = hosted_feature_layer + "/query"

        from arcpy import env
        env.overwriteOutput = 1
        wksp = env.workspace
        env.workspace = temp_db

        # payload = {'where': '1=1',
        #            'returnIdsOnly': 'true',
        #            'f': 'json',
        #            'token': self._agol_token}

        payload = "where=1%3D1&returnIdsOnly=true&f=json&token="+self._agol_token
        response = self.run_via_powershell(base_hfl_url, payload, "post")
        #response = requests.post(base_hfl_url, data=payload, verify=False)
        if response:
            data = json.loads(response)
        #data = response.json()
        try:
            data['objectIds'].sort()
        except Exception as e:
            self.log(str(data))
            self.errorlog(e.message)
            raise

        iteration = int(data['objectIds'][-1])
        minOID = int(data['objectIds'][0]) - 1
        OID = data['objectIdFieldName']
        y = minOID
        x = minOID + 1000
        firstTime = 'True'
        newIteration = (math.ceil(iteration / 1000.0) * 1000)
        while y < newIteration:
            if x > int(newIteration):
                x = int(newIteration)

            where = OID + '>' + str(y) + 'AND ' + OID + '<=' + str(x)
            self.log(where)
            fields ='*'
            query = "?where={}&outFields={}&returnGeometry=true&f=json&token={}".format(where, fields, self._agol_token)
            count_query = query + "&returnCountOnly=true"
            # get a count - 0 counts bomb the append and the JSON is malformed.
            count_result = self.run_via_powershell(base_hfl_url, count_query[1:], "post")
            count_data = json.loads(count_result)
            if "count" not in count_data:
                break
            elif count_data["count"] == 0:
                break

            fsURL = base_hfl_url + query
            fs = arcpy.FeatureSet()
            fs.load(fsURL)

            if firstTime == 'True':
                self.log('Copying features with ObjectIDs from ' + str(y) + ' to ' + str(x))
                arcpy.FeatureClassToFeatureClass_conversion(fs, temp_db ,output_fc)
                firstTime = 'False'
            else:
                self.log('Appending features with ObjectIDs from ' + str(y) + ' to ' + str(x))
                arcpy.Append_management(fs, output_fc, "NO_TEST")

            x += 1000
            y += 1000

        env.workspace = wksp

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        for file in self._cleanups:
            # just do an import and delete the file using os mmm.
            if arcpy.Exists(file):
                arcpy.Delete_management(file)

    def run_via_powershell(self, url, payload, method='get'):
        powerShellPath = r'powershell.exe'
        if method == 'post':
            powerShellCmd = self._config.powershellpost
        else:
            powerShellCmd = self._config.powershellget
        p = subprocess.Popen([powerShellPath, '-ExecutionPolicy', 'Unrestricted', '-File', powerShellCmd, url, payload], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = p.communicate()
        rc = p.returncode
        self.log("Return code given to Python script is: " + str(rc))
        self.log("stdout:\n\n" + str(output))
        self.log("stderr: " + str(error))
        return str(output)

    def upload_via_powershell(self, url, payload, file):
        powerShellPath = r'powershell.exe'
        powerShellCmd = self._config.powershellupload
        p = subprocess.Popen([powerShellPath, '-ExecutionPolicy', 'Unrestricted', '-File', powerShellCmd, url, payload, file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = p.communicate()
        rc = p.returncode
        self.log("Return code given to Python script is: " + str(rc))
        self.log("stdout:\n\n" + str(output))
        self.log("stderr: " + str(error))
        return str(output)

# if __name__ == "__main__":
#     agol = ArcGISOnlineHelper()
#     agol.clean_up = False
#     doc = arcpy.mapping.MapDocument("C:/Users/fsh/AppData/Local/Temp/_ags_20181011161311305000npyqdp.mxd")
#     agol.publish_FWP(doc)
