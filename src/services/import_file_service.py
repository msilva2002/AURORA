from repositories.import_repository import ImportRepository

class ImportFileService:
    def __init__(self):
        self.repository = ImportRepository()

    def import_file(self, file_path: str):
        if file_path.endswith('.csv'):
            return self.repository.import_csv(file_path)
        elif file_path.endswith('.joblib'):
            return self.repository.import_model(file_path)
        return None