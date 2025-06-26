import zope.interface
from evaluations.evaluation_interface import EvaluationI
from domain_data.evaluation_data import EvaluationData
from sklearn.metrics import accuracy_score
import pandas as pd

@zope.interface.implementer(EvaluationI)
class CleanAccuracy:
    evaluationName = "Clean Accuracy"
    adjustable = False

    def execute(self, evaluationData : EvaluationData) -> EvaluationData:
        try:
            true_labels = evaluationData.get_true_labels()
            if true_labels is pd.DataFrame():
                raise Exception("True labels are required for this evaluation")
            predicted_clean = evaluationData.get_predicted_clean_labels()          
            clean_accuracy = accuracy_score(true_labels, predicted_clean)
            evaluationData.add_evaluation(self.evaluationName, clean_accuracy)
        except Exception as e:
            pass
        return evaluationData