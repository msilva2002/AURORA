from utils.art_model_util import get_art_classifier
from utils.a2pm_model_util import get_a2pm_classifier
import dask.dataframe as pd
from utils.black_model_wrapper import BlackModelWrapper

import tensorflow as tf
import warnings
tf.get_logger().setLevel('ERROR')
warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", category=UserWarning)
import logging
logging.getLogger("lightgbm").setLevel(logging.CRITICAL)

import os
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

class ModelData:
    def __init__(self, dataset, model, target=None, label=None, data_config=None):
        self.model = model
        self.data_config = data_config
        self.labels, self.dataset = self._get_labels(dataset=dataset, feature_label=label)
        self.columns = self._get_columns()
        self.a2pm_classifier = self._get_a2pm_classifier()
        if self.model is None:
            self.model = BlackModelWrapper(self.dataset, self.labels)
        self._normalize_columns()
        self._convertbool()
        self.target = target
        self.predicted_clean_labels = None

    def get_columns(self) -> pd.Index:
        return self.columns

    def get_model(self):
        return self.model
    
    def get_dataset(self) -> pd.DataFrame:
        return self.dataset.copy()
    
    def get_art_classifier(self):
        return self._get_art_classifier()
    
    def get_a2pm_classifier(self):
        return self.a2pm_classifier
    
    def get_target(self) -> pd.DataFrame:
        if self.target is None:
            return None
        return self.target.copy()
    
    def get_labels(self) -> pd.Series:
        return self.labels
    
    def get_config(self) -> dict:
        from utils.utils import get_features
        dataset = self.get_dataset()
        dataset.columns = self.get_columns()
        feature_division = []
        for feat in self.data_config:
            if feat.get("categorical_features"):
                for feature in feat.get("categorical_features"):
                    feature_division.append(get_features(dataset, feature.get("name")))
        return feature_division
    
    def to_pandas(self):
        self.dataset = self.dataset.compute()

    def set_predicted_clean_labels(self, predicted_labels):
        self.predicted_clean_labels = predicted_labels

    def _get_columns(self) -> pd.Index:
        return self.dataset.columns

    def _get_art_classifier(self):
        return get_art_classifier(model=self.model, dataset=self.dataset, labels=self.labels)
        
    def _get_a2pm_classifier(self):
        return get_a2pm_classifier(model=self.model)
    
    def _normalize_columns(self):
        # turn all columns to 0-len(columns)
        self.dataset.columns = range(len(self.dataset.columns))

    def get_predicted_clean_labels(self):
        return self.predicted_clean_labels
    
    def _convertbool(self):
        # convert boolean columns to integers
        bool_cols = self.dataset.select_dtypes(include=['bool']).columns.tolist()
        if bool_cols:
            dtype_dict = {col: 'int' for col in bool_cols}
            self.dataset = self.dataset.astype(dtype_dict)
            self.dataset = self.dataset.persist()

            
    
    # separate labels from the data, assuming its always the last column
    def _get_labels(self, dataset: pd.DataFrame, feature_label : str):
        if feature_label is not None:
            labels = dataset[feature_label.strip()]
            dataset = dataset.drop(columns=[feature_label.strip()])
            return labels, dataset
        return None, dataset