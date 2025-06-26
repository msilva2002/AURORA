import zope.interface
from evaluations.evaluation_interface import EvaluationI
from domain_data.evaluation_data import EvaluationData
import pandas as pd
from sklearn.metrics import accuracy_score


@zope.interface.implementer(EvaluationI)
class AttackDeterioration:

    evaluationName = "Attack Deterioration"
    adjustable = False

    def execute(self, evaluationData : EvaluationData) -> EvaluationData:
        try:
            true_labels = evaluationData.get_true_labels() 
            if true_labels is pd.DataFrame():
                raise Exception("True labels are required for this evaluation")
            predicted_perturbed = evaluationData.get_predicted_perturbed_labels()
            adversarial_accuracy = accuracy_score(true_labels, predicted_perturbed)

            true_labels = evaluationData.get_true_labels()
            if true_labels is pd.DataFrame():
                raise Exception("True labels are required for this evaluation")
            predicted_clean = evaluationData.get_predicted_clean_labels()          
            clean_accuracy = accuracy_score(true_labels, predicted_clean)

            evaluationResult = (clean_accuracy - adversarial_accuracy)/clean_accuracy

            evaluationData.add_evaluation(self.evaluationName, evaluationResult)
        except Exception as e:
            pass
        return evaluationData