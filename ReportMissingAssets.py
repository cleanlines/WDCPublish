from BaseObject import BaseObject
import arcpy
import csv
from SendEmail import SendEmail
from CSVHelper import CSVHelper
from AbstractHelper import AbstractHelper


class ReportMissingAssets(AbstractHelper, BaseObject):

    def __init__(self):
        super(ReportMissingAssets,self).__init__()
        self.log("ReportMissing Assets initialised")

    def _load_sde_compkeys(self):
        if hasattr(self._config,"sdeconnection") and hasattr(self._config,"tablecsvlookup"):
            sde = arcpy.ArcSDESQLExecute(self._config.sdeconnection)
            print sde
            try:
                for k,v in self._config.tablecsvlookup.items():
                    self.log("Processing:{0}|{1}".format(k,v))
                    if not hasattr(self._config,"selectfields"):
                        raise Exception("Expected configuration missing: selectfields")
                    sql = "select {0} from {1}".format(self._config.selectfields,v)
                    print sql
                    sde_return = sde.execute(sql)
                    # debug
                    if isinstance(sde_return,list):
                        if len(sde_return) > 0:
                            loaded_comp_keys = [ck[0] for ck in sde_return]
                            setattr(self,v,loaded_comp_keys)
            except Exception as e:
                self.errorlog(e.message)
            finally:
                del sde
        else:
            raise Exception("Expected configuration missing: sdeconnection, tablecsvlookup")

    def _validate_sde_csv(self):
        # DEBUG raise Exception("A very bad error occurred here!")
        try: # this should be moved to the CVS helper
            for k, v in self._config.tablecsvlookup.items():
                if not hasattr(self,v):
                    raise Exception("No cached compkeys for %s" % v)
                with open(k,'rb') as csv_file:
                    delim = self._config.csvdelim if hasattr(self._config,"csvdelim") else ","
                    asset_reader = csv.reader(csv_file,delimiter=str(delim))
                    bad_rows = []
                    for row in asset_reader:
                        # print row
                        if not self._validate_compkey(row,v):
                            bad_rows.append(row)

                    if len(bad_rows) > 1:
                        # write out csv snd send
                        self._notify_bad_rows(bad_rows, k, v)
        except Exception:
            # at this point I'm not interested in any particular exceptions just rethrow
            raise

    def _notify_bad_rows(self,bad_rows,csv_lookup_key,email_lookup_key):
        try:
            bad_csv = CSVHelper(base_csv_file=csv_lookup_key).write_rows_to_csv(bad_rows)
            SendEmail(email_lookup_key).send_email_with_files([bad_csv],"Not in GIS Report","Please find attached records that have not been found in the GIS - no records with matching COMPKEY.")
        except Exception as e:
            self.log("Failed to send email for %s" % csv_lookup_key)
            self.errorlog(e.message)

    def _validate_compkey(self,row,v):
        compkey_idx = self._config.csvcompkeyindex if hasattr(self._config, "csvcompkeyindex") else 0
        # since this is a csv we should expect the vals to be strings
        try:
            key = int(row[compkey_idx])
            return key in getattr(self, v, [])
        except Exception as e:
            self.errorlog(e.message)

    def execute_validation(self):
        try:
            self._load_sde_compkeys()
            self._validate_sde_csv()
            self.log("GIS records / FWP validation done.")
            self.delete_csvs()
        except Exception:
            raise

    def delete_csvs(self):
        CSVHelper().clean_up_temp_csvs()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.delete_csvs()

# if __name__ == "__main__":
#     rma = ReportMissingAssets()
#     rma.execute_validation()
