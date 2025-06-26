from domain_data.model_data import ModelData
from domain_data.perturbed_data import PerturbedData
from domain_data.evaluation_data import EvaluationData
from managers.status_manager import StatusManager
from distances.metric_adjuster import adjust_metrics
from utils.revert_changes import revert_changes_df

class ExecuteEvaluationService:
    def __init__(self, evaluationClasses):
        self.evaluationClasses = evaluationClasses
        self.statusManager = StatusManager()

    def execute(self, modelData: ModelData, perturbedData: PerturbedData)->EvaluationData:
        if perturbedData.error == False:
            evaluation_data : EvaluationData = self._create_evaluation(modelData, perturbedData)
            for evaluationClass in self.evaluationClasses:
                evaluation_data = evaluationClass().execute(evaluation_data)
            self.statusManager.update_evaluate(perturbedData.attackName, evaluation_data.get_evaluation())
            evaluation_data = adjust_metrics(evaluation_data, self.evaluationClasses, modelData)
            self.statusManager.update_adjust(perturbedData.attackName, evaluation_data.get_evaluation())
            return evaluation_data
        return None

    #def execute(self, modelData: ModelData, perturbedData_list:List[PerturbedData])->List[EvaluationData]:
    #    for perturbedData in perturbedData_list:
    #        if perturbedData.error == False:
    #            evaluation_data : EvaluationData = self._create_evaluation(modelData, perturbedData)
    #            for evaluationClass in self.evaluationClasses:
    #                evaluation_data = evaluationClass().execute(evaluation_data)
    #            self.statusManager.update_evaluate(perturbedData.attackName, evaluation_data.get_evaluation())


    #def execute(self, modelData: ModelData, perturbedData_list:List[PerturbedData])->List[EvaluationData]:
        #evaluation_data_list : List[EvaluationData] = []
    #    for perturbedData in perturbedData_list:
    #        if perturbedData.error == False:
    #            evaluation_data : EvaluationData = self._create_evaluation(modelData, perturbedData)
    #            for evaluationClass in self.evaluationClasses:
    #                evaluation_data = evaluationClass().execute(evaluation_data)
    #            self.statusManager.update_evaluate(perturbedData.attackName, evaluation_data.get_evaluation())
                #evaluation_data_list.append(evaluation_data)
        #return evaluation_data_list
    
    def _create_evaluation(self, modelData: ModelData, perturbedData : PerturbedData) -> EvaluationData:
        model = modelData.get_model()
        data = modelData.get_dataset()
        columns = modelData.get_columns()
        data.columns = columns
        target = modelData.get_target()
        perturbation_data = perturbedData.get_perturbations()
        perturbation_data.columns = columns
        
        true_labels = modelData.get_labels()
        predicted_clean_labels = model.predict(data)
        predicted_perturbed_labels = model.predict(perturbation_data)
        # Revert changes if the labels are the same
        perturbed_df = revert_changes_df(data, perturbation_data, predicted_clean_labels, predicted_perturbed_labels)
        perturbedData.replace_perturbations(perturbed_df)
        return EvaluationData(perturbedData, true_labels, predicted_clean_labels, predicted_perturbed_labels, target)

        