from domain_data.model_data import ModelData
from domain_data.perturbed_data import PerturbedData
from domain_data.evaluation_data import EvaluationData
from distances.metric_adjuster import adjust_metrics
from utils.revert_changes import revert_changes_df
import pandas as pd

class ExecuteEvaluationService:
    def __init__(self, evaluationClasses, modelData:ModelData):
        self.evaluationClasses = evaluationClasses
        modelData.to_pandas()
        model = modelData.get_model()
        data = modelData.get_dataset()
        columns = modelData.get_columns()
        data.columns = columns
        predicted_clean_labels = model.predict(data)
        #if predicted_clean_labels.ndim == 2:
            #predicted_clean_labels = np.argmax(predicted_clean_labels, axis=1)
        modelData.set_predicted_clean_labels(predicted_clean_labels)

    def execute(self, modelData: ModelData, perturbedData: PerturbedData)->EvaluationData:
        if perturbedData.error == False:
            evaluation_data : EvaluationData = self._create_evaluation(modelData, perturbedData)
            for evaluationClass in self.evaluationClasses:
                evaluation_data = evaluationClass().execute(evaluation_data)
            evaluation_data = adjust_metrics(evaluation_data, self.evaluationClasses, modelData)
            return evaluation_data
        return None
    def _create_evaluation(self, modelData: ModelData, perturbedData : PerturbedData) -> EvaluationData:
        model = modelData.get_model()
        columns = modelData.get_columns()
        target = modelData.get_target()
        perturbation_data = perturbedData.get_perturbations()
        perturbation_data.columns = columns
        data = modelData.get_dataset()
        columns = modelData.get_columns()
        data.columns = columns
        true_labels = modelData.get_labels()
        
        predicted_clean_labels = modelData.get_predicted_clean_labels()
        predicted_perturbed_labels = model.predict(perturbation_data)
        #if predicted_perturbed_labels.ndim == 2:
            #predicted_perturbed_labels = np.argmax(predicted_perturbed_labels, axis=1)
        # Revert changes if the labels are the same
        perturbed_df = revert_changes_df(data, perturbation_data, predicted_clean_labels, predicted_perturbed_labels)
        perturbedData.replace_perturbations(perturbed_df)
        return EvaluationData(perturbedData, true_labels, predicted_clean_labels, predicted_perturbed_labels, target)

        