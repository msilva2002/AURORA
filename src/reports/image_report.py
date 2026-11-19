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
import textwrap
ORIG_COLOR = 'tab:blue'
PERT_COLOR = 'green'
from matplotlib.ticker import MaxNLocator

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

        #wrapped = ['\n'.join(textwrap.wrap(l, width=15)) for l in labels]
        labels = [f"{tick}\n({int(val)})" for tick, val in zip(xticks, values)]
        ax.set_xticklabels(labels, fontsize=10)

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
        fig, ax = plt.subplots(figsize=(12, 12), subplot_kw={'projection': 'polar'})  # was (8, 8)
        ax.set_theta_offset(pi / 2)
        ax.set_theta_direction(-1)
        
        plt.xticks(angles[:-1], xticks, fontsize=17)


        ax.plot(angles, results, linewidth=1, linestyle='solid')
        ax.tick_params(axis='x', pad=25)
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        ax.set_title(title, fontsize=20, pad=20)

        labels = [f"{tick}\n({int(val)})" for tick, val in zip(xticks, results)]
        wrapped = ['\n'.join(textwrap.wrap(l, width=15)) for l in labels]
        ax.set_xticklabels(wrapped, fontsize=17)

        #plt.show()
        return fig

    '''
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
        '''
    
    def create_category_min_max_avg_plot(self, df, category, xticks):
        number_of_plots = 3
        fig, axes = plt.subplots(1, number_of_plots, figsize=(10 * number_of_plots, 10), 
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
        ax[i].set_title("Max and Min Values", fontsize=20, pad=20)
        ax[i].fill(angles, max_vals, color='green', alpha=0.2)
        ax[i].fill(angles, min_vals, color='white', alpha=1.0)
        ax[i].tick_params(axis='x', pad=25)  # push labels outward

        # average
        i = 1
        self._set_axes_style_category(ax[i], angles, average, xticks)
        ax[i].set_title("Average Values", fontsize=20, pad=20)
        ax[i].tick_params(axis='x', pad=25)

        # value counts
        i = 2
        category_counts = np.count_nonzero(df[category].values, axis=0)
        values = list(category_counts)
        values += values[:1]
        self._set_axes_style_category(ax[i], angles, values, xticks)
        ax[i].set_title("Value Counts", fontsize=20, pad=20)
        ax[i].tick_params(axis='x', pad=25)

        # wrap long tick labels to avoid overlap
        #for axis in ax:
        #    labels = [label.get_text() for label in axis.get_xticklabels()]
        #    wrapped = ['\n'.join(textwrap.wrap(l, width=10)) for l in labels]
        #    axis.set_xticklabels(wrapped, fontsize=17, fontweight='bold')

        # wrap long tick labels to avoid overlap
        value_sets = [
            [f"{max(mx, mn):.1f} / {min(mx, mn):.1f}" for mx, mn in zip(max_vals[:-1], min_vals[:-1])],
            [f"{v:.1f}" for v in average[:-1]],
            [f"{v}" for v in values[:-1]],
        ]

        for axis, vals in zip(ax, value_sets):
            labels = [f"{tick}\n({val})" for tick, val in zip(xticks, vals)]
            wrapped = ['\n'.join(textwrap.wrap(l, width=15)) for l in labels]
            axis.set_xticklabels(wrapped, fontsize=17)

        fig.tight_layout(pad=4.0)
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
        #figure = self.create_numerical_plot(df_init, df_pert, "Mean standardized values changed for numerical features")
        figure_o, figure_p = self.create_numerical_radar_pair(df_init, df_pert, evalData.get_perturbedData().attackName)
        ExportRepository().export_plot(figure_o, self.folder_path + "numerical_features_original_"+ evalData.get_perturbedData().attackName + ".png")
        ExportRepository().export_plot(figure_p, self.folder_path + "numerical_features_perturbed_" + evalData.get_perturbedData().attackName + ".png")


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
        
        plt.xticks(angles[:-1], columns, fontsize=17)

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
        plt.title(title, fontsize=20)
        #plt.show()
        return fig



    def _style_polar(self, ax, angles):
        ax.set_theta_offset(pi / 2)
        ax.set_theta_direction(-1)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels([])                      # labels are placed by _place_labels
        ax.xaxis.grid(True, color='grey', alpha=0.4)
        ax.yaxis.grid(True, color='grey', alpha=0.4)


    def _compute_limits(self, values, zoom=False):
        """
        Work out the radial axis for a set of values. Returns (lo, hi, inner_ticks).

        zoom=False : always include the 0-1 ring (the original range), grow if values leave it.
        zoom=True  : fit the axis to the data, so small values (e.g. means of skewed
                    features, which sit close to 0 after min-max scaling) fill the plot.
        """
        vals = np.asarray(values, dtype=float)
        lo = min(0.0, np.nanmin(vals))
        hi = np.nanmax(vals) if zoom else max(1.0, np.nanmax(vals))
        if hi <= lo:
            hi = lo + 1.0
        if zoom:
            hi += 0.05 * (hi - lo)                  # a little headroom
        ticks = MaxNLocator(nbins=5).tick_values(lo, hi)
        return float(ticks[0]), float(ticks[-1]), ticks[ticks > ticks[0]]

    def _apply_limits(self, ax, lims):
        """Apply limits from _compute_limits to an axis; returns (lo, hi)."""
        lo, hi, inner = lims
        ax.set_ylim(lo, hi)
        ax.set_rgrids(inner, labels=[f"{t:.3g}" for t in inner], fontsize=9)
        return lo, hi

    def _place_labels(self, ax, angles, features, details, lims, pad=0.12, fontsize=16, width=15):
        """
        Put the feature labels outside the circle, anchored so the text always grows
        AWAY from the plot (left-aligned on the right side, right-aligned on the left side),
        instead of using the default tick labels that overlap the circle.
        `pad` is the gap between the outer ring and the label, as a fraction of the radius.
        """
        lo, hi = lims
        r = hi + pad * (hi - lo)
        for ang, f, d in zip(angles[:-1], features, details):
            name = '\n'.join(textwrap.wrap(f, width=width))
            s, c = np.sin(ang), np.cos(ang)         # screen direction (theta=0 at top, clockwise)
            ha = 'left' if s > 0.25 else 'right' if s < -0.25 else 'center'
            va = 'bottom' if c > 0.25 else 'top' if c < -0.25 else 'center'
            ax.text(ang, r, f"{name}\n({d})", ha=ha, va=va, fontsize=fontsize,
                    clip_on=False, linespacing=1.2)

    def _fmt(self, v):
        """Compact number formatting for tick labels."""
        a = abs(v)
        if a == 0:
            return "0"
        if a >= 1e4 or a < 1e-2:
            return f"{v:.1e}"
        if a >= 100:
            return f"{v:.0f}"
        return f"{v:.2f}"


    def _radar_single(self, name, df, st, color, features, angles, L1, L2, L3, third_panel):
        """One 3-panel radar figure for a single dataset, using shared limits L1/L2/L3."""
        def close(v):
            return list(v) + list(v)[:1]

        fig, axes = plt.subplots(1, 3, figsize=(32, 11), subplot_kw={'projection': 'polar'})

        # ---- panel 1: min / max band -------------------------------------------
        ax = axes[0]
        self._style_polar(ax, angles)
        mn, mx = close(st['min']), close(st['max'])
        ax.fill_between(angles, mn, mx, color=color, alpha=0.2, zorder=2)
        ax.plot(angles, mx, color=color, lw=1.3)
        ax.plot(angles, mn, color=color, lw=1.3)
        ax.set_title("Min and Max Values", fontsize=22, pad=95)
        lims = self._apply_limits(ax, L1)
        self._place_labels(ax, angles, features,
                    [f"{self._fmt(a)} / {self._fmt(b)}" for a, b in zip(df.max(), df.min())], lims)

        # ---- panel 2: mean -------------------------------------------------------
        ax = axes[1]
        self._style_polar(ax, angles)
        vals = close(st['mean'])
        ax.plot(angles, vals, color=color, lw=1.3, zorder=4)
        ax.fill(angles, vals, color=color, alpha=0.2, zorder=3)
        ax.set_title("Average Values", fontsize=22, pad=95)
        lims = self._apply_limits(ax, L2)
        self._place_labels(ax, angles, features, [self._fmt(v) for v in df.mean()], lims)

        # ---- panel 3: spread (std) or non-zero share ----------------------------
        ax = axes[2]
        self._style_polar(ax, angles)
        if third_panel == 'nonzero':
            vals, title, details = close(st['nonzero']), "% Non-zero Values", \
                [f"{v:.0f}%" for v in st['nonzero']]
        else:
            vals, title, details = close(st['std']), "Standard Deviation", \
                [self._fmt(v) for v in df.std()]
        ax.plot(angles, vals, color=color, lw=1.3, zorder=4)
        ax.fill(angles, vals, color=color, alpha=0.2, zorder=3)
        ax.set_title(title, fontsize=22, pad=95)
        lims = self._apply_limits(ax, L3)
        self._place_labels(ax, angles, features, details, lims)

        fig.suptitle(f"{name} data", fontsize=28, y=0.98)
        fig.text(0.5, 0.03, "Radial axes are scaled to the original min-max range and are identical in the "
                            "original and perturbed images. Labels show the real values.",
                ha='center', fontsize=14, color='grey')
        fig.subplots_adjust(left=0.06, right=0.94, top=0.80, bottom=0.10, wspace=0.75)
        return fig

    def create_numerical_radar_pair(self, df_init: pd.DataFrame, df_pert: pd.DataFrame, title, third_panel='std'):
        """
        Returns (fig_original, fig_perturbed): the same three radar panels for each dataset.

        third_panel='std'      standard deviation (spread)
        third_panel='nonzero'  % of non-zero values (like the "value counts" of the categorical plots)

        Both figures use the SAME radial limits (computed from both datasets together),
        so they can be compared directly side by side.
        """
        features = list(df_init.columns)
        df_init = df_init.astype(float)
        df_pert = df_pert[features].astype(float)

        n = len(features)
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
        angles += angles[:1]

        lo = df_init.min()
        span = (df_init.max() - lo).replace(0, 1.0)

        def stats(df):
            return {
                'min': ((df.min() - lo) / span).tolist(),
                'max': ((df.max() - lo) / span).tolist(),
                'mean': ((df.mean() - lo) / span).tolist(),
                'std': (df.std() / span).tolist(),
                'nonzero': ((df != 0).mean() * 100).tolist(),
            }

        so, sp = stats(df_init), stats(df_pert)

        L1 = self._compute_limits(so['min'] + so['max'] + sp['min'] + sp['max'])
        L2 = self._compute_limits(so['mean'] + sp['mean'], zoom=True)
        if third_panel == 'nonzero':
            L3 = (0.0, 100.0, np.array([20, 40, 60, 80, 100]))
        else:
            L3 = self._compute_limits(so['std'] + sp['std'], zoom=True)

        fig_o = self._radar_single("Original", df_init, so, ORIG_COLOR, features, angles, L1, L2, L3, third_panel)
        fig_p = self._radar_single(title, df_pert, sp, PERT_COLOR, features, angles, L1, L2, L3, third_panel)

        return fig_o, fig_p
