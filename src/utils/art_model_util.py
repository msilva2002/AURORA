import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf
import lightgbm as lgb
from lightgbm import LGBMClassifier, LGBMRegressor
from xgboost import XGBClassifier, XGBRegressor
from catboost import CatBoostClassifier
from art.estimators.classification import *
from sklearn.base import BaseEstimator
from services.query_service import QueryService
import pandas as pd


def get_art_classifier(model, dataset: pd.DataFrame, labels:pd.Series|None, **kwargs):
                
        if model is None:
            number_classes = _get_number_labels(dataset, labels)
            return BlackBoxClassifier(
                predict_fn=QueryService(number_classes).predict,
                input_shape=(dataset.shape[1],),
                nb_classes=number_classes,
            )


        # TensorFlow models
        try:
            if isinstance(model, tf.keras.Model):
                number_classes = _get_num_classes_tf(model)

                return TensorFlowV2Classifier(
                    model=model,
                    nb_classes=model.output_shape[-1],
                    input_shape=model.input_shape[1:],
                    loss_object=tf.keras.losses.get(model.loss),
                    #train_step=kwargs.get('train_step'),
                    #**kwargs
                )
        except (ImportError, AttributeError):
            pass

        # CatBoost
        try:
            if isinstance(model, CatBoostClassifier):
                return CatBoostARTClassifier(model=model, nb_features=dataset.shape[1])
        except Exception as e:
            print(e)
            try:
                return BlackBoxClassifier(predict_fn=lambda x: model.predict_proba(x), 
                                          input_shape=(model.n_features_in_,), 
                                          nb_classes=model.classes_,)
            except:
                pass

        # LightGBM
        try:          
            # Handle scikit-learn API models
            if isinstance(model, (LGBMClassifier, LGBMRegressor)):
                if not hasattr(model, 'booster_'):
                    raise ValueError("LightGBM model must be fitted first!")
            
                return LightGBMClassifier(
                    model=model.booster_  # Access the underlying Booster 
                )
                
            # Handle native Booster directly
            if isinstance(model, lgb.Booster):
                return LightGBMClassifier(model=model)
                
        except Exception as e:
            try:
                print(model.n_features_in_)
                print(model.n_classes_)
                return BlackBoxClassifier(predict_fn=lambda x: model.predict_proba(x), 
                                          input_shape=(model.n_features_in_,), 
                                          nb_classes=model.n_classes_,)
            except:
                pass

        # XGBoost
        try:
            if isinstance(model, (XGBClassifier, XGBRegressor)):
                num_features = getattr(model, "n_features_in_", None)
                num_classes = getattr(model, "n_classes_", None) if isinstance(model, XGBClassifier) else None
                return XGBoostClassifier(
                    model=model,
                    nb_features=num_features,
                    nb_classes=num_classes
                )
        except Exception as e:
            try:
                return BlackBoxClassifier(predict_fn=model.predict, 
                                          input_shape=(model.n_features_in_,), 
                                          nb_classes=model.n_classes_)
            except:
                pass

        # Scikit-learn (catch-all for BaseEstimator)
        if isinstance(model, BaseEstimator):
            return SklearnClassifier(model=model, **kwargs)

        raise ValueError(f"Unsupported model type: {type(model)}")

@staticmethod
def _get_number_labels(dataset: pd.DataFrame, labels: pd.Series|None) -> int:
    if labels is not None:
        return len(labels.unique())
    else:
        predictions = QueryService().predict(dataset)
        return len(set(predictions))
    
import tensorflow as tf

@staticmethod
def _get_num_classes_tf(model: tf.keras.Model) -> int:
    output_layer = model.layers[-1]
    if not isinstance(output_layer, tf.keras.layers.Dense):
        raise ValueError("The output layer must be a Dense layer.")
    num_units = output_layer.units
    if num_units == 1 and isinstance(output_layer.activation, tf.keras.activations.sigmoid):
        return 2  # Binary classification has 2 classes
    return num_units