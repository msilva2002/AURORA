# AURORA — Adversarial Understanding of Robustness and Offensive Resilience Analysis

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

<p align="center">
  <img src="/images/aurora.png" width="184" title="AURORA logo">
</p>
<br />

AURORA is an open-source framework for evaluating the robustness of machine learning models on tabular data classification. It integrates multiple adversarial perturbation methods and evaluation metrics within a unified framework to systematically assess model behavior under adversarial conditions. Additionally, AURORA incorporates a distance adjustment mechanism that penalizes implausible adversarial samples based on feature-level constraints, ensuring that the robustness assessment remains grounded in realistic perturbations.

## Installation

After downloading the repository, install the required packages inside /src using:

```
pip install -r requirements.txt
```

## Setup

Three configuration files are required before running AURORA:

**1. Attack configuration file**
A JSON file containing the configuration for the adversarial perturbation methods and the dataset labels. The default configuration file can be found in [configuration/configuration_attacks.json](configuration/configuration_attacks.json), and an example can be found [here](https://github.com/msilva2002/AURORA-Realistic-Robustness-Evaluation/tree/main/configuration/config_attacks.json). The default fields work out of the box; however, the patterns for A2PM must be configured manually, as they are dataset-specific. For the constrained versions of the perturbation methods, `integer_features` and `categorical_features` should be updated to reflect the dataset. Feature names resulting from one-hot encoding can be selected using the `*` wildcard (e.g., `State_*` captures `State_CTO`, `State_RST`, etc.). To deactivate a perturbation method, simply remove it from the configuration file.

**2. Dataset configuration file**
A JSON file specifying the categorical features in the dataset. The template can be found in [configuration/configuration_dataset.json](configuration/configuration_dataset.json), and an example can be found [here](https://github.com/msilva2002/AURORA-Realistic-Robustness-Evaluation/tree/main/configuration/config_data.json). The `*` wildcard can similarly be used to select all features sharing a common prefix.

**3. Target file** *(required for targeted attacks only)*
A CSV file specifying the target class for each sample, in order. An example can be found [here](https://github.com/msilva2002/AURORA-Realistic-Robustness-Evaluation/tree/main/configuration/target.csv).

**Model**
A model saved with `joblib` and ending with `.joblib` is required. If the model is not directly accessible, it can be queried remotely by adapting [src/repositories/query_repository.py](src/repositories/query_repository.py) to handle communication. Note that using a remote model disables white-box attack functionality, regardless of whether the model exposes gradients.

## Usage

Run AURORA with the following command inside /src :

```
python run.py -d clean_samples.csv -t target.csv -m model.joblib -c config_attacks.json -s config_data.json
```

The `-w` flag can optionally be used to specify the number of processors to use. If not set, AURORA will automatically use half of the available CPU cores. To restrict execution to a single core, set the -w flag to 1. Note that doing so will result in slower adversarial example generation.

## Results

**Adversarial examples** will be saved under the `/datasets` folder, with one file per successfully executed perturbation method, named accordingly.

**Evaluation report** will be saved under the `/evaluation_report` folder, containing a Markdown file with the full report and a folder with all associated images. A ZIP archive bundling all artifacts will also be created.