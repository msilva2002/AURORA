from domain_data.evaluation_data import EvaluationData
from domain_data.model_data import ModelData
from typing import List
from repositories.export_repository import ExportRepository
from distances.distance_calculator import calculate_hamming_distance_one_row
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend for matplotlib
import matplotlib.pyplot as plt
import numpy as np
from math import pi
from sklearn.preprocessing import StandardScaler
import pandas as pd

class ImageGenerator:
    def __init__(self, folder_path: str):
        self.folder_path = folder_path

    def generate_robustness(self, results : pd.DataFrame, title:str):
        fig, ax = plt.subplots(1, 1, figsize=(8 * 2, 8), 
                             subplot_kw={'projection': 'polar'}, sharex=False, sharey=False)
        
        xticks = results['Evaluation_Name'].tolist()
        values = results['Value'].tolist()
        values += values[:1]
        angles = np.linspace(0, 2 * np.pi, len(xticks), endpoint=False).tolist()
        angles += angles[:1]

        ax.set_theta_offset(pi / 2)
        ax.set_theta_direction(-1)

        ax.set_xticks(angles[:-1], xticks, fontsize=10)

        # plot a fine line for 0, 20, 40, 60, 80, 100
        for i in range(0, 101, 20):
            ax.plot(angles, [i] * len(angles), color='black', linewidth=0.5, linestyle='dashed', alpha=0.5)

        # plot the values
        ax.plot(angles, values, linewidth=1, linestyle='solid', color='green', zorder=4, label='Robustness')
        # add fill to the area in the middle
        ax.fill(angles, values, color='green', alpha=0.2, zorder=3)  # Fill under perturbed
        ExportRepository().export_plot(fig, self.folder_path + title)

    def generate_categorical(self, evalData:EvaluationData, modelData : ModelData, feature_combination:List[str], figure_number:int):
        # feature_combination = ["feature1", "feature2"], all from the same category

        # for original data
        df_init = modelData.get_dataset()
        columns = modelData.get_columns()
        df_init.columns = columns

        df_pert = evalData.get_perturbed_dataframe()
        df_pert.columns = columns

        df_init = df_init[feature_combination]
        df_pert = df_pert[feature_combination]

        # 1 for each feature in the feature_combination

        distances = []
        for value in feature_combination:
            dist = sum(map(calculate_hamming_distance_one_row, df_init[value], df_pert[value]))
            distances.append(dist)

        figure = self._create_category_plot(distances, feature_combination, "Values changed for categorical feature")
        ExportRepository().export_plot(figure, self.folder_path + "independent_categorical_feature_"+ evalData.get_perturbedData().attackName + "_" + str(figure_number) + ".png")

        #3 images, max and min, mean, and value counts
        figure = self.create_category_min_max_avg_plot(df_init, feature_combination, feature_combination)
        ExportRepository().export_plot(figure, self.folder_path + "original_category_" + str(figure_number) + ".png")

        figure = self.create_category_min_max_avg_plot(df_pert, feature_combination, feature_combination)
        ExportRepository().export_plot(figure, self.folder_path + "perturbed_category_" + evalData.get_perturbedData().attackName + "_" + str(figure_number) + ".png")


    def _create_category_plot(self, results, xticks, title):
        num_vars = len(results)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1]  # Complete the loop

        results += results[:1]  # Complete the loop
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})
        ax.set_theta_offset(pi / 2)
        ax.set_theta_direction(-1)
        
        plt.xticks(angles[:-1], xticks, fontsize=10)

        ax.plot(angles, results, linewidth=1, linestyle='solid')
            
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        ax.set_title(title, fontsize=12)
        #plt.show()
        return fig

    
    def create_category_min_max_avg_plot(self, df, category, xticks):
        number_of_plots = 3
        fig, axes = plt.subplots(1, number_of_plots, figsize=(8 * 2, 8), 
                             subplot_kw={'projection': 'polar'}, sharex=False, sharey=False)
        
        ax = np.ravel(axes)

        max_vals = df[category].max()
        max_vals = max_vals.tolist()
        max_vals += max_vals[:1]

        min_vals = df[category].min()
        min_vals = min_vals.tolist()
        min_vals += min_vals[:1]

        average = df[category].mean()
        average = average.tolist()
        average += average[:1]

        angles = np.linspace(0, 2 * np.pi, len(category), endpoint=False).tolist()
        angles += angles[:1]

        # max and min
        i = 0
        self._set_axes_style_max_min(ax[i], "Max", xticks, max_vals, angles)
        self._set_axes_style_max_min(ax[i], "Min", xticks, min_vals, angles)
        ax[i].set_title("Max and Min Values", fontsize=12)
        ax[i].fill(angles, max_vals, color='green', alpha=0.2)  # Transparent fill for max
        ax[i].fill(angles, min_vals, color='white', alpha=1.0)  # Ensures min area stays clear

        # average
        i = 1
        self._set_axes_style_category(ax[i], angles, average, xticks)
        ax[i].set_title("Average Values", fontsize=12)
        # value counts
        i = 2
        category_counts = np.count_nonzero(df[category].values, axis=0)
        values = list(category_counts)
        values += values[:1]
        self._set_axes_style_category(ax[i], angles, values, xticks)
        ax[i].set_title("Value Counts", fontsize=12)

        return fig



    def _set_axes_style_max_min(self, ax, label, xticks, values, angles):
        ax.set_theta_offset(pi / 2)
        ax.set_theta_direction(-1)

        # if any value is different from 0 or 1, then we plot it in red
        if any(x not in {0, 1} for x in values):
            ax.plot(angles, values, color='red', linewidth=1, linestyle='solid', label=label)
        else:
            ax.plot(angles, values, color='black', linewidth=1, linestyle='solid', label=label)

        #ax[i].plot(angles, average, color='black', linewidth=0.8, linestyle='solid', label='Average')
        ax.set_xticks(angles[:-1], xticks, fontsize=10)
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

    def _set_axes_style_category(self, ax, angles, results, xticks):
        ax.set_theta_offset(pi / 2)
        ax.set_theta_direction(-1)
        
        ax.set_xticks(angles[:-1], xticks, fontsize=10)

        ax.plot(angles, results, linewidth=1, linestyle='solid')
            
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        #plt.show()

    def generate_numerical(self, evalData:EvaluationData, modelData : ModelData, feature_combination:List[List[str]]):
        df_init = modelData.get_dataset()
        columns = modelData.get_columns()
        df_init.columns = columns

        remaining_columns = list(set(df_init.columns) - {item for sublist in feature_combination for item in sublist})

        df_init = modelData.get_dataset()
        columns = modelData.get_columns()
        df_init.columns = columns

        df_pert = evalData.get_perturbed_dataframe()
        df_pert.columns = columns

        df_init = df_init[remaining_columns]
        df_pert = df_pert[remaining_columns]

        # standard scaler to compare the mean
        figure = self.create_numerical_plot(df_init, df_pert, "Mean standardized values changed for numerical features")
        ExportRepository().export_plot(figure, self.folder_path + "numerical_features_" + evalData.get_perturbedData().attackName + ".png")


    def create_numerical_plot(self,df_init, df_perturbed, title):

        num_vars = len(df_init.columns)
        columns = df_init.columns
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1]  # Complete the loop

        # Standardize the data
        scaler = StandardScaler()
        df_init_scaled = scaler.fit_transform(df_init)
        df_perturbed_scaled = scaler.transform(df_perturbed)

        df_init_scaled = pd.Series(np.mean(df_init_scaled, axis=0), index=columns)  # Convert to Series with column names
        df_perturbed_scaled = pd.Series(np.mean(df_perturbed_scaled, axis=0), index=columns)
        
        df_init_scaled = df_init_scaled.values.flatten().tolist()
        df_perturbed_scaled = df_perturbed_scaled.values.flatten().tolist()

        # Ensure radar chart loops back to first value
        df_init_scaled += df_init_scaled[:1]
        df_perturbed_scaled += df_perturbed_scaled[:1]
        
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})
        ax.set_theta_offset(pi / 2)
        ax.set_theta_direction(-1)
        
        plt.xticks(angles[:-1], columns, fontsize=10)

        max_val = max(max(df_init_scaled), max(df_perturbed_scaled))
        min_val = min(min(df_init_scaled), min(df_perturbed_scaled))
        # check the abs values of the max and min values
        if abs(max_val) > abs(min_val):
            min_val = -max_val
        else:
            max_val = -min_val
        
        # set the limits of the plot
        ax.set_ylim(min_val, max_val)
        
        ax.plot(angles, df_init_scaled, color='blue', linewidth=1, linestyle='dashed', alpha=0.5, label='Original')
        ax.plot(angles, df_perturbed_scaled, linewidth=1, linestyle='solid', color='green', zorder=4, label='Perturbed')
        # add fill to the area in the middle
        #ax.fill(angles, df_init_scaled, alpha=0.2, color='blue', zorder=3)
        # Fill the area between the two lines
        ax.fill(angles, df_perturbed_scaled, color='green', alpha=0.2, zorder=3)  # Fill under perturbed
            
        plt.legend(loc='upper right')
        plt.title(title, fontsize=12)
        #plt.show()
        return fig

