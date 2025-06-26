import unittest
from evaluations.evaluation_clean_accuracy import CleanAccuracy
from domain_data.evaluation_data import EvaluationData
from domain_data.perturbed_data import PerturbedData
import pandas as pd

class TestCleanAccuracy(unittest.TestCase):
    def setUp(self):
        true_labels = pd.DataFrame([0, 1, 2, 3, 0, 1, 2, 3, 0, 1])
        predicted_clean_labels = pd.DataFrame([0, 1, 0, 3, 0, 1, 0, 3, 0, 1])
        perturbedData = PerturbedData(None, None, None, True, "", False)
        self.evalData = EvaluationData(perturbedData, true_labels, predicted_clean_labels, None, None)

    def test_clean_accuracy_correct(self):
        print("Testing Clean Accuracy")
        evaluationData : EvaluationData = CleanAccuracy().execute(self.evalData)
        self.assertEqual(evaluationData.get_evaluation().Evaluation_Name[0], "Clean Accuracy")
        self.assertEqual(evaluationData.get_evaluation().Value[0], 0.8)

        self.assertNotEqual(evaluationData.get_evaluation().Evaluation_Name[0], "Adversarial Accuracy")
        self.assertNotEqual(evaluationData.get_evaluation().Value[0], 0.7)

    def test_clean_accuracy_no_true_labels(self):
        print("Testing Clean Accuracy with no true labels")
        self.evalData.true_labels = None
        evaluationData : EvaluationData = CleanAccuracy().execute(self.evalData)
        # evaluationData.get_evaluation() should be an empty DataFrame
        self.assertEqual(evaluationData.get_evaluation().empty, True)