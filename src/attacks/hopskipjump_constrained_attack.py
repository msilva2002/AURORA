import zope.interface
from attacks.attack_interface import AttackI
from domain_data.perturbed_data import PerturbedData
from domain_data.model_data import ModelData
from art.attacks.evasion import HopSkipJump
import time
import pandas as pd
from attacks.attack_error_handler import AttackErrorHandler
from config.configuration import Configuration
from utils.utils import apply_constraints

@zope.interface.implementer(AttackI) 
class HopSkipJumpConstrainedAttack:
    _attackName = "HopSkipJumpConstrained"
    def execute(self, modeldata: ModelData) -> PerturbedData:
        data = modeldata.get_dataset()
        columns = modeldata.get_columns()
        model = modeldata.get_art_classifier()
        try:
            config = Configuration().get_config(attackName=self._attackName)
            categorical_features = config.get("categorical_features", None)
            integer_features = config.get("integer_features", None)
            data = data.to_numpy()
            config = {k: v for k, v in config.items() if k not in ['categorical_features', 'integer_features']}
            attack = HopSkipJump(classifier=model, targeted=False, verbose=True, **config )
            start = time.time()
            adversarial_data = attack.generate(x=data)
            adversarial_data = pd.DataFrame(adversarial_data, columns=columns)
            adversarial_data = apply_constraints(adversarial_data, categorical_features, integer_features)
            end = time.time()
            return PerturbedData(attackName=self._attackName, perturbations=pd.DataFrame(adversarial_data), run_time=end-start, targeted=False)
        except Exception as e:
            return AttackErrorHandler().handle_error(attackName=self._attackName, targeted=False, error=e)

'''
    def _apply_constraints(self, data, categorical_features, integer_features):
        patterns = categorical_features.split(",") if isinstance(categorical_features, str) else categorical_features
        for pattern in patterns:
            cols = get_features(data, pattern)
            numeric_group = data[cols].apply(lambda col: pd.to_numeric(col, errors='coerce'))
            numeric_group = numeric_group.fillna(0)
            
            max_col = numeric_group.idxmax(axis=1)

            one_hot = pd.DataFrame(0, index=data.index, columns=cols)
            for idx in data.index:
                one_hot.at[idx, max_col[idx]] = 1

            data[cols] = one_hot

        integer_features = integer_features.split(",") if isinstance(integer_features, str) else integer_features
        for feature in integer_features:
            print(f"Applying constraints for integer feature: {feature}")
            feature = feature.strip()
            if feature in data.columns:
                data[feature] = pd.to_numeric(data[feature], errors='coerce').round().astype('Int64')
        return data
'''

'''
feature = [0,0,0,0,0]
df = pd.DataFrame([feature], columns=['0_0', '0_1', '0_2', '0_3', '0_4'])
print(df)
print("====")
print(_apply_constraints(df, ['0_*'], []))
'''


