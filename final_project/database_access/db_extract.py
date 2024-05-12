from final_project.configuration.mongo_db_connection import MongoDB
from final_project.constants import DATABASE_NAME
from final_project.exception import final_except
import pandas as pd
import sys
from typing import Optional
import numpy as np



class VisaData: 
    '''
    This class will be used to extract mongo data into a dataframe
    '''

    def __init__(self):
        '''
        
        '''
        try:
            self.mongo_db = MongoDB(database_name=DATABASE_NAME)
        except Exception as e:
            raise final_except(e, sys)
        
    def export_collection_as_df(self, collection_name: str, database_name:Optional[str]=None) -> pd.DataFrame:
        try:
            '''
            Export collection and return pd.Dataframe
            '''
            if database_name is None:
                collection = self.mongo_client[database_name][collection_name]
            else:
                collection = self.mongo_client[database_name][collection_name]

            df = pd.DataFrame(list(collection.find()))
            if "_id" in df.columns.to_list():
                df=df.drop(columns = ["_id"], axis = 1)
            df.replace({"na":np.nan}, inplace =True)
            return df
        except Exception as e:
            raise final_except(e,sys)
    


