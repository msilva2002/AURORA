from domain_data.evaluation_data import EvaluationData
from domain_data.model_data import ModelData
from typing import List
from distances.distance_calculator import calculate_distance, calculate_threshold
from config.data_configuration import DataConfiguration
from utils.utils import get_successful_adversarial_samples

def adjust_metrics(evalData : EvaluationData, evalClasses, modelData : ModelData):  

    eval_df = evalData.get_evaluation()
    original_df = modelData.get_dataset()
    original_df.columns = modelData.get_columns()
    perturbed_df = evalData.get_perturbed_dataframe()

    categorical = DataConfiguration().get_config(df_init=original_df)

    # get the successful adversarial samples
    df_init_successful, df_perturbed_successful = get_successful_adversarial_samples(original_df, perturbed_df, evalData.get_predicted_clean_labels(), evalData.get_predicted_perturbed_labels())
    distance_perturbation = calculate_distance(original=df_init_successful, perturbed=df_perturbed_successful, categorical_features=categorical)
    threshold = calculate_threshold(original=original_df, categorical_features=categorical)
    adjustment = calculate_adjustment(distance_perturbation, threshold)

    for evalClass in evalClasses:
        if evalClass.adjustable == True:
            # check if the evalClass.name is in evalData
            attackName = evalClass.evaluationName
            if attackName not in eval_df["Evaluation_Name"].values:
                continue
            # get the original metric value
            original_metric = eval_df.loc[eval_df["Evaluation_Name"] == attackName, "Value"].values[0]
            # get the adjusted metric value
            metric_adjusted = original_metric * adjustment
            if metric_adjusted < 0:
                metric_adjusted = 0
            evalData.add_evaluation("Da " + attackName, metric_adjusted)   
    return evalData

def calculate_adjustment(distance_perturbation, threshold):
    x = max(0, distance_perturbation - threshold)

    if x == 0:
        return 1 - (0)
    elif x <= threshold:
        return 1 - ((0.9*x)/threshold)
    else:
        return 1 - (1 - (threshold/(20*(x - (threshold/2)))))