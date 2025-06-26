import pandas as pd
import numpy as np
from domain_data.perturbed_data import PerturbedData
class EvaluationData:
    def __init__(self, perturbedData : PerturbedData, true_labels, predicted_clean_labels, predicted_perturbed_labels, target_labels):
        self.perturbedData = perturbedData
        self.evaluation : pd.DataFrame = pd.DataFrame(columns=["Evaluation_Name", "Value"])
        self.true_labels : pd.DataFrame = self._normalize_labels(true_labels)
        self.predicted_clean_labels : pd.DataFrame = self._normalize_labels(predicted_clean_labels)
        self.predicted_perturbed_labels : pd.DataFrame = self._normalize_labels(predicted_perturbed_labels)
        self.target_labels : pd.DataFrame = self._normalize_target(target_labels)

    def _normalize_target(self, target):
        if target is not None:
            target = np.asarray(target)
            if target.ndim > 1:
                target = target.reshape(-1)
            target = pd.DataFrame(target)
        else:
            target = pd.DataFrame()
        return target

    def _normalize_labels(self, labels):
        if labels is not None:           
            if len(labels.shape) > 1 and labels.shape[1] > 1:
                labels = labels.argmax(axis=1)
            labels = pd.DataFrame(labels)
        else:
            labels = pd.DataFrame()
        
        return labels
    
    def is_targeted(self) -> bool:
        return self.perturbedData.is_targeted()
    
    def get_perturbedData(self) -> PerturbedData:
        return self.perturbedData
    
    def get_perturbed_dataframe(self) -> pd.DataFrame:
        return self.perturbedData.get_perturbations().copy()

    def get_true_labels(self) -> pd.DataFrame:
        return self.true_labels
    
    def get_predicted_clean_labels(self) -> pd.DataFrame:
        return self.predicted_clean_labels
    
    def get_predicted_perturbed_labels(self) -> pd.DataFrame:
        return self.predicted_perturbed_labels
    
    def get_target_labels(self) -> pd.DataFrame:     
        return self.target_labels
    
    def get_time(self) -> float:
        return self.perturbedData.get_run_time()

    def add_evaluation(self, evaluationName, evaluation):
        self.evaluation = self.evaluation.loc[:, self.evaluation.notna().any(axis=0)]  # Exclude all-NA columns
        new_row = pd.DataFrame({"Evaluation_Name": [evaluationName], "Value": [evaluation]})
        self.evaluation = pd.concat([self.evaluation, new_row], ignore_index=True)  # Append new row

    def get_evaluation(self) -> pd.DataFrame:
        return self.evaluation.copy()