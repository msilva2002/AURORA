import zope.interface
from attacks.attack_interface import AttackI
from domain_data.perturbed_data import PerturbedData
from domain_data.model_data import ModelData
from art.attacks.evasion import HopSkipJump
import time
import pandas as pd
from attacks.attack_error_handler import AttackErrorHandler
from utils.utils import apply_constraints

@zope.interface.implementer(AttackI) 
class HopSkipJumpConstrainedAttack:
    _attackName = "HopSkipJumpConstrained"
    def execute(self, modeldata: ModelData, config) -> PerturbedData:
        data = modeldata.get_dataset()
        columns = modeldata.get_columns()
        model = modeldata.get_art_classifier()
        try:
            categorical_features = config.get("categorical_features", None)
            integer_features = config.get("integer_features", None)
            data = data.compute().to_numpy()
            config = {k: v for k, v in config.items() if k not in ['categorical_features', 'integer_features']}
            attack = HopSkipJump(classifier=model, targeted=False, verbose=False, **config )
            start = time.time()
            adversarial_data = attack.generate(x=data)
            adversarial_data = pd.DataFrame(adversarial_data, columns=columns)
            adversarial_data = apply_constraints(adversarial_data, categorical_features, integer_features)
            end = time.time()
            return PerturbedData(attackName=self._attackName, perturbations=pd.DataFrame(adversarial_data), run_time=end-start, targeted=False)
        except Exception as e:
            return AttackErrorHandler().handle_error(attackName=self._attackName, targeted=False, error=e)



