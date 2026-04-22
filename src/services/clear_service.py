from repositories.clear_repository import ClearRepository

class ClearService:
    def clear_folder(self, path:str):
        ClearRepository().clear_folder(path=path)

    def clear_file(self, path:str):
        ClearRepository().clear_file(path=path)

