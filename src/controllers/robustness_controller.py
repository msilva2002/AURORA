from flask import Blueprint, request, jsonify, send_file
from domain_data.model_data import ModelData
from domain_data.perturbed_data import PerturbedData
from services.execute_attack_service import ExecuteAttackService
from services.execute_evaluation_service import ExecuteEvaluationService
import threading
from managers.status_manager import StatusManager

import warnings
warnings.filterwarnings("ignore")

from attacks.hopskipjump_attack import HopSkipJumpAttack
from attacks.hopskipjump_constrained_attack import HopSkipJumpConstrainedAttack
from attacks.hopskipjump_targeted_attack import HopSkipJumpAttackTargeted
from attacks.hopskipjump_constrained_targeted_attack import HopSkipJumpAttackConstrainedTargeted
from attacks.zoo_attack import ZerothOrderOptimizationAttack
from attacks.zoo_constrained_attack import ZerothOrderOptimizationConstrainedAttack
from attacks.zoo_targeted_attack import ZerothOrderOptimizationAttackTargeted
from attacks.zoo_constrained_targeted_attack import ZerothOrderOptimizationConstrainedAttackTargeted
from attacks.cw_attack import CarliniWagnerAttack
from attacks.cw_constrained_attack import CarliniWagnerConstrainedAttack
from attacks.cw_targeted_attack import CarliniWagnerAttackTargeted
from attacks.cw_constrained_targeted_attack import CarliniWagnerConstrainedAttackTargeted
from attacks.a2pm_attack import A2PMAttack
from attacks.a2pm_targeted_attack import A2PMAttackTargeted
#from attacks.pgd_attack import ProjectedGradientDescentAttack
#from attacks.pgd_targeted_attack import ProjectedGradientDescentAttackTargeted
from attacks.boundary_attack import BoundaryAttackClass as BoundaryAttack
from attacks.boundary_constrained_attack import BoundaryConstrainedAttack
from attacks.boundary_targeted_attack import BoundaryAttackTargeted
from attacks.boundary_constrained_targeted_attack import BoundaryConstrainedAttackTargeted

from evaluations.evaluation_clean_accuracy import CleanAccuracy
from evaluations.evaluation_adversarial_accuracy import AdversarialAccuracy
from evaluations.evaluation_attack_success_rate import AttackSuccessRate
from evaluations.evaluation_misclassification_rate import MisclassificationRate
from evaluations.evaluation_confusion_matrix import ConfusionMatrix
from evaluations.evaluation_time import EvaluationTime
from evaluations.evaluation_attack_deterioration import AttackDeterioration

from reports.report import ReportCreator

attackClasses = [A2PMAttack, 
                 BoundaryAttack, BoundaryConstrainedAttack, 
                 CarliniWagnerAttack, CarliniWagnerConstrainedAttack,
                 HopSkipJumpAttack, HopSkipJumpConstrainedAttack,
                 ZerothOrderOptimizationAttack, ZerothOrderOptimizationConstrainedAttack]

attackClassesTargeted = [A2PMAttackTargeted, 
                         BoundaryAttackTargeted, BoundaryConstrainedAttackTargeted, 
                         CarliniWagnerAttackTargeted, CarliniWagnerConstrainedAttackTargeted,
                         HopSkipJumpAttackTargeted, HopSkipJumpAttackConstrainedTargeted,
                         ZerothOrderOptimizationAttackTargeted, ZerothOrderOptimizationConstrainedAttackTargeted]
#attackClassesTargeted = []
#attackClasses = [BoundaryConstrainedAttack, BoundaryAttack]

evaluationClasses = [CleanAccuracy, AdversarialAccuracy, AttackSuccessRate, 
                     MisclassificationRate, AttackDeterioration, ConfusionMatrix, EvaluationTime]

robustnesstest_bp = Blueprint('robustnesstest', __name__, url_prefix='/api/robustnesstest')

StatusManager(attackClasses + attackClassesTargeted)

thread = None

@robustnesstest_bp.route('/start', methods=['POST'])
def start_attack_sequence():
    global thread
    if thread is not None and thread.is_alive():
        return jsonify({"error": "Already executing"}), 400

    status_manager = StatusManager()
    status_manager.reset_status()

    if 'dataset' not in request.files:
        return jsonify({"error": "Dataset file is required"}), 400

    model_file = request.files.get('model')  # .joblib file (optional)
    dataset_file = request.files['dataset']  # .csv file (required)
    target_file = request.files.get('target')  # .csv file (optional)
    import pandas as pd
    import joblib

    # Load the model if provided
    model = None
    if model_file:
        # check if the file is a joblib file
        if model_file.filename.endswith('.joblib'):
            model = joblib.load(model_file)

    # Load dataset
    dataset = pd.read_csv(dataset_file)

    # Load target file if provided
    target = None
    if target_file:
        try:
            target = pd.read_csv(target_file)
        except:
            target = None
    
    modelData = ModelData(dataset=dataset, model=model, target=target)
    if thread is not None and thread.is_alive():
        return jsonify({"error": "Already executing"}), 400
    thread = threading.Thread(target=thread_function, args=(modelData,))
    thread.start()

    json_response = {
        "message": "Started"
    }

    return jsonify(json_response), 200

def thread_function(modelData : ModelData):

    try:
        attack_service = ExecuteAttackService(attackClasses=attackClasses, attackClassesTargeted=attackClassesTargeted)
        evaluation_service = ExecuteEvaluationService(evaluationClasses=evaluationClasses)
        evalList = []
        for attack in attack_service.classes:
            pertubedData = attack_service.execute(modelData=modelData, attackClass=attack)
            evaluation = evaluation_service.execute(modelData=modelData, perturbedData=pertubedData)
            if evaluation is not None:
                evalList.append(evaluation)

        ReportCreator().generate_report(modelData=modelData, evalList=evalList, perturbationMethods=attackClasses + attackClassesTargeted, metrics=evaluationClasses)
    finally:
        global thread
        thread = None   


#evaluate dataset
@robustnesstest_bp.route('/custom', methods=['POST'])
def evaluate_custom():
    import pandas as pd
    import joblib
    # it will be created as a "custom" attack
    global thread
    if thread is not None and thread.is_alive():
        return jsonify({"error": "Already executing"}), 400

    status_manager = StatusManager()
    status_manager.reset_status()

    
    if 'dataset' not in request.files:
        return jsonify({"error": "Dataset file is required"}), 400
    
    if 'perturbed_dataset' not in request.files:
        return jsonify({"error": "Perturbed dataset file is required"}), 400
    

    model_file = request.files.get('model')  # .joblib file (optional)
    dataset_file = request.files['dataset']  # .csv file (required)
    dataset_perturbed_file = request.files['perturbed_dataset']  # .csv file (required)
    target_file = request.files.get('target')  # .csv file (optional)

    # Load the model if provided
    model = None
    if model_file:
        # check if the file is a joblib file
        if model_file.filename.endswith('.joblib'):
            model = joblib.load(model_file)

    # Load dataset
    dataset = pd.read_csv(dataset_file)

    dataset_perturbed = pd.read_csv(dataset_perturbed_file)

    # Load target file if provided
    target = None
    if target_file:
        try:
            target = pd.read_csv(target_file)
        except:
            target = None

    
    modelData = ModelData(dataset=dataset, model=model, target=target)
    if thread is not None and thread.is_alive():
        return jsonify({"error": "Already executing"}), 400
    
    # run_time : float, targeted=False, message="",
    if target is not None:
        perturbedData = PerturbedData(attackName="Custom", perturbations=dataset_perturbed, run_time=0.0, targeted=True)
    else:
        perturbedData = PerturbedData(attackName="Custom", perturbations=dataset_perturbed, run_time=0.0, targeted=False)

    thread = threading.Thread(target=thread_function_custom, args=(modelData,perturbedData,))
    thread.start()

    json_response = {
        "message": "Started"
    }

    return jsonify(json_response), 200



def thread_function_custom(modelData : ModelData, pertubedData : PerturbedData):

    try:
        status_manager = StatusManager()
        status_manager.update_load("Custom")
        evaluation_service = ExecuteEvaluationService(evaluationClasses=evaluationClasses)
        evaluation_service.execute(modelData=modelData, perturbedData=pertubedData)
    finally:
        global thread
        thread = None 
    
@robustnesstest_bp.route('/datadescription', methods=['PUT', 'GET', 'POST'])
def data_description():
    from config.data_configuration import DataConfiguration
    configuration = DataConfiguration()
    if request.method == 'PUT':
        data = request.json
        result = configuration.update_config(data)
        if not result:
            return jsonify({"message": "Invalid configuration"}), 400
        return jsonify({"message": "Configuration successful"}), 200
    elif request.method == 'GET':
        return jsonify({"config": configuration.get_config_file()}), 200
    elif request.method == 'POST':
        configuration.reset_config()
        return jsonify({"message": "Configuration reset"}), 200
    else:
        return jsonify({"message": "Invalid method"}), 405

@robustnesstest_bp.route('/configuration', methods=['PUT', 'GET', 'POST'])
def configuration():
    from config.configuration import Configuration
    configuration = Configuration()
    if request.method == 'PUT':
        data = request.json
        result = configuration.update_config(data)
        if not result:
            return jsonify({"message": "Invalid configuration"}), 400
        return jsonify({"message": "Configuration successful"}), 200
    elif request.method == 'GET':
        return jsonify({"config": configuration.get_config_file()}), 200
    elif request.method == 'POST':
        configuration.reset_config()
        return jsonify({"message": "Configuration reset"}), 200
    else:
        return jsonify({"message": "Invalid method"}), 405
    
@robustnesstest_bp.route('/download', methods=['GET'])
def download():
    # retrive attack name from json
    attack_name = request.args.get('attackName')
    try:
        dataset = StatusManager().get_perturbation(attack_name)
        if dataset is None:
            return jsonify({"error": "Dataset not available/ not finished"}), 404
        else:
            # return csv file
            return send_file(dataset, as_attachment=True, download_name=f'{attack_name}.csv')
    except Exception as e:
        print(e)
        return jsonify({"error": "Invalid data"}), 400
    
@robustnesstest_bp.route('/reportstatus', methods=['GET'])
def report_status():
    statusManager = StatusManager().get_report_status()
    if statusManager:
        return jsonify(statusManager), 200
    else:
        return jsonify({"error": "Report not available"}), 404
    
@robustnesstest_bp.route('/report', methods=['GET'])
def report():
    statusManager = StatusManager().get_report_status()
    if statusManager:
        report = StatusManager().get_report()
        print(report)
        if report is not None:
            return send_file(report, as_attachment=True, download_name='report.zip')
        else:
            return jsonify({"error": "Report not ready"}), 404
    else:
        return jsonify({"error": "Report not available"}), 404

    


        
#test connection
@robustnesstest_bp.route('/test', methods=['GET'])
def test_connection():
    return jsonify({"message": "Connection successful"}), 200

@robustnesstest_bp.route('/status', methods=['GET'])
def get_status():
    status = StatusManager().get_status()
    return jsonify(status), 200

