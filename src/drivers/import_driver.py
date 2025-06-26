import pandas as pd
import joblib
import os
class ImportDriver:

    def get_csv(self, path: str) -> pd.DataFrame:
        if not os.path.exists(path):
            raise FileNotFoundError(f"{path} not found")
        return path
        
    def import_csv(self, path: str) -> pd.DataFrame:
        try:
            return pd.read_csv(path)
        except:
            return None
                
    def get_zip(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"{path} not found")
        return path

    
    def import_model(self, path: str):
        return joblib.load(path)
    
    def get_png_from_folder(self, path : str, name: str):
        # this path is generic and should return all the pngs matching the pattern
        # for example, independent_categorical_feature_A2PM should return all the pngs in the folder
        # that are related to the independent_categorical_feature_A2PM, namely independent_categorical_feature_A2PM_0.png, independent_categorical_feature_A2PM_1.png, etc.
        # the function should return a list of pngs
        png_files = []
        for file in os.listdir(path):
            if file.endswith(".png") and file.startswith(name):
                relative_path = os.path.join(os.path.basename(os.path.dirname(os.path.join(path, file))), os.path.basename(file))
                # replace \\ with /
                relative_path = relative_path.replace("\\", "/")
                png_files.append(relative_path)

        return png_files