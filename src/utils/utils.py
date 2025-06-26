import pandas as pd

def get_features(df, selected_features):
    # check if the selected features have a "*" in them
    # if they do, then we need to get all the features that have that prefix
    # if not, then we just return the selected features

    if selected_features is None:
        return list()

    features = set()  # Using a set to avoid duplicate columns
    selected_features = selected_features.split(",")  # Split the string by ','
    for feature in selected_features:
        if "*" in feature:
            prefix = feature.rstrip("*")  # Remove '*' to get the prefix
            matches = [col for col in df.columns if col.startswith(prefix)]
            features.update(matches)
        else:
            if feature.strip() in df.columns:  # Ensure the column exists in df
                features.add(feature.strip())
    
    return list(features)

def get_successful_adversarial_samples(df_init, df_pert, y_init: pd.DataFrame, y_pert: pd.DataFrame):
    # Get the samples that changed their label from y_init to y_pert
    # and are in the same row in both dataframes
    # This is done by checking if the label in y_init is different from y_pert
    # and if the row in df_init is the same as the row in df_pert
    # We can use the index of the dataframe to check if the rows are the same
    
    mask = (y_init != y_pert).squeeze()

    # Get the indices where labels have changed
    changed_index = df_init.index[mask]

    # Select only the changed samples
    df_init_changed = df_init.loc[changed_index]
    df_pert_changed = df_pert.loc[changed_index]
    return df_init_changed, df_pert_changed

def apply_constraints(data, categorical_features, integer_features):
        patterns = categorical_features.split(",") if isinstance(categorical_features, str) else categorical_features
        for pattern in patterns:
            cols = get_features(data, pattern)
            numeric_group = data[cols].apply(lambda col: pd.to_numeric(col, errors='coerce'))
            numeric_group = numeric_group.fillna(0)
            
            max_col = numeric_group.abs().idxmax(axis=1)

            one_hot = pd.DataFrame(0, index=data.index, columns=cols)
            for idx in data.index:
                one_hot.at[idx, max_col[idx]] = 1

            data[cols] = one_hot

        integer_features = integer_features.split(",") if isinstance(integer_features, str) else integer_features
        for feature in integer_features:
            feature = feature.strip()
            if feature in data.columns:
                data[feature] = pd.to_numeric(data[feature], errors='coerce').round().astype('Int64')
        return data
