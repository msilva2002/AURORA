import os, shutil

class ClearDriver:
    def clear_folder(self, path:str):
        if os.path.exists(path):
            for filename in os.listdir(path):
                file_path = os.path.join(path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {e}')
        else:
            os.makedirs(path)

    def clear_file(self, path:str):
        if os.path.exists(path):
            os.remove(path)
        else:
            print(f"The file {path} does not exist.")