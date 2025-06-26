from domain_data.perturbed_data import PerturbedData
import pandas as pd
class AttackErrorHandler:
    def handle_error(self, attackName: str, targeted: bool, error: Exception):
        # the attack requires a target
        if "target" in str(error).lower():
            return PerturbedData(attackName=attackName, perturbations=pd.DataFrame(), run_time=0, targeted=targeted, error=True, message="Missing target data.")
        # model is not compatible with art attack
        if "classifier" in str(error).lower():
            return PerturbedData(attackName=attackName, perturbations=pd.DataFrame(), run_time=0, targeted=targeted, error=True, message="Model is not compatible with attack.")
        if "reduce the number of parallelcoordinate updates `nb_parallel`" in str(error).lower():
            return PerturbedData(attackName=attackName, perturbations=pd.DataFrame(), run_time=0, targeted=targeted, error=True, message="A lower value for nb_parallel is required.")
        else:
            return PerturbedData(attackName=attackName, perturbations=pd.DataFrame(), run_time=0, targeted=targeted, error=True, message="An unknown error occurred." + str(error))
