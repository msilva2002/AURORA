from domain_data.evaluation_data import EvaluationData
from evaluations.evaluation_attack_deterioration import AttackDeterioration
from evaluations.evaluation_attack_success_rate import AttackSuccessRate
from evaluations.evaluation_misclassification_rate import MisclassificationRate
from typing import List
import pandas as pd

#robustnessClasses = [AttackSuccessRate, MisclassificationRate, AttackDeterioration]

class RobustnessCalculator:

    def calculate_robustness(self, evaluationList : List[EvaluationData]):
        # for AttackSuccessRate, only the targeted attacks are considered
        # for MisclassificationRate, only the untargeted attacks are considered
        # for AttackDeterioration, all attacks are considered
        # using adjusted values for the metrics

        attackNameASR = AttackSuccessRate.evaluationName
        attackNameMR = MisclassificationRate.evaluationName
        attackNameAD = AttackDeterioration.evaluationName

        attackSuccessRate = []
        misclassificationRate = []
        attackDeterioration = []

        for evaluation in evaluationList:
            evalData = evaluation.get_evaluation()

            # Handle Attack Success Rate (for targeted attacks)
            if evaluation.is_targeted():
                name = "Da " + attackNameASR if AttackSuccessRate.adjustable else attackNameASR
                value = evalData.loc[evalData['Evaluation_Name'] == name, 'Value'].values
                attackSuccessRate.append(value[0] if value.size > 0 else 0)

            # Handle Misclassification Rate (for untargeted attacks)
            else:
                name = "Da " + attackNameMR if MisclassificationRate.adjustable else attackNameMR
                value = evalData.loc[evalData['Evaluation_Name'] == name, 'Value'].values
                misclassificationRate.append(value[0] if value.size > 0 else 0)

            # Handle Attack Deterioration (for all attacks)
            name = "Da " + attackNameAD if AttackDeterioration.adjustable else attackNameAD
            value = evalData.loc[evalData['Evaluation_Name'] == name, 'Value'].values
            attackDeterioration.append(value[0] if value.size > 0 else 0)

        # If no data collected, fallback to [0]
        if not attackSuccessRate:
            attackSuccessRate = [0]
        if not misclassificationRate:
            misclassificationRate = [0]
        if not attackDeterioration:
            attackDeterioration = [0]

        # Compute averages
        attack_success_rate_avg = sum(attackSuccessRate) / len(attackSuccessRate)
        misclassification_rate_avg = sum(misclassificationRate) / len(misclassificationRate)
        attack_deterioration_avg = sum(attackDeterioration) / len(attackDeterioration)

        # Calculate final robustness metrics
        attackSuccessRate_final = round(100 - attack_success_rate_avg * 100, 2)
        misclassificationRate_final = round(100 - misclassification_rate_avg * 100, 2)
        attackDeterioration_final = round(100 - attack_deterioration_avg * 100, 2)

        # Create pandas DataFrame with the **final values**
        results = pd.DataFrame([
            {"Evaluation_Name": attackNameASR, "Value": attackSuccessRate_final},
            {"Evaluation_Name": attackNameMR, "Value": misclassificationRate_final},
            {"Evaluation_Name": attackNameAD, "Value": attackDeterioration_final}
        ])

        return results


    def calculate_robustness_worst_case(self, evaluationList : List[EvaluationData]):
            # for AttackSuccessRate, only the targeted attacks are considered
            # for MisclassificationRate, only the untargeted attacks are considered
            # for AttackDeterioration, all attacks are considered
            # using adjusted values for the metrics
            # only the worst results (best attacks) are considered

            attackNameASR = AttackSuccessRate.evaluationName
            attackNameMR = MisclassificationRate.evaluationName
            attackNameAD = AttackDeterioration.evaluationName

            attackSuccessRate = 0
            misclassificationRate = 0
            attackDeterioration = 0

            for evaluation in evaluationList:
                evalData = evaluation.get_evaluation()

                # Handle Attack Success Rate (for targeted attacks)
                if evaluation.is_targeted():
                    name = "Da " + attackNameASR if AttackSuccessRate.adjustable else attackNameASR
                    value = evalData.loc[evalData['Evaluation_Name'] == name, 'Value'].values
                    value = (value[0] if value.size > 0 else 0)
                    if attackSuccessRate <= value:
                        attackSuccessRate = value
                    

                # Handle Misclassification Rate (for untargeted attacks)
                else:
                    name = "Da " + attackNameMR if MisclassificationRate.adjustable else attackNameMR
                    value = evalData.loc[evalData['Evaluation_Name'] == name, 'Value'].values
                    value = (value[0] if value.size > 0 else 0)
                    if misclassificationRate <= value:
                        misclassificationRate = value

                # Handle Attack Deterioration (for all attacks)
                name = "Da " + attackNameAD if AttackDeterioration.adjustable else attackNameAD
                value = evalData.loc[evalData['Evaluation_Name'] == name, 'Value'].values
                value = (value[0] if value.size > 0 else 0)
                if attackDeterioration <= value:
                    attackDeterioration = value
                

            # Calculate final robustness metrics
            attackSuccessRate_final = round(100 - attackSuccessRate * 100, 2)
            misclassificationRate_final = round(100 - misclassificationRate * 100, 2)
            attackDeterioration_final = round(100 - attackDeterioration * 100, 2)

            # Create pandas DataFrame with the **final values**
            results = pd.DataFrame([
                {"Evaluation_Name": attackNameASR, "Value": attackSuccessRate_final},
                {"Evaluation_Name": attackNameMR, "Value": misclassificationRate_final},
                {"Evaluation_Name": attackNameAD, "Value": attackDeterioration_final}
            ])

            return results
            

                    
                    


                

