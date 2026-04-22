from domain_data.model_data import ModelData
from typing import List
from domain_data.perturbed_data import PerturbedData

class ExecuteAttackService:
    def __init__(self, attackClasses, attackClassesTargeted):
        self.classes = []
        for attackClass in attackClasses + attackClassesTargeted:
            self.classes.append(attackClass())

        
    def execute(self, modelData: ModelData, attackClass, config)->PerturbedData:
        perturbed_data : PerturbedData = attackClass.execute(modelData, config)
        if perturbed_data.error == True:
            #self.statusManager.update_error(attackClass._attackName, perturbed_data.message)
            print(f"Error while executing {attackClass._attackName}: {perturbed_data.message}")
        else:
            perturbation = perturbed_data.get_perturbations()
            perturbation.columns = modelData.get_columns()
            from repositories.export_repository import ExportRepository
            ExportRepository().export_csv(perturbation, f"datasets/{attackClass._attackName}.csv")
            #self.statusManager.update_finish(attackClass._attackName, perturbation)
        return perturbed_data


    #def execute(self, modelData: ModelData)->List[PerturbedData]:
    #    perturbed_data_list : List[PerturbedData] = []
    #    for attackClass in self.classes:
    #        self.statusManager.update_run(attackClass._attackName)
    #        perturbed_data : PerturbedData = attackClass.execute(modelData)
    #        if perturbed_data.error == True:
    #            self.statusManager.update_error(attackClass._attackName, perturbed_data.message)
    #        else:
    #            self.statusManager.update_finish(attackClass._attackName)
    #        perturbed_data_list.append(perturbed_data)
    #    return perturbed_data_list