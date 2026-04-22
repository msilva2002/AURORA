import zope.interface
from attacks.attack_error_handler import AttackErrorHandler
from attacks.attack_interface import AttackI
from domain_data.model_data import ModelData
from domain_data.perturbed_data import PerturbedData
import time
import pandas as pd
from art.attacks.evasion import BoundaryAttack
from utils.revert_changes import revert_deleted_rows

@zope.interface.implementer(AttackI) 
class BoundaryAttackTargeted:
    _attackName = "BoundaryAttackTargeted"
    def execute(self, modeldata: ModelData, config) -> PerturbedData:
        data = modeldata.get_dataset()
        model = modeldata.get_art_classifier()
        target = modeldata.get_target()
        columns = modeldata.get_columns()
        try:
            data = data.compute().to_numpy()
            attack = BoundaryAttack(estimator=model, targeted=True, verbose=False, **config )
            start = time.time()
            adversarial_data = attack.generate(x=data, y=target)
            end = time.time()
            adversarial_data = pd.DataFrame(adversarial_data, columns=columns)
            data = modeldata.get_dataset().persist()
            data.columns = columns
            adversarial_data = revert_deleted_rows(data.compute(), adversarial_data)
            return PerturbedData(attackName=self._attackName, perturbations=pd.DataFrame(adversarial_data), run_time=end-start, targeted=True)
        except Exception as e:
            return AttackErrorHandler().handle_error(attackName=self._attackName, targeted=True, error=e)
