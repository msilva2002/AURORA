from domain_data.model_data import ModelData
from domain_data.perturbed_data import PerturbedData
from services.execute_attack_service import ExecuteAttackService
from services.execute_evaluation_service import ExecuteEvaluationService
import warnings
warnings.filterwarnings("ignore")

from attacks.hopskipjump_attack import HopSkipJumpAttack
from attacks.hopskipjump_constrained_attack import HopSkipJumpConstrainedAttack
from attacks.hopskipjump_targeted_attack import HopSkipJumpAttackTargeted
from attacks.hopskipjump_constrained_targeted_attack import HopSkipJumpAttackConstrainedTargeted
from attacks.zoo_attack import ZerothOrderOptimizationAttack
from attacks.zoo_constrained_attack import ZerothOrderOptimizationConstrainedAttack
from attacks.zoo_targeted_attack import ZerothOrderOptimizationAttackTargeted
from attacks.zoo_constrained_targeted_attack import ZerothOrderOptimizationConstrainedAttackTargeted
from attacks.cw_attack import CarliniWagnerAttack
from attacks.cw_constrained_attack import CarliniWagnerConstrainedAttack
from attacks.cw_targeted_attack import CarliniWagnerAttackTargeted
from attacks.cw_constrained_targeted_attack import CarliniWagnerConstrainedAttackTargeted
from attacks.a2pm_attack import A2PMAttack
from attacks.a2pm_targeted_attack import A2PMAttackTargeted
#from attacks.pgd_attack import ProjectedGradientDescentAttack
#from attacks.pgd_targeted_attack import ProjectedGradientDescentAttackTargeted
from attacks.boundary_attack import BoundaryAttackClass as BoundaryAttack
from attacks.boundary_constrained_attack import BoundaryConstrainedAttack
from attacks.boundary_targeted_attack import BoundaryAttackTargeted
from attacks.boundary_constrained_targeted_attack import BoundaryConstrainedAttackTargeted

from evaluations.evaluation_clean_accuracy import CleanAccuracy
from evaluations.evaluation_adversarial_accuracy import AdversarialAccuracy
from evaluations.evaluation_attack_success_rate import AttackSuccessRate
from evaluations.evaluation_misclassification_rate import MisclassificationRate
from evaluations.evaluation_confusion_matrix import ConfusionMatrix
from evaluations.evaluation_time import EvaluationTime
from evaluations.evaluation_attack_deterioration import AttackDeterioration
from reports.report import ReportCreator

attackClasses = [A2PMAttack, 
                 BoundaryAttack, BoundaryConstrainedAttack, 
                 CarliniWagnerAttack, CarliniWagnerConstrainedAttack,
                 HopSkipJumpAttack, HopSkipJumpConstrainedAttack,
                 ZerothOrderOptimizationAttack, ZerothOrderOptimizationConstrainedAttack]

attackClassesTargeted = [A2PMAttackTargeted, 
                         BoundaryAttackTargeted, BoundaryConstrainedAttackTargeted, 
                         CarliniWagnerAttackTargeted, CarliniWagnerConstrainedAttackTargeted,
                         HopSkipJumpAttackTargeted, HopSkipJumpAttackConstrainedTargeted,
                         ZerothOrderOptimizationAttackTargeted, ZerothOrderOptimizationConstrainedAttackTargeted]

evaluationClasses = [CleanAccuracy, AdversarialAccuracy, AttackSuccessRate, 
                     MisclassificationRate, AttackDeterioration, ConfusionMatrix, EvaluationTime]


def clear_folders():
    import os
    dir_path = os.path.dirname(os.path.abspath(__file__))
    from services.clear_service import ClearService
    ClearService().clear_folder(path=dir_path+"/../datasets/")
    ClearService().clear_file(path=dir_path+"/../evaluation_report/report.zip")
    ClearService().clear_file(path=dir_path+"/../evaluation_report/report.md")
    ClearService().clear_folder(path=dir_path+"/../evaluation_report/images/")



def start_attack_sequence(modelData : ModelData, config):
    attack_service = ExecuteAttackService(attackClasses=attackClasses, attackClassesTargeted=attackClassesTargeted)
    try:
        for attack in attack_service.classes:
            if attack._attackName == config["attackName"]:
                config.pop('attackName')
                pertubedData = attack_service.execute(modelData=modelData, attackClass=attack, config=config)
                return pertubedData
    except Exception as e:
        print(f"An error occured: {e}")
        return None

def start_evaluation_sequence(modelData : ModelData, perturbedDataList : list[PerturbedData]):
    evaluation_service = ExecuteEvaluationService(evaluationClasses=evaluationClasses, modelData=modelData)
    evalList = []
    for i in perturbedDataList:
        evaluation = evaluation_service.execute(modelData=modelData, perturbedData=i)
        print(i.attackName)
        if evaluation is not None:
            evalList.append(evaluation)
    ReportCreator().generate_report(modelData=modelData, evalList=evalList, perturbationMethods=attackClasses + attackClassesTargeted, metrics=evaluationClasses)
