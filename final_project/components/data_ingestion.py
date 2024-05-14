import os
import sys

from pandas import DataFrame
from sklearn.model_selection import train_test_split

from final_project.entity.config_entity import DataIngestionConfig
from final_project.entity.artifact_entity import DataIngestionArtifacts


from final_project.exception import final_except
from final_project.logger import logging


from final_project.database_access.db_extract import VisaData

class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig = DataIngestionConfig()):
        '''
        
        '''
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise final_except(e,sys)
        
        def export_data_into_feature_store(self)-> DataFrame:
            '''
            exports data from database and returns dataframe
            '''
            try:
                logging.info("export_data_into_feature_store")
                visa_data = VisaData()
                dataframe = visa_data.export_collection_as_df(collection_name=self.data_ingestion_config.collection_name)
                logging.info("shape of dataframe: {dataframe.shape}")
                feature_store_file_path = self.data_ingestion_config.feature_store_file_path
                dir_path = os.path.dirname(feature_store_file_path)
                os.makedirs(dir_path, exist_ok=True)
                logging.info(f"Saving exported data into feature store file path: {feature_store_file_path}")
                dataframe.to_csv(feature_store_file_path, index=False, header=True)
                return dataframe
            except Exception as e:
                raise final_except(e,sys)
        def split_data_as_train_test(self, dataframe: DataFrame)-> None:
            '''
            split data into train and test with specified ratio
            '''

            logging.info("Entered split_data method of DataIngestion Class")

            try:
                train_set, test_set = train_test_split(dataframe, test_size = data_ingestion_config.train_test_split_ration)
                logging.info("Performed train test split")
                logging.ingo("Exited split_data method of DataIngestion Class")

                dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
                os.makedirs(dir_path, exist_ok=True)

                logging.info("Exporting training and test file path")

                train_set.to_csv(self.data_ingestion_config.training_file_path, index = False, header = True)
                test_set.to_csv(self.data_ingestion_config.testing_file_path, index = False, header = True)

                logging.info("Exported the train test file.")
            except Exception as e:
                raise final_except(e,sys)
            
        def initiate_data_ingestion(self) -> DataIngestionArtifacts:
            '''
            initiate the data ingestion components of the training pipeline
            
            train and test set are returned as artifacts of the data ingestion components
            '''

            logging.info("Entered the initiate data ingestion method of DataIngestion Class")

            try:
                dataframe = self.export_data_info_feature_store()
                logging.info("Got the data from database")

                self.split_data_as_train_set(dataframe)

                logging.info("Performed the train and test split")

                logging.info("Exited initiate_data_ingestion method")

                data_ingestion_artifact = DataIngestionArtifacts(trained_file_path=self.data_ingestion_config.training_file_path, 
                                                                 test_file_path = self.data_ingestion_config.testing_file_path)
                logging.info(f"Data Ingestion artifact: {data_ingestion_artifact}")

                return data_ingestion_artifact
            except Exception as e:
                raise final_except(e, sys)
                

