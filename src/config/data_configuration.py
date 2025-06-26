# singleton which holds the configuration values, imports a json file and stores the values in a dictionary
import json
from utils.utils import get_features

class DataConfiguration:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataConfiguration, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self.config = []
        self._load_config()

    def _load_config(self):
        with open("config/data_config.json", "r") as f:
            self.config = json.load(f)

    def reset_config(self):
        self.config = []
        self._load_config()

    def update_config(self, new_config):
        try:
            # Directly replace self.config with the new configuration (no need to convert to string)
            self.config = new_config
            return True
        except Exception as e:
            #raise e
            return False

    def get_config(self, df_init):
        feature_division = []
        for feat in self.config:
            if feat.get("categorical_features"):
                for feature in feat.get("categorical_features"):
                    feature_division.append(get_features(df_init, feature.get("name")))
        return feature_division
    
    def get_config_file(self):
        return self.config
