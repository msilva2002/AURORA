import unittest
from evaluations.evaluation_adversarial_accuracy import AdversarialAccuracy
from domain_data.evaluation_data import EvaluationData
from domain_data.perturbed_data import PerturbedData
import pandas as pd

class TestAdversarialAccuracy(unittest.TestCase):
    def setUp(self):
        true_labels = pd.DataFrame([0, 1, 2, 3, 0, 1, 2, 3, 0, 1])
        predicted_perturbed_labels = pd.DataFrame([0, 1, 0, 3, 0, 1, 0, 3, 0, 1])

        perturbedData = PerturbedData(None, None, None, False, "", False)

        self.evalData = EvaluationData(perturbedData, true_labels, None, predicted_perturbed_labels, None)

    def test_adversarial_accuracy_correct(self):
        print("Testing Adversarial Accuracy")
        evaluationData : EvaluationData = AdversarialAccuracy().execute(self.evalData)
        self.assertEqual(evaluationData.get_evaluation().Evaluation_Name[0], "Adversarial Accuracy")
        self.assertEqual(evaluationData.get_evaluation().Value[0], 0.8)

        self.assertNotEqual(evaluationData.get_evaluation().Evaluation_Name[0], "Clean Accuracy")
        self.assertNotEqual(evaluationData.get_evaluation().Value[0], 0.7)

    def test_adversarial_accuracy_no_true_labels(self):
        print("Testing Adversarial Accuracy with no true labels")
        self.evalData.true_labels = None
        evaluationData : EvaluationData = AdversarialAccuracy().execute(self.evalData)
        # evaluationData.get_evaluation() should be an empty DataFrame
        self.assertEqual(evaluationData.get_evaluation().empty, True)
        