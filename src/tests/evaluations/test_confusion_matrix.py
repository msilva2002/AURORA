import unittest
from evaluations.evaluation_confusion_matrix import ConfusionMatrix
from domain_data.evaluation_data import EvaluationData
from domain_data.perturbed_data import PerturbedData
import pandas as pd
import numpy as np

class TestConfusionMatrix(unittest.TestCase):
    def setUp(self):
        predicted_clean_labels = pd.DataFrame([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        predicted_perturbed_labels = pd.DataFrame([9, 8, 7, 6, 5, 4, 3, 2, 1, 0])
        perturbedData = PerturbedData(None, None, None, False, "", False)
        self.evalData = EvaluationData(perturbedData, None, predicted_clean_labels, predicted_perturbed_labels, None)

    def test_attack_success_rate_correct(self):
        print("Testing Confusion Matrix")
        expected_value = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
                          [0, 0, 0, 0, 0, 0, 0, 0, 1, 0], 
                          [0, 0, 0, 0, 0, 0, 0, 1, 0, 0], 
                          [0, 0, 0, 0, 0, 0, 1, 0, 0, 0], 
                          [0, 0, 0, 0, 0, 1, 0, 0, 0, 0], 
                          [0, 0, 0, 0, 1, 0, 0, 0, 0, 0], 
                          [0, 0, 0, 1, 0, 0, 0, 0, 0, 0], 
                          [0, 0, 1, 0, 0, 0, 0, 0, 0, 0], 
                          [0, 1, 0, 0, 0, 0, 0, 0, 0, 0], 
                          [1, 0, 0, 0, 0, 0, 0, 0, 0, 0]])

        evaluationData : EvaluationData = ConfusionMatrix().execute(self.evalData)
        self.assertEqual(evaluationData.get_evaluation().Evaluation_Name[0], "Confusion Matrix")
        actual_value = np.array(evaluationData.get_evaluation().Value[0])
        self.assertTrue(np.array_equal(actual_value, expected_value))

        not_expected_value = np.array([[10, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
                          [0, 0, 0, 0, 0, 0, 0, 0, 1, 0], 
                          [0, 0, 0, 0, 0, 0, 0, 1, 0, 0], 
                          [0, 0, 0, 0, 0, 0, 1, 0, 0, 0], 
                          [0, 0, 0, 0, 0, 1, 0, 0, 0, 0], 
                          [0, 0, 0, 0, 1, 0, 0, 0, 0, 0], 
                          [0, 0, 0, 1, 0, 0, 0, 30, 0, 0], 
                          [0, 0, 1, 0, 0, 0, 0, 0, 0, 0], 
                          [0, 1, 0, 0, 0, 40, 0, 0, 0, 0], 
                          [1, 0, 0, 0, 0, 0, 0, 0, 0, 0]])
        self.assertNotEqual(evaluationData.get_evaluation().Evaluation_Name[0], "Clean Accuracy")
        self.assertFalse(np.array_equal(actual_value, not_expected_value))