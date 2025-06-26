import zope.interface
from attacks.attack_interface import AttackI
from domain_data.perturbed_data import PerturbedData
from domain_data.model_data import ModelData
from art.attacks.evasion import CarliniL2Method
import time
import pandas as pd
from attacks.attack_error_handler import AttackErrorHandler
from config.configuration import Configuration

@zope.interface.implementer(AttackI) 
class CarliniWagnerAttack:
    _attackName = "CarliniWagner"
    def execute(self, modeldata: ModelData) -> PerturbedData:
        data = modeldata.get_dataset()
        model = modeldata.get_art_classifier()
        try:
            data = data.to_numpy()
            config = Configuration().get_config(attackName=self._attackName)
            attack = CarliniL2Method(classifier=model, targeted=False, verbose=True, **config)
            start = time.time()
            adversarial_data = attack.generate(x=data)
            end = time.time()
            return PerturbedData(attackName=self._attackName, perturbations=pd.DataFrame(adversarial_data), run_time=end-start)
        except Exception as e:
            return AttackErrorHandler().handle_error(attackName=self._attackName, targeted=False, error=e)
