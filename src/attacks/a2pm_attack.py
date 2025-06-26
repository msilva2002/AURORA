import zope.interface
from attacks.attack_interface import AttackI
from domain_data.perturbed_data import PerturbedData
from domain_data.model_data import ModelData
from a2pm import A2PMethod
import time
import pandas as pd
from attacks.attack_error_handler import AttackErrorHandler
from utils.a2pm_pattern_util import get_patterns
from config.configuration import Configuration

@zope.interface.implementer(AttackI) 
class A2PMAttack:
    _attackName = "A2PM"

    def execute(self, modeldata: ModelData) -> PerturbedData:
        data = modeldata.get_dataset()
        labels = modeldata.get_labels()
        columns = modeldata.get_columns()
        model = modeldata.get_a2pm_classifier()

        data.columns = columns
        try:
            config = Configuration().get_config(attackName=self._attackName)
            pattern = get_patterns(data, config["patterns"])
            attack = A2PMethod(pattern=pattern, seed=42)
            attack = attack.fit(X=data, y=labels)
            start = time.time()
            adversarial_data = attack.generate(classifier=model, X=data, y=labels)
            end = time.time()
            return PerturbedData(attackName=self._attackName, perturbations=pd.DataFrame(adversarial_data), run_time=end-start)
        except Exception as e:
            return AttackErrorHandler().handle_error(attackName=self._attackName, targeted=False, error=e)           