import zope.interface
from evaluations.evaluation_interface import EvaluationI
from domain_data.evaluation_data import EvaluationData

# Attack Success Rate is the rate of successful attacks, representing the rate of attacks that successfully changed the prediction to the target class.


@zope.interface.implementer(EvaluationI)
class AttackSuccessRate:

    evaluationName = "Attack Success Rate"
    adjustable = True

    def execute(self, evaluationData : EvaluationData) -> EvaluationData:
        try:
            if evaluationData.is_targeted() == False:
                raise Exception("Attack must be targeted for this evaluation")

            predicted_clean = evaluationData.get_predicted_clean_labels()
            predicted_perturbed = evaluationData.get_predicted_perturbed_labels()
            target = evaluationData.get_target_labels()

            number_of_attacks = len(predicted_perturbed)
            number_of_successful_attacks = 0

            for i in range(number_of_attacks):
                if (target.iloc[i].values)==(predicted_clean.iloc[i].values):
                    number_of_attacks -= 1
                    continue
                if (predicted_perturbed.iloc[i].values)==(target.iloc[i].values):
                    number_of_successful_attacks += 1

            attack_success_rate = number_of_successful_attacks / number_of_attacks
            evaluationData.add_evaluation(self.evaluationName, attack_success_rate)
        except Exception as e:
            pass
        return evaluationData
