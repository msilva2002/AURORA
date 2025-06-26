import zope.interface
from attacks.attack_error_handler import AttackErrorHandler
from attacks.attack_interface import AttackI
from domain_data.model_data import ModelData
from domain_data.perturbed_data import PerturbedData
from config.configuration import Configuration
import time

@zope.interface.implementer(AttackI) 
class AttackTemplate:
    _attackName = "Attack Name"
    def execute(self, modeldata: ModelData) -> PerturbedData:
        # retrive neccessary data from ModelData (columns, dataset, target, model)
        try:
            # convert data to numpy array if necessary
            # get configuration for the attack
            # initiate the attack and pass the configurations if necessary
            # start the timer
            start = time.time()
            # execute the attack, passing the target if necessary
            #adversarial_data = attack.generate(x=data)
            # end the timer
            end = time.time()
            # return the perturbed data
            #return PerturbedData(attackName=self._attackName, perturbations=pd.DataFrame(adversarial_data), run_time=end-start)
        except Exception as e:
            # in case of an error, handle it using the error handler
            return AttackErrorHandler().handle_error(attackName=self._attackName, targeted=False, error=e)
