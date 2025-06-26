import tensorflow as tf
import torch
from keras import Model
from a2pm.wrappers import KerasWrapper, SklearnWrapper, TorchWrapper, BaseWrapper
from sklearn.base import BaseEstimator
from catboost import CatBoostClassifier
#from services.query_service import QueryService
import pandas as pd


def get_a2pm_classifier(model):
        
        if model is None:
            return None


        # TensorFlow models
        try:
            if isinstance(model, tf.keras.Model):
                return KerasWrapper(classifier=model)                   
        except (ImportError, AttributeError):
            pass

        # Scikit-learn (catch-all for BaseEstimator)
        if isinstance(model, BaseEstimator):
            return SklearnWrapper(classifier=model)
        
        if isinstance(model, CatBoostClassifier):
            return CatBoostWrapper(model=model)

        raise ValueError(f"Unsupported model type: {type(model)}")


class CatBoostWrapper(BaseWrapper):
    def __init__(self, **params):
        super().__init__(**params)
        self.model = params.get('model')
    
    def predict(self, X):
        if isinstance(X, pd.DataFrame):
            X = X.to_numpy()
        X = X.copy()
        y_pred=self.model.predict(X)
        return y_pred.ravel()