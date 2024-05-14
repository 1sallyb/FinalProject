import sys

from panda import DataFrame
from sklearn.pipeline import Pipeline

from final_project.exception import final_except
from final_project.logger import logging

# Target Value Mapping
class TargetValueMapping:
    def __init__(self):
        self.Certified: int = 0
        self.Denied: int = 1

    def _asdict(self):
        return self.__dict__
    def reverse_mapping(self):
        mapping_response = self._asdict()
        return dict(zip(mapping_response.values(), mapping_response.keys()))
    
    class USVisaModel:
        def __init__(self, preprocessing_object: Pipeline,trained_model_object: object):
            '''
            inputs objects of preprocessor and trained models
            '''
            self.preprocessing_object = preprocessing_object
            self.trained_model_object = trained_model_object

            def predict(self, dataframe: DataFrame) -> DataFrame:
                '''
                accept raw input and transform raw input into preprocessing object

                guarantees the data to be in the correct format for the model to be trained on

                perform predictions on the transformed data
                '''

                logging.info("Entered the predict method of the USVisaModel Class")

                try:
                    logging.info("Using the train model to get predictions")
                    transformed_feature = self.preprocessing_object.transform(dataframe)
                    logging.info('Transformed features stored')
                    return self.trained_model_object.get_predictions(transformed_features)
                except Exception as e:
                    raise final_except(e, sys)
                
                def __repr__(self):
                    return f"{type(self.train_model_object).__name__}"
                def __str__(self):
                    return f"{type(self.train_model_object).__name__}"



