from scipy.spatial.distance import hamming
import math
import pandas as pd
import numpy as np
from typing import List
PENALTY = 2

def calculate_hamming_distance_one_row(p1, p2):
    p1 = np.atleast_1d(p1)
    p2 = np.atleast_1d(p2)
    
    hamming_dist = hamming(p1, p2)
    
    # normalization
    hamming_dist = hamming_dist*len(p1)
    return hamming_dist

def calculate_hamming_distance(p1, p2):

    p1 = np.atleast_1d(p1)
    p2 = np.atleast_1d(p2)
    
    hamming_dist = hamming(p1, p2)

    # assuming p2 is always the perturbed
    invalid_count = sum((x not in {0, 1}) for x in p2)
    hamming_dist += invalid_count * PENALTY

    invalid_count = int(sum(x != 0 for x in p2) > 1)
    hamming_dist += invalid_count * PENALTY

    invalid_count = max(0, all(x == 0 for x in p2))
    hamming_dist += invalid_count * PENALTY

    # normalization
    hamming_dist = hamming_dist*len(p1)
    return hamming_dist

def calculate_euclidian_distance(p1, p2):
    if isinstance(p1, (int, float)) and isinstance(p2, (int, float)):
        # Scalar version
        return math.sqrt((p1 - p2) ** 2)
    
    elif isinstance(p1, pd.DataFrame) and isinstance(p2, pd.DataFrame):
        # DataFrame version — element-wise
        return ((p1 - p2) ** 2).map(math.sqrt)

    else:
        return math.sqrt((p1 - p2) ** 2)
    
def calculate_distance(original, perturbed, categorical_features : List[str]):
    perturbed.columns = original.columns
    distance = []
    for categorical in categorical_features:
        col_init = original[categorical].values
        col_pert = perturbed[categorical].values

        # List comprehension for speed
        dist = [calculate_hamming_distance(p1, p2) for p1, p2 in zip(col_init, col_pert)]
        distance.append(np.median(sorted(dist)))

    numerical_features = list(set(original.columns) - {item for sublist in categorical_features for item in sublist})

    for numerical in numerical_features:

        col_init = original[numerical].values
        col_pert = perturbed[numerical].values
        dist = [calculate_euclidian_distance(p1, p2) for p1, p2 in zip(col_init, col_pert)]

        distance.append(np.median(sorted(dist)))

    return sum(distance)

def calculate_threshold(original, categorical_features : List[str]):
    threshold = 0
    for categorical in categorical_features:
        threshold += 2

    numerical_features = list(set(original.columns) - {item for sublist in categorical_features for item in sublist})

    for numerical in numerical_features:
       median_value = original[numerical].median()
       # add the absolute value of the median to the threshold
       threshold += abs(median_value)

    if threshold < 0:
        threshold = 0

    return threshold

