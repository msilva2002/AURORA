import pandas as pd
class PerturbedData:
    def __init__(self, attackName : str, perturbations:pd.DataFrame, run_time : float, targeted=False, message="", error=False):
        self.attackName = attackName
        self.perturbations = perturbations
        self.run_time = run_time
        self.targeted = targeted
        self.message = message
        self.error = error

    def replace_perturbations(self, perturbations: pd.DataFrame):
        self.perturbations = perturbations

    def get_perturbations(self) -> pd.DataFrame:
        return self.perturbations

    def is_targeted(self) -> bool:
        return self.targeted
    
    def get_run_time(self) -> float:
        return self.run_time