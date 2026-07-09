from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Manager
import time, os
import argparse
from domain_data.model_data import ModelData
from controllers import shell_controller

def parse_args():
    parser = argparse.ArgumentParser(
        description="AURORA shell parallel application."
    )

    parser.add_argument(
        "-d", "--dataset",
        required=True,
        help="Path to the dataset."
    )

    parser.add_argument(
        "-t", "--target",
        required=False,
        help="Target labels. If empty only non-targeted attacks will execute."
    )

    parser.add_argument(
        "-m", "--model",
        required=False,
        help="Path to the model. If false, the API class will be used."
    )

    parser.add_argument(
        "-w", "--workers",
        required=False,
        type=int,
        help="Maximum number of workers. Default is half of available processors."
    )

    parser.add_argument(
        "-c", "--config",
        required=True,
        help="Attack configuration."
    )

    parser.add_argument(
        "-s", "--settings",
        required=True,
        help="Dataset setting, what feature is categorical/numerical."
    )

    return parser.parse_args()


def load_data(args):
    import joblib
    try:
        model = joblib.load(args.model)
    except:
        print("Model not found. Running using API.")
    
    import dask.dataframe as pd
    try:
        dataset = pd.read_csv(args.dataset)
    except:
        raise Exception("An error was found while importing the dataset.")
    
    try:
        target = pd.read_csv(args.target)
    except:
        print("Target not found. Running only non-targeted.")
        target = None

    import json
    try:
        with open(args.config, "r") as f:
            config = json.load(f)
        feature_label = next((item['feature_label'] for item in config if 'feature_label' in item), None)
    except:
        print("Label not found in configuration. Assuming no label is present in dataset.")
        feature_label = None

    try:
        with open(args.settings, "r") as f:
            data_config = json.load(f)
    except:
        print("Data configuration file not found.")
        data_config = None

    
    modelData = ModelData(dataset=dataset, model=model, target=target, label=feature_label, data_config=data_config)
    return modelData

def worker(task_id, attack, progress, modelData):
    try:
        attack_name = str(attack["attackName"])
        print(f"Worker {task_id} received attack type: {attack_name}")
        result = shell_controller.start_attack_sequence(modelData, attack)
        progress[task_id] = "completed"
        return result
    except Exception as e:
        progress[task_id] = f"failed: {str(e)}"
        return None

if __name__ == "__main__":
    args = parse_args()
    modelData = load_data(args=args)
    if args.workers == None or args.workers<1:
        num_cpus = os.cpu_count()
        args.workers = num_cpus/2
    elif args.workers > os.cpu_count():
        args.workers = os.cpu_count()

    import json
    with open(args.config, "r") as f:
            config = json.load(f)
    attacks = [item for item in config if 'attackName' in item]

    shell_controller.clear_folders()
    results = []
    with Manager() as manager:
        progress = manager.dict()

        with ProcessPoolExecutor(max_workers=int(args.workers)) as pool:
            futures = {
                pool.submit(worker, i, attacks[i], progress, modelData): i
                for i in range(len(attacks))
            }

            while futures:
                for f in list(futures):
                    if f.done():
                        print(f"Task {futures[f]} finished.")
                        results.append(f.result())
                        del futures[f]

                time.sleep(1)
    shell_controller.start_evaluation_sequence(modelData=modelData, perturbedDataList=results)