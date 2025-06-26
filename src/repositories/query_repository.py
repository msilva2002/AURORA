import zope.interface
from repositories.query_interface import QueryModelI
import pandas as pd
import requests

@zope.interface.implementer(QueryModelI) 
class QueryModel:

    def predict(self, df: pd.DataFrame):  
        predictions = []        
        for _, row in df.iterrows():
            try:
                features = row.values.tolist()
                response = requests.post(
                    "http://127.0.0.1:8080/predict",
                    json={'features': features},
                    timeout=10
                )

                if response.status_code == 200:
                    pred = response.json()['prediction'][0]
                    predictions.append(pred)
                else:
                    predictions.append(None)
                    print(f"Error for row {_}: {response.json().get('error')}")

            except Exception as e:
                predictions.append(None)
                print(f"Failed to process row {_}: {str(e)}")

        return predictions

