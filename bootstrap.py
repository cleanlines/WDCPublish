from PublishGeodbServicesHelper import PublishGeodbServicesHelper
from PublishFWPServicesHelper import PublishFWPServicesHelper
from BaseLogger import BaseLogger
from SendEmail import SendEmail
from ProcessMonitor import ProcessMonitor
from ReportMissingAssets import ReportMissingAssets
from FileHelper import FileHelper
import datetime


class PublishWrapper(BaseLogger):
    def publish(self):
        with ProcessMonitor() as pm:
            try:
                ReportMissingAssets().execute_validation()
            except Exception as e:
                self.errorlog(e.message)
                SendEmail("ProcessFailure").send_email_with_files([self._logger.log_file], "CSV Validation Failure", "The CSV to GIS validation failed. Please review attached log file. The FWP has not been published")
                pm.log_failure("CSV Validation Failure", e.message)
                return
            try:
                PublishFWPServicesHelper().publish()
            except Exception as e:
                self.errorlog(e.message)
                SendEmail("ProcessFailure").send_email_with_files([self._logger.log_file], "FWP Publishing Failure", "The FWP publish failed. Please review attached log file.")
                pm.log_failure("FWP Publishing Failure", e.message)
                return
            try:
                PublishGeodbServicesHelper().publish()
            except Exception as e:
                self.errorlog(e.message)
                SendEmail("ProcessFailure").send_email_with_files([self._logger.log_file], "Geodb Publishing Failure", "The Geodb publish failed. Please review attached log file.")
                pm.log_failure("Geodb Publishing Failure", e.message)
                return
            pm.log_success("Full Publish Process")
        # once a month clean up the temp directory
        if datetime.datetime.now().day == 17:
            self.log("Time of the month to remove all _ags files.")
            FileHelper().remove_all_temp_files()

if __name__ == '__main__':
    PublishWrapper().publish()
