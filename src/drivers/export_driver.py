import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import os
import zipfile

class ExportDriver:
    
    def export_plot(self, figure, file_path: str):
        figure.savefig(file_path)
        plt.close(figure)

    def export_md(self, lines : list[str], file_path: str):
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
        return True
        

    def export_csv(self, data:pd.DataFrame, file_path: str):
        data.to_csv(file_path, index=False)

    def create_zip_file_folder(self, folder_path: str, file_path: str, zip_path: str = None):

        if not os.path.isdir(folder_path):
            raise FileNotFoundError(f"Folder not found: {folder_path}")

        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Determine the output zip file path
        if zip_path is None:
            zip_name = os.path.basename(folder_path.rstrip("/\\")) + ".zip"
            zip_path = os.path.join(os.getcwd(), zip_name)
        elif os.path.isdir(zip_path):
            zip_name = os.path.basename(folder_path.rstrip("/\\")) + ".zip"
            zip_path = os.path.join(zip_path, zip_name)
        else:
            os.makedirs(os.path.dirname(zip_path), exist_ok=True)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            folder_name = os.path.basename(os.path.normpath(folder_path))  # e.g., "images"

            # Include all files inside the folder, preserving the folder name in the zip
            for root, _, files in os.walk(folder_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, start=folder_path)
                    arcname = os.path.join(folder_name, relative_path)  # e.g., images/img1.png
                    zipf.write(full_path, arcname)

            # Add the separate file at the root of the zip
            zipf.write(file_path, arcname=os.path.basename(file_path))
