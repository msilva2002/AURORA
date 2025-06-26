import unittest
from domain_data.perturbed_data import PerturbedData
from evaluations.evaluation_clean_accuracy import CleanAccuracy
from evaluations.evaluation_misclassification_rate import MisclassificationRate
from evaluations.evaluation_attack_success_rate import AttackSuccessRate
from evaluations.evaluation_confusion_matrix import ConfusionMatrix
from evaluations.evaluation_adversarial_accuracy import AdversarialAccuracy
from domain_data.evaluation_data import EvaluationData
import pandas as pd

class TestCleanAccuracy(unittest.TestCase):
    def setUp(self):
        true_labels = pd.DataFrame([0, 1, 2, 3, 0, 1, 2, 3, 0, 1])
        predicted_clean_labels = pd.DataFrame([0, 1, 0, 3, 0, 1, 0, 3, 0, 1])
        predicted_perturbed_labels = pd.DataFrame([0, 1, 0, 3, 0, 1, 0, 3, 0, 1])
        target = pd.DataFrame([1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        perturbedData = PerturbedData(None, None, None, True, "", False)

        self.evalData = EvaluationData(perturbedData, true_labels, predicted_clean_labels, predicted_perturbed_labels, target)

    def test_return_size(self):
        print("Testing evaluation return size")
        self.evalData = CleanAccuracy().execute(self.evalData)
        self.evalData = MisclassificationRate().execute(self.evalData)
        

        self.assertTrue(len(self.evalData.get_evaluation().Evaluation_Name) == 2)
        self.assertTrue(len(self.evalData.get_evaluation().Value) == 2)

        self.evalData = AttackSuccessRate().execute(self.evalData)
        self.evalData = ConfusionMatrix().execute(self.evalData)
        self.evalData = AdversarialAccuracy().execute(self.evalData)

        self.assertTrue(len(self.evalData.get_evaluation().Evaluation_Name) == 5)
        self.assertTrue(len(self.evalData.get_evaluation().Value) == 5)

        self.assertFalse(None in self.evalData.get_evaluation().Value)

        self.evalData.is_targeted = False
        self.evalData = AttackSuccessRate().execute(self.evalData)
        # none was added to the evaluation
        self.assertTrue(len(self.evalData.get_evaluation().Value) == 5)

