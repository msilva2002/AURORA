import unittest
from domain_data.perturbed_data import PerturbedData
from evaluations.evaluation_attack_success_rate import AttackSuccessRate
from domain_data.evaluation_data import EvaluationData
import pandas as pd

class TestAttackSuccessRate(unittest.TestCase):
    def setUp(self):
        predicted_perturbed_labels = pd.DataFrame([0, 1, 0, 3, 0, 1, 0, 3, 0, 1])
        target = pd.DataFrame([1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        perturbed_clean_labels = pd.DataFrame([0, 1, 0, 3, 0, 2, 0, 3, 0, 3])

        perturbedData = PerturbedData(None, None, None, True, "", False)
        self.evalData = EvaluationData(perturbedData, None, perturbed_clean_labels, predicted_perturbed_labels, target)

    def test_attack_success_rate_correct(self):
        print("Testing Attack Success Rate")
        evaluationData : EvaluationData = AttackSuccessRate().execute(self.evalData)
        self.assertEqual(evaluationData.get_evaluation().Evaluation_Name[0], "Attack Success Rate")
        self.assertEqual(evaluationData.get_evaluation().Value[0], 0.2)

        self.assertNotEqual(evaluationData.get_evaluation().Evaluation_Name[0], "Clean Accuracy")
        self.assertNotEqual(evaluationData.get_evaluation().Value[0], 0.7)

    def test_attack_success_rate_no_target(self):
        print("Testing Attack Success Rate with no target")
        self.evalData.perturbedData.targeted = False
        evaluationData : EvaluationData = AttackSuccessRate().execute(self.evalData)
        # evaluationData.get_evaluation() should be an empty DataFrame
        self.assertEqual(evaluationData.get_evaluation().empty, True)