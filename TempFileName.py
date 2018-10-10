import datetime
import tempfile


class TempFileName(object):

    @staticmethod
    def generate_temporary_file_name():
        f = tempfile.NamedTemporaryFile(
            prefix="_ags_{0}".format(datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")), suffix=".log")
        file_name = f.name
        f.close()
        return file_name

# bada bing bada boom