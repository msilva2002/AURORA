from drivers.import_driver import ImportDriver
import pandas as pd

class ImportRepository:

    def get_csv(self, path: str) -> pd.DataFrame:
        return ImportDriver().get_csv(path=path)
        
    def import_csv(self, path: str) -> pd.DataFrame:
        return ImportDriver().import_csv(path=path)
                
    def get_zip(self, path: str):
        return ImportDriver().get_zip(path=path)

    
    def import_model(self, path: str):
        return ImportDriver().import_model(path=path)
    
    def get_png_from_folder(self, path : str, name: str):
        return ImportDriver().get_png_from_folder(path=path, name=name)
                

                

        
    