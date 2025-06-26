from utils.utils import get_features

def get_patterns(df, config_patterns):
    patterns = []
    for p in config_patterns:  # Ensure patterns exist
            
            pattern_dict = {"type": p.get("type")}

            # Extract features and add only if not empty
            for key in ["features", "locked_features", "integer_features"]:
                value = _get_features(df, p.get(key))  # Call get_features only if key exists
                if value:
                    pattern_dict[key] = value

            # Add numerical values only if they exist
            for key in ["ratio", "max_ratio", "missing_value", "probability"]:
                value = p.get(key)
                if value is not None:
                    pattern_dict[key] = value

            patterns.append(pattern_dict)

    # Convert list to tuple if needed
    patterns = tuple(patterns)
    return patterns

def _get_features(df, selected_features):
    features = get_features(df, selected_features)  # Call the get_features function
    
    # return position of features in df
    features = [df.columns.get_loc(f) for f in features]

    return list(features)