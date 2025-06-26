# singleton which holds the configuration values, imports a json file and stores the values in a dictionary
import json

class Configuration:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Configuration, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self.config = []
        self._load_config()

    def _load_config(self):
        with open("config/config.json", "r") as f:
            self.config = json.load(f)

    def reset_config(self):
        self.config = []
        self._load_config()

    def _parse_values(self, config):
        for item in config:
            if isinstance(item, dict):
                for key, value in item.items():
                    if isinstance(value, str) and value.isdigit():
                        item[key] = int(value)
                    elif isinstance(value, str) and value.replace('.', '', 1).isdigit():
                        item[key] = float(value)
        return config

    def update_config(self, new_config):
        try:
            parsed_config = self._parse_values(new_config)
            # Directly replace self.config with the new configuration (no need to convert to string)
            self.config = parsed_config

            return True
        except Exception as e:
            print(e)
            return False

    def get_config(self, attackName):
        for attack in self.config:
            if attack.get("attackName") == attackName:
                attack_copy = attack.copy()
                attack_copy.pop("attackName", None)
                return attack_copy
        return {}
    
    def get_config_file(self):
        return self.config

    def get_label(self):
        return next((item["feature_label"] for item in self.config if item.get("feature_label")), None)