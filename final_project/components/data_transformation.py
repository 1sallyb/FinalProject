import sys

import numpy as np
import pandas as pd


from imblearn.combine import SMOTEENN
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder, PowerTransformer
from sklearn.compose import ColumnTransformer


from final_project.constants import TARGET_COLUMN, SCHEMA_FILE_PATH, CURRENT_YEAR
from final_project.entity.config_entity import DataTransformationConfig
from final_project.entity.artifact_entity import DataTransformationArtifact, DataIngestionArtifacts, DataValidationArtifacts


from final_project.exception import final_except
from final_project.logger import logging

from final_project.utils.main_utils import save_object, save_numpy_array_data, read_yaml_file,drop_columns
from final_project.entity.estimator import TargetValueMapping


class DataTransformation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifacts,
                 data_transformation_config: DataTransformationConfig,
                 data_validation_artifact: DataTransformationArtifact):
        
        '''
        the output is the data ingestion artifact 
        and configuration of data transformation
        '''

        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_transformation_config = data_transformation_config
            self.data_validation_artifact = data_validation_artifact
            self.schema_config = read_yaml_file(file_path=SCHEMA_FILE_PATH)

        except Exception as e:
            raise final_except(e,sys)
        

        @staticmethod
        def read_data(file_path)->pd.DataFrame:
            try:
                return pd.read_csv(file_path)
            except Exception as e:
                raise final_except(e,sys)
            
        
        def get_data_transformer_object(self)-> Pipeline:
            '''
            Creates and returns a data transformer object
            for the data
            '''

            try:
                logging.info("Got numerial columns from schema_config")
                
                numerical_transformer = StandardScaler()
                nominal_transformer = OneHotEncoder()
                ordinal_encoder = OrdinalEncoder()

                logging.info("Initialized StandardScaler, OneHotEncoder, and OrdinalEncoder")

                nominal_columns = self._schema_config['nominal_columns']
                ordinal_columns = self._schema_config['ordinal_columns']
                transform_columns = self._schema_config['transform_columns']
                num_features = self._schema_config['num_features']

                logging.info('Initialize power transformer')

                transform_pipe = Pipeline(steps = [
                    ('transformer', PowerTransformer(method= 'yeo-johnson'))
                ])

                preprocessor = ColumnTransformer(
                    [
                        ('OneHotEncoder', nominal_transformer, nominal_columns)
                        ('OrdinalEncoder', ordinal_encoder, ordinal_columns)
                        ('StandardScaler', numerical_transformer, num_features)
                    ]
                )

                logging.info('Created preprocessor object from ColumnTransformer')
                logging.info("Exited the get_data_transformer_object method of DataTransformation Class")

                return preprocessor
            except Exception as e:
                raise final_except(e,sys)
            
        def initiate_data_transformation(self)->DataTransformationArtifact:
            '''
                initiate data transformation component of pipeline
                returns a transformed preprocessor object
            '''

            try:
                if self.data_validation_artifact.validation_status:
                    logging.info("Starting data transformation")

                    preprocessor = self.get_data_transformer_object
                    logging.info('Acquired preprocessor object')

                    train_df = DataTransformation.read_data(file_path=self.data_ingestion_artifact.trained_file_path)
                    test_df = DataTransformation.read_data(file_path=self.data_ingestion_artifact.test_file_path)

                    input_feature_train_df = train_df.drop(columns = [TARGET_COLUMN], axis = 1)
                    target_feature_train_df = train_df[TARGET_COLUMN]

                    logging.info("Acquired features of the traning data set")
                    input_feature_train_df['company_age'] = CURRENT_YEAR - input_feature_train_df['yr_of_estab']
                    logging.info('Created column company_age in the Training dataset')

                    drop_cols = self._schema.config['drop_columns']

                    logging.info("Dropped the drop_cols from the training dataset")

                    input_feature_train_df = drop_columns(df = input_feature_train_df, cols = drop_columns)
                    target_feature_train_df = target_feature_train_df.replace(TargetValueMapping())

                    input_feature_test_df = test_df.drop(columns = [TARGET_COLUMN], axis = 1)
                    target_feature_test_df = test_df[TARGET_COLUMN]

                    input_feature_test_df['company_age'] = CURRENT_YEAR - input_feature_test_df['yr_of_estab']

                    logging.info('Created column company_age in the testing dataset')
                    logging.info("Dropped the drop_cols from the testing dataset")

                    input_feature_test_df = drop_columns(df = input_feature_test_df, cols = drop_columns)
                    target_feature_test_df = target_feature_test_df.replace(TargetValueMapping())

                    logging.info("Got train features and test features of testing dataset")
                    logging.info("Applying preprocessing object on training and testing dataframe")

                    input_features_train_arr = preprocessor.fit_transform(input_feature_train_df)
                    input_features_test_arr = preprocessor.transform(input_feature_test_df)

                    logging.info("The preprocessor object has applied fit transform to train features")
                    logging.info("Applying SMOTEENN on Training dataset")

                    smt = SMOTEENN(sampling_strategy = 'minority')

                    input_feature_train_final, target_feature_train_final = smt.fit_resample(
                        input_feature_train_arr, target_feature_train_df
                    )

                    logging.info("Applied SMOTEENN")
                    logging.info("Created train array and test array")

                    train_arr = np.c_[
                        input_feature_train_final, np.array(target_feature_train_final)
                    ]
                    test_arr = np.c_[
                        input_feature_test_final,np.array(target_feature_test_df)
                    ]

                    save_object(self.data_transformation_config.transformed_object_file_path, preprocessor)
                    save_numpy_array_data(self.data_transformation_config.transformed_train_file_path, array = train_arr)
                    save_numpy_array_data(self.data_transformation_config.transformed_test_file_path, array = test_arr)
                    
                    logging.info("Saved preprocessor object")
                    logging.info("Exited initiate_data_transformation method of DataTransformation class")

                    data_transformation_artifact = DataTransformationArtifact(
                        transformed_object_file_path = self.data_transformation_config.transformed_object_file_path,
                        transformed_train_file_path = self.data_transformation_config.transformed_train_file_path,
                        transformed_test_file_path = self.data_transformation_config.transformed_test_file_path,
                    )

                    return data_transformation_artifact                    
                else:
                    raise Exception(self.data_validation_artifact.message)
                    
            except Exception as e:
                raise final_except(e,sys)
