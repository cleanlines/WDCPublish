import zipfile
from zipfile import ZipFile
import os
from BaseObject import BaseObject


class ZipHelper(BaseObject):
    def __init__(self, archive_name):
        super(ZipHelper, self).__init__()
        self._archive_name = archive_name
        self.log("ZipHelper initialised")

    @property
    def archive(self):
        return self._archive_name

    @archive.setter
    def archive(self,archive_name):
        self._archive_name = archive_name


class ZipArchive(ZipHelper):
    """wrapper for zippping folders / files """
    def __init__(self, archive_name, folder=None, files=[]):
        super(ZipArchive, self).__init__(archive_name)
        a_zipfile = ZipFile(self.archive, 'w', zipfile.ZIP_DEFLATED, True)
        a_zipfile.close()
        self.log("archive created")
        # zip up folder and add files to archive if required
        if folder:
            self.zip_dir(folder)
        if len(files) > 0:
            self.zip_files(files)

    def zip_files(self,files):
        if os.path.exists(self.archive):
            a_zipfile = ZipFile(self.archive, 'a', zipfile.ZIP_DEFLATED, True)
        else:
            a_zipfile = ZipFile(self.archive, 'w', zipfile.ZIP_DEFLATED, True)
        try:
            [a_zipfile.write(e,os.path.split(e)[-1]) for e in files]
        except Exception as err:
            self._config.log.do_message(str(err),"error")
        finally:
            a_zipfile.close()

    def zip_dir(self, dir_to_zip):
        if os.path.exists(self.archive):
            a_zipfile = ZipFile(self.archive, 'a', zipfile.ZIP_DEFLATED, True)
        else:
            a_zipfile = ZipFile(self.archive, 'w', zipfile.ZIP_DEFLATED, True)
        try:
            head, tail = os.path.split(dir_to_zip)
            dir_to_zip_len = len(head.rstrip(os.sep)) + 1
            for dirname, subdirs, files in os.walk(dir_to_zip):
                for filename in files:
                    path = os.path.join(dirname, filename)
                    entry = path[dir_to_zip_len:]
                    a_zipfile.write(path, entry)
        except Exception as err:
            self.errorlog(str(err))
        finally:
            a_zipfile.close()

class UnZipArchive(ZipHelper):
    """wrapper to unzip an archive"""
    def __init__(self,archive_name):
        super(UnZipArchive, self).__init__(archive_name)

    def extract_archive(self,location,archive=None):
        #unzip an archive or cached one
        try:
            with zipfile.ZipFile(self.archive if archive is None else archive, "r") as z:
                self._config.log.do_message("extracting {0} to {1}".format(self.archive,location),"debug")
                z.extractall(location)
                self._config.log.do_message("extract done","debug")
        except Exception,err:
            self._config.log.do_message(err.message,"error")
            raise
