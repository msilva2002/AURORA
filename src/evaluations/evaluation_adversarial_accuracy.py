import zope.interface
from evaluations.evaluation_interface import EvaluationI
from domain_data.evaluation_data import EvaluationData
import pandas as pd
from sklearn.metrics import accuracy_score


@zope.interface.implementer(EvaluationI)
class AdversarialAccuracy:
    evaluationName = "Adversarial Accuracy"
    adjustable = False
    
    def execute(self, evaluationData : EvaluationData) -> EvaluationData:
        try:
            true_labels = evaluationData.get_true_labels() 
            if true_labels is pd.DataFrame():
                raise Exception("True labels are required for this evaluation")
            predicted_perturbed = evaluationData.get_predicted_perturbed_labels()
            adversarial_accuracy = accuracy_score(true_labels, predicted_perturbed)
            evaluationData.add_evaluation(self.evaluationName, adversarial_accuracy)
        except Exception as e:
            pass
        return evaluationData