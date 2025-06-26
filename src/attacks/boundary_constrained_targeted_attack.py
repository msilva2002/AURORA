import zope.interface
from attacks.attack_error_handler import AttackErrorHandler
from attacks.attack_interface import AttackI
from domain_data.model_data import ModelData
from domain_data.perturbed_data import PerturbedData
from config.configuration import Configuration
import time
import pandas as pd
from art.attacks.evasion import BoundaryAttack
from utils.utils import apply_constraints
from utils.revert_changes import revert_deleted_rows

@zope.interface.implementer(AttackI) 
class BoundaryConstrainedAttackTargeted:
    _attackName = "BoundaryConstrainedAttackTargeted"
    def execute(self, modeldata: ModelData) -> PerturbedData:
        data = modeldata.get_dataset()
        model = modeldata.get_art_classifier()
        columns = modeldata.get_columns()
        target = modeldata.get_target()
        try:
            config = Configuration().get_config(attackName=self._attackName)
            categorical_features = config.get("categorical_features", None)
            integer_features = config.get("integer_features", None)
            data = data.to_numpy()
            config = {k: v for k, v in config.items() if k not in ['categorical_features', 'integer_features']}
            attack = BoundaryAttack(estimator=model, targeted=True, verbose=True, **config )
            start = time.time()
            adversarial_data = attack.generate(x=data, y=target)
            adversarial_data = pd.DataFrame(adversarial_data, columns=columns)
            data = modeldata.get_dataset()
            data.columns = columns
            adversarial_data = revert_deleted_rows(data, adversarial_data)
            adversarial_data = apply_constraints(adversarial_data, categorical_features, integer_features)
            end = time.time()
            return PerturbedData(attackName=self._attackName, perturbations=pd.DataFrame(adversarial_data), run_time=end-start, targeted=True)
        except Exception as e:
            return AttackErrorHandler().handle_error(attackName=self._attackName, targeted=True, error=e)
