import zope.interface 
from domain_data.evaluation_data import EvaluationData


class EvaluationI(zope.interface.Interface): 
    def execute(self, evaluationData : EvaluationData) -> EvaluationData:
        pass