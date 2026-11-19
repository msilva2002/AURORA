from repositories.clear_repository import ClearRepository
from repositories.import_repository import ImportRepository
from repositories.export_repository import ExportRepository
from domain_data.model_data import ModelData
from domain_data.evaluation_data import EvaluationData
from typing import List
from reports.image_report import ImageGenerator
import re
import pandas as pd
from distances.distance_calculator import get_penalty, calculate_threshold, calculate_distance
from robustness.robustness_calculation import RobustnessCalculator

IMAGE_FOLDER = "evaluation_report/images/"  # Folder to store images
REPORT_NAME = "evaluation_report/report.md"  # Name of the report file
ZIP_NAME = "evaluation_report/report.zip"  # Name of the zip file

class ReportCreator:
    def __init__(self):
        # clear previous report data and images
        ClearRepository().clear_folder(IMAGE_FOLDER)
        ClearRepository().clear_file(REPORT_NAME)
        ClearRepository().clear_file(ZIP_NAME)


    def generate_report(self, modelData : ModelData, evalList : List[EvaluationData], perturbationMethods , metrics):
        # generate images for each evaluation
        self._generate_images(modelData, evalList)
        # create structured report
        self._create_structured_report(modelData, evalList, perturbationMethods, metrics)


    def _create_structured_report(self, modelData : ModelData, evalList : List[EvaluationData], perturbationMethods, metrics):
        df_init = modelData.get_dataset()
        columns = modelData.get_columns()
        df_init.columns = columns
        categorical = modelData.get_config()
        
        results_table = []
        results_table.append("### Evaluation Results")
        #| Metric | T | C | CA | AA | ASR | MR | AD | TR | **DA / ASR** | **DA / MR** | **D** |
        header = "| Method | Targeted | Constrained | Distance | Treshold | Penalty |"
        for metricClass in metrics:
            try:
                metric = metricClass.evaluationName
                if str(metric).lower() == "confusion matrix":
                    continue
                metric = "".join([word[0] for word in metric.split()])
            except:
                continue
            header += f" {metric} |"
        
        for metricClass in metrics:
            try:
                adjustable = metricClass.adjustable
                if adjustable == True:
                    text = "Distance Adjusted "+metricClass.evaluationName
                    extracted_value = "".join([word[0] for word in text.split()])
                    header += f" {extracted_value} |"
            except:
                continue
        results_table.append(header)
        header_line = header.split(" | ")
        
        separator_item = ":---:"
        line = "| "
        list_of_separators = [separator_item] * len(header_line)
        line += " | ".join(list_of_separators)
        line += " |"
        results_table.append(line)

        for eval in evalList:
            if eval.get_evaluation() is None:
                continue
            
            name = eval.get_perturbedData().attackName
            targeted = "❌"
            constrained = "❌"
            if "targeted" in str(name).lower():
                name = re.sub(r'targeted', '', name, flags=re.IGNORECASE)
                name = re.sub(r'\s+', ' ', name).strip()
                targeted = "✅"
            if "constrained" in str(name).lower():
                name = re.sub(r'constrained', '', name, flags=re.IGNORECASE)
                name = re.sub(r'\s+', ' ', name).strip()
                constrained = "✅"
            
            line = f"| {name} | {targeted} | {constrained} |"

            df_pert = eval.get_perturbed_dataframe()
            df_pert.columns = modelData.get_columns()
            from utils.utils import get_successful_adversarial_samples
            df_init_successful, df_perturbed_successful = get_successful_adversarial_samples(df_init=df_init, df_pert=df_pert, y_init=eval.get_predicted_clean_labels(), y_pert=eval.get_predicted_perturbed_labels())


            numerical_features = list(set(df_init.columns) - {item for sublist in categorical for item in sublist})

            norm_params = {
            col: {
                "min": df_init[col].min(),
                "max": df_init[col].max()
                }
                for col in numerical_features
            }

            #threshold = calculate_threshold(df_init, categorical)

            threshold = calculate_threshold(df_init_successful, categorical, norm_params)
            

            distance = calculate_distance(df_init_successful, df_perturbed_successful, categorical, norm_params)
            penalty = get_penalty(df_init_successful, categorical, norm_params)

            import numpy as np
            if np.isnan(distance):
                distance = 0.0
            if np.isnan(threshold):
                threshold = 0.0
            if np.isnan(penalty):
                penalty = 0.0

            line += f" {distance} | {threshold} | {penalty} |"

            metrics_header = header.split("|")
            # remove first 6 hits
            metrics_header = metrics_header[7:]
            for metric in metrics_header:
                exist = False
                for _, row in eval.get_evaluation().iterrows():
                    metric_name = row["Evaluation_Name"]
                    metric_name = "".join([word[0] for word in metric_name.split()])
                    if str(metric).replace("|","").replace(" ","") == metric_name:
                        value = row["Value"]
                        if metric_name != "TR":
                            value = f"{value * 100:.2f}%"
                        else:
                            value = f"{value:.2f}"
                        line += f" {value} |"
                        exist = True
                        break
                if exist == False:
                    line += f" - |"

            results_table.append(line)
        
        robustness_eval = []
        robustness_eval.append("## Robustness Evaluation")

        robustness_eval.append("81-100: Very robust.\n")
        robustness_eval.append("61-80: Robust.\n")
        robustness_eval.append("41-60: Moderately robust.\n")
        robustness_eval.append("21-40: Weakly robust.\n")
        robustness_eval.append("0-20: Not robust.\n")

        robustnessCalculator = RobustnessCalculator()
        robustness = robustnessCalculator.calculate_robustness(evalList)
        ImageGenerator(IMAGE_FOLDER).generate_robustness(robustness, "robustness.png")
        listImages = ImportRepository().get_png_from_folder(IMAGE_FOLDER, "robustness.png")
        for image in listImages:
            robustness_eval.append(f"![{image}]({image})\n")
        
        robustAvg = sum(robustness["Value"]) / len(robustness["Value"])
        robustAvg = int(round(float(robustAvg), 0))

        thresholds_robustness = [0, 21, 41, 61, 81]
        labels_robustness = ["Not robust.", "Weakly robust.", "Moderately robust.", "Robust.", "Very robust."]
        import bisect
        idx = bisect.bisect_right(thresholds_robustness, robustAvg) - 1
        robustness_label = labels_robustness[idx]
        robustness_eval.append(f"###### Robustness score: {robustAvg} - {robustness_label}")

        robustness_eval.append("---\n")

        robustness = robustnessCalculator.calculate_robustness_worst_case(evalList)
        ImageGenerator(IMAGE_FOLDER).generate_robustness(robustness, "robustness_worst_case.png")
        listImages = ImportRepository().get_png_from_folder(IMAGE_FOLDER, "robustness_worst_case")
        for image in listImages:
            robustness_eval.append(f"![{image}]({image})\n")

        robustAvg = sum(robustness["Value"]) / len(robustness["Value"])
        robustAvg = round(float(robustAvg), 0)
        idx = bisect.bisect_right(thresholds_robustness, robustAvg) - 1
        robustness_label = labels_robustness[idx]
        robustness_eval.append(f"###### Robustness score worst case scenario: {robustAvg} - {robustness_label}")

        attack_specific = []
        for eval in evalList:
            if eval.get_evaluation() is None:
                continue
            attack_specific.append(f"## {eval.get_perturbedData().attackName}\n")

            attack_specific.append(f"#### Confusion Matrix")

            metric_name = eval.get_evaluation().loc[eval.get_evaluation()["Evaluation_Name"] == "Confusion Matrix"]
            metric_value = metric_name.iloc[0]["Value"]

            num_classes = metric_value.shape[0]
            labels = [str(i) for i in range(num_classes)]  # Use numeric class indices

            # Header
            header = "| Actual \\ Predicted | " + " | ".join(labels) + " |"
            separator = "|" + "---|" * (num_classes + 1)

            attack_specific.append(header)
            attack_specific.append(separator)

            # Rows
            for i in range(num_classes):
                row = "| " + labels[i] + " | " + " | ".join([str(metric_value[i][j]) for j in range(num_classes)]) + " |"
                attack_specific.append(row)

            #markdown_lines.append("The following images show the variation between each value within the categorical features. A higher value indicates a higher rate of modification of the value, while a lower value indicates a lower rate of modification of the value.\nThe total sum between all the values for a categorical feature should be always less or equal to the number of rows in the dataset. If this is not true, then the method for generating the perturbations does not aqquaint for categorical features logic and can change values at will.\n") 
            listImages = ImportRepository().get_png_from_folder(IMAGE_FOLDER , "independent_categorical_feature_" + eval.get_perturbedData().attackName+"_")
            if listImages:
                attack_specific.append(f"#### Variation between each value within the categorical features\n")
                for image in listImages:
                    attack_specific.append(f"![{image}]({image})")
                    attack_specific.append("---\n")

            
            #text = "A red line indicates that atleast one of the values is not possible for the categorical feature, by either not being 0 or 1. A black line indicates that the value is possible for the categorical feature.\nThe average values and the value count should have a proportional representation, meaning that if the average value is 0,5, then the value count should be 50% of the total number of rows in the dataset. If this is not true, then the method for generating the perturbations does not aqquaint for categorical features logic and can change values at will. The total sum of value counts should be less or equal to the number of rows in the dataset.\n"
            #markdown_lines.append(text)
            listImagesOriginal = ImportRepository().get_png_from_folder(IMAGE_FOLDER , "original_category_")
            listImagesPerturbed = ImportRepository().get_png_from_folder(IMAGE_FOLDER , "perturbed_category_" + eval.get_perturbedData().attackName+"_")
            if listImagesPerturbed:
                attack_specific.append(f"#### Comparison of Normal and Perturbed Results for Categorical Features\n")
                for i in range(len(listImagesOriginal)):
                    attack_specific.append("Original data")
                    attack_specific.append(f"![{listImagesOriginal[i]}]({listImagesOriginal[i]})\n")
                    attack_specific.append("Perturbed data")
                    attack_specific.append(f"![{listImagesPerturbed[i]}]({listImagesPerturbed[i]})")
                    attack_specific.append("---\n")
                
            #text = "The values shown represent the scaled difference of values for each numerical feature. If a number appears on the top left corner, it means that the value if on that scale (for example, 1e-6 means 0.000001).\n"
            #attack_specific.append(text)
            listImagesOriginal = ImportRepository().get_png_from_folder(IMAGE_FOLDER , "numerical_features_original")
            listImages = ImportRepository().get_png_from_folder(IMAGE_FOLDER, "numerical_features_perturbed_" + eval.get_perturbedData().attackName+".")
            if listImages:
                attack_specific.append(f"#### Comparison of Normal and Perturbed Results for Numerical Features\n")
                for i in range(len(listImages)):
                    attack_specific.append("Original data")
                    attack_specific.append(f"![{listImagesOriginal[i]}]({listImagesOriginal[i]})\n")
                    attack_specific.append("Perturbed data")
                    attack_specific.append(f"![{listImages[i]}]({listImages[i]})")
                    attack_specific.append("---\n")

        markdown_lines = results_table + robustness_eval + attack_specific
        if ExportRepository().export_md(markdown_lines, REPORT_NAME):
            ExportRepository().create_zip_file_folder(file_path=REPORT_NAME, folder_path=IMAGE_FOLDER, zip_path=ZIP_NAME)


    def _generate_images(self, modelData : ModelData, evalList : List[EvaluationData]):
        df_init = modelData.get_dataset()
        columns = modelData.get_columns()
        df_init.columns = columns

        category_features = modelData.get_config()
        # generate necessary images for each evaluation
        imageGenerator = ImageGenerator(IMAGE_FOLDER)

        for evalData in evalList:
            if evalData.get_perturbedData().error:
                continue
            i = 0
            # generate images for categorical features
            for feature_combination in category_features:
                imageGenerator.generate_categorical(evalData, modelData, feature_combination, i)
                i += 1
            # generate images for numerical features
            imageGenerator.generate_numerical(evalData, modelData, category_features)

        