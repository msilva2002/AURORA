from drivers.export_driver import ExportDriver
import pandas as pd

class ExportRepository:
    
    def export_plot(self, figure, file_path: str):
        ExportDriver().export_plot(figure=figure, file_path=file_path)

    def export_md(self, lines : list[str], file_path: str):
        return ExportDriver().export_md(lines=lines, file_path=file_path)
        

    def export_csv(self, data:pd.DataFrame, file_path: str):
        ExportDriver().export_csv(data=data, file_path=file_path)

    def create_zip_file_folder(self, folder_path: str, file_path: str, zip_path: str = None):
        ExportDriver().create_zip_file_folder(folder_path=folder_path, file_path=file_path, zip_path=zip_path)
