from utils.art_model_util import get_art_classifier
from utils.a2pm_model_util import get_a2pm_classifier
import pandas as pd
from utils.black_model_wrapper import BlackModelWrapper
from config.configuration import Configuration

import tensorflow as tf
import warnings
tf.get_logger().setLevel('ERROR')
warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", category=UserWarning)
import logging
logging.getLogger("lightgbm").setLevel(logging.CRITICAL)

class ModelData:
    def __init__(self, dataset, model, target=None):
        self.model = model
        self.labels, self.dataset = self._get_labels(dataset=dataset)
        self.columns = self._get_columns()
        self.art_classifier = self._get_art_classifier()
        self.a2pm_classifier = self._get_a2pm_classifier()
        if self.model is None:
            self.model = BlackModelWrapper(self.dataset, self.labels)
        self._normalize_columns()
        self._convertbool()
        self.target = target

    def get_columns(self) -> pd.Index:
        return self.columns

    def get_model(self):
        return self.model
    
    def get_dataset(self) -> pd.DataFrame:
        return self.dataset.copy()
    
    def get_art_classifier(self):
        return self.art_classifier
    
    def get_a2pm_classifier(self):
        return self.a2pm_classifier
    
    def get_target(self) -> pd.DataFrame:
        if self.target is None:
            return None
        return self.target.copy()
    
    def get_labels(self) -> pd.Series:
        return self.labels

    def _get_columns(self) -> pd.Index:
        return self.dataset.columns

    def _get_art_classifier(self):
        return get_art_classifier(model=self.model, dataset=self.dataset, labels=self.labels)
        
    def _get_a2pm_classifier(self):
        return get_a2pm_classifier(model=self.model)
    
    def _normalize_columns(self):
        # turn all columns to 0-len(columns)
        self.dataset.columns = range(len(self.dataset.columns))

    def _convertbool(self):
        # convert boolean columns to integers
        bool_cols = self.dataset.select_dtypes(include=['bool']).columns.tolist()
        for col in bool_cols:
            self.dataset[col] = self.dataset[col].astype(int)
    
    # separate labels from the data, assuming its always the last column
    def _get_labels(self, dataset: pd.DataFrame):
        label = Configuration().get_label()
        if label is not None:
            labels = dataset[label.strip()]
            dataset = dataset.drop(columns=[label.strip()])
            return labels, dataset
        return None, dataset