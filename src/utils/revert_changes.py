import pandas as pd
import numpy as np
from typing import List

def revert_deleted_rows(df_init: pd.DataFrame, df_perturbed: pd.DataFrame) -> pd.DataFrame:
    df_result = df_perturbed.copy()
    nan_rows = df_perturbed[df_perturbed.isna().all(axis=1)]
    # replace NaN rows in df_perturbed with corresponding rows from df_init
    for index in nan_rows.index:
        if index in df_init.index:
            df_result.loc[index] = df_init.loc[index]
    
    return df_result


def revert_changes_df(df_init: pd.DataFrame, df_perturbed : pd.DataFrame, clean_labels:np.ndarray, perturbed_labels:np.ndarray)-> pd.DataFrame:
    """
    In case of the perturbation is not successful, revert the changes made to the initial dataframe,
    replacing the row by the original one.
    """

    df_result = revert_deleted_rows(df_init, df_perturbed)

    n_rows = len(df_init)
    if not (len(clean_labels) == len(perturbed_labels) == n_rows == len(df_perturbed)):
        raise ValueError("DataFrames and label lists must all have the same length")
        
    if list(df_init.columns) != list(df_perturbed.columns):
        raise ValueError("df_init and df_perturbed must have the same columns")
    
    # Build boolean mask where labels have *not* changed
    mask = np.array(clean_labels) == np.array(perturbed_labels)

    
    # Create result by copying perturbed, then reverting rows with matching labels
    df_result.loc[mask] = df_init.loc[mask]
    return df_result

'''
df_init = pd.DataFrame({
    'A': [1, 2, 3],
    'B': [4, 5, 6],
    'C': [7, 8, 9]
})

df_perturbed = pd.DataFrame({
    'A': [9, 9, 9],
    'B': [8, 8, 8],
    'C': [7, 8, 9]
})

clean_labels = ["1", "2", "3"]
perturbed_labels = ["3", "2", "1"]
rv_df = revert_changes_df(df_init, df_perturbed, clean_labels, perturbed_labels)

print(rv_df)


perturbed_labels = ["1", "2", "3"]
rv_df = revert_changes_df(df_init, df_perturbed, clean_labels, perturbed_labels)
print(rv_df)
'''