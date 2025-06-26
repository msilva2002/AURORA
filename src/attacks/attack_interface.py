import zope.interface 
import pandas as pd
from domain_data.perturbed_data import PerturbedData
from domain_data.model_data import ModelData
from typing import List

class AttackI(zope.interface.Interface): 
    def execute(self, modeldata: ModelData ) -> PerturbedData: 
        pass