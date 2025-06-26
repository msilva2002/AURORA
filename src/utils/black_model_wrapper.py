from services.query_service import QueryService
import pandas as pd

class BlackModelWrapper:
    def __init__(self, dataset, labels):
        number_classes = self._get_number_labels(dataset, labels)
        self.service = QueryService(number_classes)
        

    def predict(self, df):
        predictions = self.service.predict(df)
        return predictions
    
    @staticmethod
    def _get_number_labels(dataset: pd.DataFrame, labels: pd.Series|None) -> int:
        if labels is not None:
            return len(labels.unique())
        else:
            predictions = QueryService().predict(dataset)
            return len(set(predictions))