import zope.interface
from evaluations.evaluation_interface import EvaluationI
from domain_data.evaluation_data import EvaluationData

# Misclassification Rate is the rate of misclassification of the model on the perturbed data, representing the rate of attacks that successfully changed the prediction.
# If the model is 100% accurate for the original data, the misclassification rate will be 1 - accuracy.
@zope.interface.implementer(EvaluationI)
class MisclassificationRate:

    evaluationName = "Misclassification Rate"
    adjustable = True

    def execute(self, evaluationData : EvaluationData) -> EvaluationData:
        try:
            #if evaluationData.is_targeted():
            #    raise Exception("Attack must be untargeted for this evaluation")
            predicted_clean = evaluationData.get_predicted_clean_labels()
            predicted_perturbed = evaluationData.get_predicted_perturbed_labels()
            number_of_attacks = len(predicted_perturbed)
            number_of_successful_attacks = (predicted_perturbed != predicted_clean).sum().sum()
            misclassification_rate = number_of_successful_attacks / number_of_attacks
            evaluationData.add_evaluation(self.evaluationName, misclassification_rate)
        except Exception as e:
            pass
        return evaluationData