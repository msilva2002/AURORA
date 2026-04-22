import zope.interface
from attacks.attack_interface import AttackI
from domain_data.perturbed_data import PerturbedData
from domain_data.model_data import ModelData
from art.attacks.evasion import HopSkipJump
import time
import pandas as pd
from attacks.attack_error_handler import AttackErrorHandler

@zope.interface.implementer(AttackI) 
class HopSkipJumpAttack:
    _attackName = "HopSkipJump"
    def execute(self, modeldata: ModelData, config) -> PerturbedData:
        data = modeldata.get_dataset()
        model = modeldata.get_art_classifier()
        try:
            data = data.compute().to_numpy()
            attack = HopSkipJump(classifier=model, targeted=False, verbose=False, **config )
            start = time.time()
            adversarial_data = attack.generate(x=data)
            end = time.time()
            return PerturbedData(attackName=self._attackName, perturbations=pd.DataFrame(adversarial_data), run_time=end-start, targeted=False)
        except Exception as e:
            return AttackErrorHandler().handle_error(attackName=self._attackName, targeted=False, error=e)
