
import pandas as pd
from io import BytesIO
from db import Db

dbs = Db()
class Ingest():
    def __init__(self):
        self.stat = ""


    def get_file(self,user_id, filename, file_data):
        """ Initial file upload storing"""
        # df = pd.read_csv(BytesIO(file_data))
        df = self.load(filename=filename, file_data=file_data)
        try:
            dbs.store_data(filename=filename, file_data=file_data, user_id=user_id)
            self.stat = "Success"
        except Exception as e:
            self.stat = "Failed"
            return {
                "Ingest Error": str(e)
            }


    def load(self, filename, file_data):
            """ file fromat and loading to ETL pipeline"""
            extension = filename.lower().split(".")[-1]
    
            if extension == "csv":
                return pd.read_csv(BytesIO(file_data))
            elif extension in ["xlsx", "xls"]:
                return pd.read_excel(BytesIO(file_data))
            elif extension == "json":
                return pd.read_json(BytesIO(file_data))
            else:
                return ValueError(
                    f"Unsupported format: .{extension}"
                )
