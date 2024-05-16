import json
import sys
from evidently.model_profile import Profile
from evidently.model_profile.sections import DataDriftProfileSection

from pandas import DataFrame

from final_project.exception import final_except
from final_project.logger import logging
from final_project.utils.main_utils import read_yaml_file, write_yaml_file
from final_project.entity.artifact_entity import DataIngestionArtifacts, DataValidationArtifacts
from final_project.entity.config_entity import DataValidationConfig
from final_project.constants import SCHEMA_FILE_PATH

class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifacts, data_validation_config: DataValidationConfig):
        '''
        take data_ingestion_artifact output and validata data validation configuration
        '''

        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self._schema_config = read_yaml_file(file_path=SCHEMA_FILE_PATH)

        except Exception as e:
            raise final_except(e,sys)
        
    def validate_number_of_columns(self, datafame:DataFrame) -> bool:
        '''
        validate the number of columns in the dataframe
        '''

        try:
            status = len(datafame.columns) == len(self._schema_config['columns'])
            logging.info(f"The shape of the data is: [{status}]")
            return status
        except Exception as e:
            raise final_except(e,sys)
        
    def does_column_exist(self, df: DataFrame) -> bool:
        '''
        check if the columns exist in the dataframe
         '''
        try:
            dataframe_columns = df.columns
            missing_numerical_columns = []
            missing_categorical_columns = []
            for column in self._schema_config['numerical_columns']:                    
                if column not in dataframe_columns:
                    missing_numerical_columns.append(column)
                    
                if len(missing_numerical_columns) > 0:
                    logging.info(f"The missing numerical columns are: {missing_numerical_columns}")

            for column in self._schema_config['categorical_columns']:
                if column not in dataframe_columns:
                    missing_categorical_columns.append(column)
                    
                if len(missing_categorical_columns) > 0:
                    logging.info(f"The missing categorical columns are: {missing_categorical_columns}")

            return False if len(missing_categorical_columns) > 0 or len(missing_numerical_columns) > 0 else True
            
        except Exception as e:
            raise final_except(e,sys)
            
        @staticmethod
        def read_data(file_path) -> DataFrame:
            try:
                return pd.read_csv(file_path)
            except Exception as e:
                raise final_except(e,sys)
                
    def detect_dataset_drift(self, reference_df: DataFrame, current_df: DataFrame ) -> bool:
        '''
        this method validates if drift is detected
        '''

        try: 
            data_drift_profile = Profile(sections = [DataDriftProfileSection()])
            data_drift_profile.calculate(reference_df, current_df)

            report = data_drift_profile.json()
            json_report = json.loads(report)

            write_yaml_file(file_path=self.data_validation_config.drift_report, content = json_report)

            n_features = json_report['data_drift']['data']['metrics']['n_features']

            n_drifted_features = json_report['data_drift']['data']['metrics']['dataset_drift']

            logging.info(f"{n_drifted_features}/{n_features} drift detected")
            drift_status = json_report['data_drift']['data']['metrics']['dataset_drift']

            return drift_status
        except Exception as e:
            raise final_except(e,sys)
                
    def initiate_data_validation(self) -> DataValidationArtifacts:
        '''
        initiates the data validation component for the pipeline
        returns a bool on validation results
        '''

        try:
            validation_error_msg = ''
            logging.info("Entered the initiate data method of the data validation class")

            train_df, test_df = (DataValidation.read_data(file_path= self.data_ingestion_artifact_path.trained_file_path),
                                DataValidation.read_data(file_path= self.data_ingestion_artifact_path.test_file_path))
                    
            status = self.validate_number_of_columns(dataframe = train_df)
            logging.info(f"All required columns present in train data {status}")
            if not status:
                validation_error_msg += "Columns are missing in training data"
                    
            status = self.validate_number_of_columns(dataframe = test_df)
            logging.info(f"All required columns present in test data {status}")
            if not status:
                validation_error_msg += "Columns are missing in testing data"

            status = self.does_column_exist(df = train_df)

            if not status:
                validation_error_msg += "Columns are missing from the training data"

            status = self.does_column_exist(df = test_df)

            if not status:
                validation_error_msg += "Columns are missing from the test data"

            validation_status = len(validation_error_msg) == 0

            if validation_status:
                drift_status =self.detect_dataset_drift(train_df, test_df)
                if drift_status:
                    logging.info("Drift detected")
                    validation_error_msg = "Drift detected"
                else:
                    validation_error_msg = "Drift not detected"
            else:
                logging.info("Validation error: {validation_error_msg}")

                    
            data_validation_artifact = DataValidationArtifacts(
                validation_status=validation_status,
                message= validation_error_msg,
                drift_report_file_path=self.data_validation.drift_report_file_path
               )

            logging.info(f"Data validation artifact: {data_validation_artifact}")
            return data_validation_artifact
        except Exception as e:
            raise final_except(e,sys)
                    
                



