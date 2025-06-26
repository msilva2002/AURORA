from repositories.query_repository import QueryModel
import pandas as pd
import numpy as np
class QueryService:
    def __init__(self, nb_class:int):
        self.query_repository = QueryModel()
        self.nb_class = nb_class

    def predict(self, df):
        predictions = self.query_repository.predict(pd.DataFrame(df))
        # turn into probabilities
        if self.nb_class > 2:
            predictions = self._to_probabilities(predictions)
        return predictions
    
    def _to_probabilities(self, predictions):
        proba = np.zeros((len(predictions), self.nb_class))
        for i, pred in enumerate(predictions):
            proba[i, pred] = 1
        return proba