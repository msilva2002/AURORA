import pandas as pd
import numpy as np
from repositories.clear_repository import ClearRepository
from repositories.export_repository import ExportRepository
from repositories.import_repository import ImportRepository

class StatusManager:

    # start singleton
    _instance = None

    states = ["" ,"Loaded", "Running", "Finished", "Evaluated", "Evaluated and Adjusted"] # and Error

    def __new__(cls, attackClasses=None):
        if cls._instance is None:
            cls._instance = super(StatusManager, cls).__new__(cls)
            cls._instance._init(attackClasses)
        return cls._instance

    def _init(self, attackClasses):
        if attackClasses is not None:  # Ensure attackClasses is not None
            self.classes = {c._attackName for c in attackClasses}
            # start as empty
            self.status = {c: self.states[0] for c in self.classes}
            # dictionary to store evaluation results
            self.eval = {c: [] for c in self.classes}
            # check if the datasets folder exists, if so, delete all files, if not, create it
            ClearRepository().clear_folder("datasets")
            # start report availability 
            self.report = False
        
    def reset_status(self):
        self.status = {c: self.states[0] for c in self.classes}
        self.eval = {c: [] for c in self.classes}
        self.report = False
    
    def update_load(self, attackClass):
        self.status[attackClass] = self.states[1]
    
    def update_run(self, attackClass):
        self.status[attackClass] = self.states[2]

    def update_finish(self, attackClass, perturbation:pd.DataFrame):
        self.status[attackClass] = self.states[3]
        # save the perturbation to a file
        ExportRepository().export_csv(perturbation, f"datasets/{attackClass}.csv")

        
    
    def update_evaluate(self, attackClass, evaluation:pd.DataFrame):
        self.status[attackClass] = self.states[4]
        self.eval[attackClass] = [
            {record["Evaluation_Name"]: self._convert_value(record["Value"])}
            for record in evaluation.to_dict(orient="records")
        ]

    def update_adjust(self, attackClass, evaluation:pd.DataFrame):
        self.status[attackClass] = self.states[5]
        self.eval[attackClass] = [
            {record["Evaluation_Name"]: self._convert_value(record["Value"])}
            for record in evaluation.to_dict(orient="records")
        ]

    def set_report_ready(self):
        self.report = True

    def get_report_status(self):
        return self.report

    def get_report(self):
        from reports.report import ZIP_NAME
        if self.report:
            return ImportRepository().get_zip(ZIP_NAME)
        else:
            return None

    def get_perturbation(self, attackClass):
       # check if attack is finished or further
        # get the position of the attackClass in the states list
        try:
            state_index = self.states.index(self.status[attackClass])
        except Exception as e:
            return None
            # get index of finished state
        finished_index = self.states.index(self.states[3])
        print(f"State index: {state_index}, Finished index: {finished_index}")
        if state_index < finished_index:
            print(f"Perturbation for {attackClass} is not available. Status: {self.status[attackClass]}")
            return None
        return ImportRepository().get_csv(f"datasets/{attackClass}.csv")
        

    def _convert_value(self, value):
        """Convert NumPy arrays to lists and handle other special types."""
        if isinstance(value, np.ndarray):  # Check if value is a NumPy array
            return value.tolist()  # Convert NumPy array to list
        return value  # Return the value as is if not a NumPy array

    def update_error(self, attackClass, error_message):
        self.status[attackClass] = error_message

    # to a json friendly format
    def get_status(self):
        json_status = []
        for key, value in self.status.items():
            evaluation_data = self.eval.get(key, [])
            
            json_status.append({
                "attackName": str(key),
                "status": value,
                "evaluation": evaluation_data
            })
        
        return json_status
