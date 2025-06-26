import zope.interface
from attacks.attack_interface import AttackI
from domain_data.perturbed_data import PerturbedData
from domain_data.model_data import ModelData
from art.attacks.evasion import ProjectedGradientDescent
import time
import pandas as pd
from attacks.attack_error_handler import AttackErrorHandler
from config.configuration import Configuration

# Note: This method is not ready to be used, for there are some issues with the ART library and the targeted attack.

@zope.interface.implementer(AttackI) 
class ProjectedGradientDescentAttack:
    _attackName = "ProjectedGradientDescent"
    def execute(self, modeldata: ModelData) -> PerturbedData:
        data = modeldata.get_dataset()
        model = modeldata.get_art_classifier()
        try:
            data = data.to_numpy()
            config = Configuration().get_config(attackName=self._attackName)
            attack = ProjectedGradientDescent(estimator=model, targeted=False, verbose=True, **config)
            start = time.time()
            adversarial_data = attack.generate(x=data)
            end = time.time()
            return PerturbedData(attackName=self._attackName, perturbations=pd.DataFrame(adversarial_data), run_time=end-start)
        except Exception as e:
            print(f"Error in {self._attackName}: {e}")
            return AttackErrorHandler().handle_error(attackName=self._attackName, targeted=False, error=e)
