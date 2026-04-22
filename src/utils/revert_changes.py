import pandas as pd
import numpy as np
from typing import List

def revert_deleted_rows(df_init: pd.DataFrame, df_perturbed: pd.DataFrame) -> pd.DataFrame:
    df_result = df_perturbed.copy()
    nan_rows = df_perturbed[df_perturbed.isna().all(axis=1)]
    
    if len(nan_rows) > 0:
        indices_needed = nan_rows.index.tolist()
        mask = df_init.index.to_series().isin(indices_needed)
        df_init_subset = df_init[mask]
        
        for index in nan_rows.index:
            if index in df_init_subset.index:
                # Convert the row to match dtypes column by column
                row = df_init_subset.loc[index]
                for col in df_result.columns:
                    row[col] = row[col].astype(df_result[col].dtype)
                df_result.loc[index] = row
        
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
    clean_arr = np.array(clean_labels)
    if clean_arr.ndim == 2 and np.issubdtype(clean_arr.dtype, np.floating):
        clean_labels = np.argmax(clean_arr, axis=1)
        perturbed_labels = np.argmax(np.array(perturbed_labels), axis=1)

    mask = np.array(clean_labels) == np.array(perturbed_labels)

    # Create result by copying perturbed, then reverting rows with matching labels
    #if mask.any():
    #    indices_to_revert = df_perturbed.index[mask]
    #    df_init_subset = df_init.loc[df_init.index.isin(indices_to_revert)]
    #    df_result.loc[mask] = df_init_subset.loc[indices_to_revert]
    indices_to_revert = df_perturbed.index[mask]
    if len(indices_to_revert) > 0:
        df_result.loc[mask] = df_init.loc[indices_to_revert].astype(df_result.dtypes).values
        #df_result.loc[mask] = df_init.loc[indices_to_revert].values#.astype(df_result.dtypes).values
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
# expected output:
# 9 8 7
# 2 5 8
# 9 8 9
print(rv_df)


perturbed_labels = ["1", "2", "3"]
rv_df = revert_changes_df(df_init, df_perturbed, clean_labels, perturbed_labels)
# expected output:
#1 4 7
#2 5 8
#3 6 9
print(rv_df)
'''