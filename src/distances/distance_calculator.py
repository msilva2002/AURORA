from scipy.spatial.distance import hamming
import math
import pandas as pd
import numpy as np
from typing import List
PENALTY = 10

def get_penalty(original, categorical_features : List[str],normalization_params:dict):
    threshold = calculate_threshold(original, categorical_features,normalization_params)
    penalty = threshold * 0.1 * len(categorical_features)
    return np.round(penalty,2) 

def calculate_hamming_distance_one_row(p1, p2):
    p1 = np.atleast_1d(p1)
    p2 = np.atleast_1d(p2)
    
    hamming_dist = hamming(p1, p2)
    
    # normalization
    hamming_dist = hamming_dist*len(p1)
    return hamming_dist

def calculate_hamming_distance(p1, p2, penalty):

    p1 = np.atleast_1d(p1)
    p2 = np.atleast_1d(p2)
    
    hamming_dist = hamming(p1, p2)

    # assuming p2 is always the perturbed
    invalid_count = sum((x not in {0, 1}) for x in p2)
    hamming_dist += invalid_count * penalty

    invalid_count = int(sum(x != 0 for x in p2) > 1)
    hamming_dist += invalid_count * penalty

    invalid_count = max(0, all(x == 0 for x in p2))
    hamming_dist += invalid_count * penalty

    # normalization
    hamming_dist = hamming_dist*len(p1)
    return hamming_dist

def calculate_euclidean_distance(p1, p2, normalization=None, min_d = None, max_d = None):
    if pd.isna(p1) or pd.isna(p2):
        return 0
    # Calculate raw distance
    if isinstance(p1, (int, float)) and isinstance(p2, (int, float)):
        distance = math.sqrt((p1 - p2) ** 2)

    elif isinstance(p1, pd.DataFrame) and isinstance(p2, pd.DataFrame):
        distance = ((p1 - p2) ** 2).map(math.sqrt)

    else:
        #try:
        distance = math.sqrt((p1 - p2) ** 2)
        #except Exception as e:
        #    print(f"Found {e}")
        #    print(f"P1: {p1}")
        #    print(f"P2: {p2}")
        #    exit(-1)
    if min_d is None and max_d is None:
        return distance
    
    if normalization == "minmax":
        if isinstance(distance, pd.DataFrame):
            return distance.apply(lambda col: (col - min_d) / (max_d - min_d) if max_d != min_d else 0.0)
        return abs((distance - min_d) / (max_d - min_d) if max_d != min_d else 0.0)

    raise ValueError(f"Unknown normalization: {normalization}")
    
def calculate_distance(original : pd.DataFrame, perturbed : pd.DataFrame, categorical_features : List[str], normalization_params : dict):
    perturbed.columns = original.columns
    distance = []
    penalty = get_penalty(original, categorical_features,normalization_params)
    for categorical in categorical_features:
        col_init = original[categorical].values
        col_pert = perturbed[categorical].values

        # List comprehension for speed
        dist = [calculate_hamming_distance(p1, p2, penalty) for p1, p2 in zip(col_init, col_pert)]
        distance.append(np.median(dist))
        #distance.append(sum(dist))
    numerical_features = list(set(original.columns) - {item for sublist in categorical_features for item in sublist})

    for numerical in numerical_features:
        col_init = original[numerical].values
        col_pert = perturbed[numerical].values
        dist = [calculate_euclidean_distance(p1, p2, "minmax", normalization_params[numerical]["min"], normalization_params[numerical]["max"]) for p1, p2 in zip(col_init, col_pert)]
        distance.append(np.nanmedian(dist))
        #distance.append(sum(dist))
        
    return np.round(sum(distance),2)

def calculate_threshold(original, categorical_features : List[str],normalization_params):
    threshold = 0
    for categorical in categorical_features:
        threshold += 2

    numerical_features = list(set(original.columns) - {item for sublist in categorical_features for item in sublist})

    for numerical in numerical_features:
        normalized_p1 = original[numerical].copy()
        min_val = normalization_params[numerical]["min"]
        max_val = normalization_params[numerical]["max"]
        normalized_p1 = (original[numerical] - min_val) / (max_val - min_val)
        #median_value = original[numerical].median()
        #  add the absolute value of the median to the threshold
        threshold += np.abs(normalized_p1).median()

    if threshold < 0:
        threshold = 0

    return np.round(threshold,2)

