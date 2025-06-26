from sklearn.metrics import confusion_matrix
import zope.interface
from evaluations.evaluation_interface import EvaluationI
from domain_data.evaluation_data import EvaluationData


@zope.interface.implementer(EvaluationI)
class ConfusionMatrix:

    evaluationName = "Confusion Matrix"
    adjustable = False
    def execute(self, evaluationData : EvaluationData) -> EvaluationData:
        try:
            predicted_clean = evaluationData.get_predicted_clean_labels()
            predicted_perturbed = evaluationData.get_predicted_perturbed_labels()
            cm = confusion_matrix(predicted_clean, predicted_perturbed)
            evaluationData.add_evaluation(self.evaluationName, cm)
        except Exception as e:
            pass
        return evaluationData