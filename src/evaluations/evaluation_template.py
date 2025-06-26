import zope.interface
from evaluations.evaluation_interface import EvaluationI
from domain_data.evaluation_data import EvaluationData


@zope.interface.implementer(EvaluationI)
class EvaluationTemplate:

    evaluationName = "Evaluation Name"
    adjustable = False

    def execute(self, evaluationData : EvaluationData) -> EvaluationData:
        #try:
            # check if perturbation was targeted or not (can be necessary in some evaluations)
            # retrive necessary data from evaluationData
            # perform the evaluation
            # add the evaluation to the evaluationData
            #evaluationData.add_evaluation(self.evaluationName, evaluationResult)
        #except Exception as e:
        #    pass
        return evaluationData