from drivers.clear_driver import ClearDriver

class ClearRepository:
    def clear_folder(self, path:str):
        ClearDriver().clear_folder(path=path)

    def clear_file(self, path:str):
        ClearDriver().clear_file(path=path)