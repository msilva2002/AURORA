import unittest
from evaluations.evaluation_misclassification_rate import MisclassificationRate
from domain_data.evaluation_data import EvaluationData
from domain_data.perturbed_data import PerturbedData
import pandas as pd

class TestMisclassificationRate(unittest.TestCase):
    def setUp(self):
        predicted_clean_labels = pd.DataFrame([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        predicted_perturbed_labels = pd.DataFrame([9, 8, 7, 6, 5, 4, 3, 2, 1, 0])
        perturbedData = PerturbedData(None, None, None, False, "", False)
        self.evalData = EvaluationData(perturbedData, None, predicted_clean_labels, predicted_perturbed_labels, None)

    def test_attack_success_rate_correct(self):
        print("Testing Misclassification Rate")
        evaluationData : EvaluationData = MisclassificationRate().execute(self.evalData)
        self.assertEqual(evaluationData.get_evaluation().Evaluation_Name[0], "Misclassification Rate")
        self.assertEqual(evaluationData.get_evaluation().Value[0], 1)

        self.assertNotEqual(evaluationData.get_evaluation().Evaluation_Name[0], "Clean Accuracy")
        self.assertNotEqual(evaluationData.get_evaluation().Value[0], 0.7)