import zope.interface 
import pandas as pd
from typing import List

class QueryModelI(zope.interface.Interface): 
    def predict(self, df: pd.DataFrame) -> List[float]: 
        pass