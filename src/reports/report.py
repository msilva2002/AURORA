from repositories.clear_repository import ClearRepository
from repositories.import_repository import ImportRepository
from repositories.export_repository import ExportRepository
from domain_data.model_data import ModelData
from domain_data.evaluation_data import EvaluationData
from typing import List
from config.data_configuration import DataConfiguration
from reports.image_report import ImageGenerator
import re
import pandas as pd
from distances.distance_calculator import PENALTY, calculate_threshold, calculate_distance
from robustness.robustness_calculation import RobustnessCalculator
from managers.status_manager import StatusManager

IMAGE_FOLDER = "reports/images/"  # Folder to store images
REPORT_NAME = "reports/report.md"  # Name of the report file
ZIP_NAME = "reports/report.zip"  # Name of the zip file

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
        StatusManager().set_report_ready()


    def slugify(self, text):
        text = text.strip().lower()
        text = re.sub(r"[^\w\s-]", "", text)      # Remove punctuation
        text = re.sub(r"\n", "", text)          # Remove newlines
        return re.sub(r"\s+", "%20", text)          # Replace spaces with hyphens

       
    def _create_structured_report(self, modelData : ModelData, evalList : List[EvaluationData], perturbationMethods, metrics):
        df_init = modelData.get_dataset()
        columns = modelData.get_columns()
        df_init.columns = columns
        categorical = DataConfiguration().get_config(df_init=df_init)
        
        markdown_lines = []
        headings = [("##", "Index")]
        markdown_lines.append("## Index\n")
        markdown_lines.append("_index_placeholder_\n")
        ##########    
        headings.append(("##", "Perturbation Methods Available"))
        markdown_lines.append("## Perturbation Methods Available\n")
        for perturbationClass in perturbationMethods:
            try:
                attack = perturbationClass._attackName
            except:
                continue
            markdown_lines.append(f"###### {attack}\n")
            #try:
            #    description = perturbationClass._description
            #except:
            #    description = "No description available"
            #markdown_lines.append(f"- Description: {description}\n")
            markdown_lines.append("---\n")
        ##########    
        headings.append(("##", "Evaluation Metrics Available"))
        markdown_lines.append("## Evaluation Metrics Available\n")
        for metricClass in metrics:
            try:
                metric = metricClass.evaluationName
            except:
                continue
            markdown_lines.append(f"###### {metric}\n")
            #try:
            #    description = metricClass.description
            #except:
            #    description = "No description available"
            #markdown_lines.append(f"- Description: {description}\n")
            try:
                adjustable = metricClass.adjustable
            except:
                adjustable = False
            if adjustable:
                markdown_lines.append(f"- This metric is adjustable")
            else:
                markdown_lines.append(f"- This metric is not adjustable")
            markdown_lines.append("---\n")
        ########## 
        headings.append(("##", "Distance Adjustment"))
        markdown_lines.append("## Distance Adjustment\n")
        text = "As most of the adversarial methods generate perturbations without any regard for the realistic component of tabular data, namely the presence of categorical features, these values can take values that are either too wildish, or even impossible. To take matters to our hands, AURORA employes a Distance Adjustement (DA) to some features, which makes interpretying the metrics more accurate to the actual data.\n"
        markdown_lines.append(text)
        markdown_lines.append("---\n")
        ##########
        for eval in evalList:
            if eval.get_evaluation() is None:
                continue
            headings.append(("##", eval.get_perturbedData().attackName))
            markdown_lines.append(f"## {eval.get_perturbedData().attackName}\n")

            headings.append(("###", "Variation between each value within the categorical features"))
            markdown_lines.append(f"### Variation between each value within the categorical features\n")
            markdown_lines.append("The following images show the variation between each value within the categorical features. A higher value indicates a higher rate of modification of the value, while a lower value indicates a lower rate of modification of the value.\nThe total sum between all the values for a categorical feature should be always less or equal to the number of rows in the dataset. If this is not true, then the method for generating the perturbations does not aqquaint for categorical features logic and can change values at will.\n") 
            listImages = ImportRepository().get_png_from_folder(IMAGE_FOLDER , "independent_categorical_feature_" + eval.get_perturbedData().attackName+"_")
            for image in listImages:
                markdown_lines.append(f"![{image}]({image})")
                markdown_lines.append("---\n")

            headings.append(("###", "Comparison of Normal and Perturbed Results for Categorical Features"))
            markdown_lines.append(f"### Comparison of Normal and Perturbed Results for Categorical Features\n")
            text = "A red line indicates that atleast one of the values is not possible for the categorical feature, by either not being 0 or 1. A black line indicates that the value is possible for the categorical feature.\nThe average values and the value count should have a proportional representation, meaning that if the average value is 0,5, then the value count should be 50% of the total number of rows in the dataset. If this is not true, then the method for generating the perturbations does not aqquaint for categorical features logic and can change values at will. The total sum of value counts should be less or equal to the number of rows in the dataset.\n"
            markdown_lines.append(text)
            listImagesOriginal = ImportRepository().get_png_from_folder(IMAGE_FOLDER , "original_category_")
            listImagesPerturbed = ImportRepository().get_png_from_folder(IMAGE_FOLDER , "perturbed_category_" + eval.get_perturbedData().attackName+"_")
            for i in range(len(listImagesOriginal)):
                markdown_lines.append("Original data")
                markdown_lines.append(f"![{listImagesOriginal[i]}]({listImagesOriginal[i]})\n")
                markdown_lines.append("Perturbed data")
                markdown_lines.append(f"![{listImagesPerturbed[i]}]({listImagesPerturbed[i]})")
                markdown_lines.append("---\n")
            
            headings.append(("###", "Comparison of Normal and Perturbed Results for Numerical Features"))
            markdown_lines.append(f"### Comparison of Normal and Perturbed Results for Numerical Features\n")
            text = "The values shown represent the scaled difference of values for each numerical feature. If a number appears on the top left corner, it means that the value if on that scale (for example, 1e-6 means 0.000001).\n"
            markdown_lines.append(text)
            listImages = ImportRepository().get_png_from_folder(IMAGE_FOLDER, "numerical_features_" + eval.get_perturbedData().attackName+".")
            for image in listImages:
                markdown_lines.append(f"![{image}]({image})\n")

            headings.append(("###", "Statistics of Original and Perturbed Data"))
            markdown_lines.append(f"### Statistics of Original and Perturbed Data\n")

            stats_init = self._get_stats(df_init)
            df_pert = eval.get_perturbed_dataframe()
            df_pert.columns = modelData.get_columns()
            stats_pert = self._get_stats(df_pert)

            # create a table with the statistics
            markdown_lines.append("| Feature | Original Max | Perturbed Max | Original Min | Perturbed Min | Original Median | Perturbed Median | Original Average | Perturbed Average |")
            markdown_lines.append("|---------|--------------|---------------|--------------|----------------|------------------|-------------------|-------------------|--------------------|")

            # Add each row
            for feature in modelData.get_columns():
                original_max = stats_init.loc[feature, 'Max']
                perturbed_max = stats_pert.loc[feature, 'Max']
                original_min = stats_init.loc[feature, 'Min']
                perturbed_min = stats_pert.loc[feature, 'Min']
                original_median = stats_init.loc[feature, 'Median']
                perturbed_median = stats_pert.loc[feature, 'Median']
                original_average = stats_init.loc[feature, 'Average']
                perturbed_average = stats_pert.loc[feature, 'Average']
                markdown_lines.append(f"| {feature} | {original_max} | {perturbed_max} | {original_min} | {perturbed_min} | {original_median} | {perturbed_median} | {original_average} | {perturbed_average} |")
            
            headings.append(("###", "Distance Adjustment Evaluation Metrics"))
            markdown_lines.append(f"### Distance Adjustment Evaluation Metrics\n")
            # get the distance value, threshold and penalty value

            from utils.utils import get_successful_adversarial_samples
            df_init_successful, df_perturbed_successful = get_successful_adversarial_samples(df_init=df_init, df_pert=df_pert, y_init=eval.get_predicted_clean_labels(), y_pert=eval.get_predicted_perturbed_labels())

            threshold = calculate_threshold(df_init, categorical)
            distance = calculate_distance(df_init_successful, df_perturbed_successful, categorical)
            penalty = PENALTY
            text = "The threshold is a constant value calculated from the original dataset, and penalty is a constant value that is used to penalize invalid values identified in the categorical features.\n"
            markdown_lines.append(text)
            markdown_lines.append(f"Threshold: {threshold}\n")
            markdown_lines.append(f"Penalty: {penalty}\n")
            text = "The distance value is calculated from the original dataset and the perturbed dataset, and it is used to measure the distance between the two datasets. A higher distance value means that the perturbed dataset is more different from the original dataset and so the metrics require an adjustment.\n"
            markdown_lines.append(text)
            markdown_lines.append(f"Distance: {distance}\n")


            headings.append(("###", "Evaluation Results"))
            markdown_lines.append(f"### Evaluation Results\n")
            # create a table with the evaluation results
            markdown_lines.append("| Metric | Value |")
            markdown_lines.append("|--------|-------|")

            for _, row in eval.get_evaluation().iterrows():
                metric_name = row["Evaluation_Name"]
                if str(metric_name).lower() == "confusion matrix":
                    continue
                metric_value = row["Value"]
                markdown_lines.append(f"| {metric_name} | {metric_value} |")

            markdown_lines.append("\nConfusion Matrix\n")
            # create a table with the confusion matrix
            metric_name = eval.get_evaluation().loc[eval.get_evaluation()["Evaluation_Name"] == "Confusion Matrix"]
            metric_value = metric_name.iloc[0]["Value"]

            num_classes = metric_value.shape[0]
            labels = [str(i) for i in range(num_classes)]  # Use numeric class indices

            # Header
            header = "| Actual \\ Predicted | " + " | ".join(labels) + " |"
            separator = "|" + "---|" * (num_classes + 1)

            markdown_lines.append(header)
            markdown_lines.append(separator)

            # Rows
            for i in range(num_classes):
                row = "| " + labels[i] + " | " + " | ".join([str(metric_value[i][j]) for j in range(num_classes)]) + " |"
                markdown_lines.append(row)



        ##########
        headings.append(("##", "Robustness Evaluation"))
        markdown_lines.append("## Robustness Evaluation\n")

        text = "The robustness of the model is evaluated using three main metrics. **DA Attack Success Rate** to measure the robustness of models against targeted adversarial attacks, **DA Misclassification Rate** to measure the robustness of models against untargeted adversarial attacks, and **Attack Deteoration** to measure the quantification of the deteoration of the model performance. This value results in a value between 0 and 100, and the closer to 100, the more robust the model is. The results can be assigned to five different levels of robustness, being:\n"
        markdown_lines.append(text)

        markdown_lines.append("80-100: Very robust.\n")
        markdown_lines.append("60-80: Robust.\n")
        markdown_lines.append("40-60: Moderately robust.\n")
        markdown_lines.append("20-40: Weakly robust.\n")
        markdown_lines.append("0-20: Not robust.\n")

        robustnessCalculator = RobustnessCalculator()
        robustness = robustnessCalculator.calculate_robustness(evalList)
        ImageGenerator(IMAGE_FOLDER).generate_robustness(robustness, "robustness.png")
        listImages = ImportRepository().get_png_from_folder(IMAGE_FOLDER, "robustness.png")
        for image in listImages:
            markdown_lines.append(f"![{image}]({image})\n")
        
        robustAvg = sum(robustness["Value"]) / len(robustness["Value"])
        robustAvg = round(float(robustAvg), 0)
        markdown_lines.append(f"###### Robustness score: {robustAvg}")

        markdown_lines.append("---\n")

        robustness = robustnessCalculator.calculate_robustness_worst_case(evalList)
        ImageGenerator(IMAGE_FOLDER).generate_robustness(robustness, "robustness_worst_case.png")
        listImages = ImportRepository().get_png_from_folder(IMAGE_FOLDER, "robustness_worst_case")
        for image in listImages:
            markdown_lines.append(f"![{image}]({image})\n")

        robustAvg = sum(robustness["Value"]) / len(robustness["Value"])
        robustAvg = round(float(robustAvg), 0)
        markdown_lines.append(f"###### Robustness score worst case scenario: {robustAvg}")
        
        index_lines = []
        for level, title in headings[1:]:  # Skip first "Index" heading
            clean_title = title.strip()   # Just in case there are hidden chars
            anchor = self.slugify(clean_title)
            indent = "  " if level == "###" else ""
            index_lines.append(f"{indent}* [{title}](#{anchor})")

        # Replace the placeholder with the actual index
        index_str = "\n".join(index_lines) + "\n"

        markdown_lines = [
            line if line.strip() != "_index_placeholder_" else index_str
            for line in markdown_lines
        ]

        
        if ExportRepository().export_md(markdown_lines, REPORT_NAME):
            ExportRepository().create_zip_file_folder(file_path=REPORT_NAME, folder_path=IMAGE_FOLDER, zip_path=ZIP_NAME)



    def _get_stats(self, df)->pd.DataFrame:
        statistics = {
            'Max': df.max(),
            'Min': df.min(),
            'Median': df.median(),
            'Average': df.mean()
        }

        stats_df = pd.DataFrame(statistics)
        return stats_df

    def _generate_images(self, modelData : ModelData, evalList : List[EvaluationData]):
        df_init = modelData.get_dataset()
        columns = modelData.get_columns()
        df_init.columns = columns

        category_features = DataConfiguration().get_config(df_init)
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

        