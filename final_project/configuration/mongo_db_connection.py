import sys
import pymongo
from pymongo import MongoClient

from final_project.exception import final_except
from final_project.logger import logging

import os
from final_project.constants import DATABASE_NAME, MONGODB_URL

class MongoDB:

    '''
    Class Name: export data into feature store
    Description: desport data from MongoDV and store as dataframe

    Output: connection to the base in Mongo 
    On Failure: raise exveption
    '''

    client = None
    

    def __init__(self, database_name = DATABASE_NAME) -> None:
        try:
            if MongoDB.client is None:
                mongo_db_url = os.getenv('MONGODB_DB_URL')
                if mongo_db_url is None:
                    raise Exception(f"Environment key: {MONGODB_URL} is read.")
                MongoDB.client = pymongo.MongoClient(mongo_db_url)
                
            self.client = MongoDB.client
            self.database = self.client[database_name]
            self.database_name = database_name
            logging.info('MongoDB connection successful')

        except Exception as e:
            raise final_except(e,sys)