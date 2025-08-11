import os
from pathlib import Path

import numpy as np
import pandas as pd
import pymia.evaluation.evaluator as eval_
import SimpleITK as sitk
from colorama import Fore
from loguru import logger
from pymia.evaluation.metric import metric
from pymia.evaluation.writer import CSVStatisticsWriter
from multiprocessing import Pool, Manager, Lock

from audit.metrics.segmentation_metrics import calculate_metrics
from audit.metrics.segmentation_metrics import one_hot_encoding
from audit.utils.commons.file_manager import list_dirs
from audit.utils.commons.strings import fancy_print
from audit.utils.commons.strings import fancy_tqdm
from audit.utils.sequences.sequences import get_spacing
from audit.utils.sequences.sequences import load_nii_by_subject_id

"""
CUSTOM METRICS
"""


@logger.catch
def check_multiprocessing(config_file):
    cpu_cores = config_file.get("cpu_cores")
    if cpu_cores is None or cpu_cores == "None":
        logger.info("cpu_cores not specified or invalid in metric_extraction.yml file, defaulting to os.cpu_count()")
        cpu_cores = os.cpu_count()
    if not isinstance(cpu_cores, int) or cpu_cores <= 0:
        logger.info(f"Invalid cpu_cores value: {cpu_cores} in metric_extraction.yml file, defaulting to os.cpu_count()")
        cpu_cores = os.cpu_count()
    logger.info(f"Using {cpu_cores} CPU cores for processing")
    return cpu_cores


def initializer(shared_df, lock):
    """Initialize shared variables for multiprocessing"""
    global shared_dataframe, dataframe_lock
    shared_dataframe = shared_df
    dataframe_lock = lock


def process_subject(data: pd.DataFrame, params: dict, cpu_cores: int) -> pd.DataFrame:
    """Process a single subject"""
    path_ground_truth_dataset = params["path_ground_truth_dataset"]
    path_predictions = params["path_predictions"]
    numeric_label = params["numeric_label"]
    subject_id = params["subject_id"]
    label_names = params["label_names"]
    metrics_to_extract = params["metrics_to_extract"]
    model_name = params["model_name"]

    # read ground truth segmentation and prediction
    gt = load_nii_by_subject_id(root_dir=path_ground_truth_dataset, subject_id=subject_id, as_array=True)
    pred = load_nii_by_subject_id(root_dir=path_predictions, subject_id=subject_id, seq="_pred", as_array=True)
    spacing = get_spacing(load_nii_by_subject_id(path_predictions, subject_id, seq="_pred"))

    # making the segmentations binary (one hot encoding for each region)
    gt = one_hot_encoding(gt, numeric_label)
    pred = one_hot_encoding(pred, numeric_label)

    # compute metrics
    metrics = calculate_metrics(
        ground_truth=gt,
        segmentation=pred,
        subject=subject_id,
        regions=label_names,
        metrics=metrics_to_extract,
        spacing=spacing
    )

    # from list of dict to dataframe
    subject_info_df = pd.DataFrame(metrics)

    # add model info
    subject_info_df["model"] = model_name

    if cpu_cores == 1:
        return subject_info_df

    with dataframe_lock:
        data[subject_id] = subject_info_df

    return data


def extract_audit_metrics(config_file) -> pd.DataFrame:
    label_names, numeric_label = (
        list(config_file["labels"].keys()),
        list(config_file["labels"].values()),
    )

    # load paths to test data
    path_ground_truth_dataset = config_file["data_path"]
    metrics_to_extract = [key for key, value in config_file["metrics"].items() if value]
    subjects_list = list_dirs(path_ground_truth_dataset)

    # load paths to predictions
    models = config_file["model_predictions_paths"]
    raw_metrics = pd.DataFrame()
    cpu_cores = check_multiprocessing(config_file)

    if cpu_cores == 1:
        for model_name, path_predictions in models.items():
            fancy_print(f"\nStarting metric extraction for model {model_name}", Fore.LIGHTMAGENTA_EX, "✨")
            logger.info(f"Starting metric extraction for model {model_name}")

            # loop over all the elements in the root_dir folder
            with fancy_tqdm(total=len(subjects_list), desc=f"{Fore.CYAN}Progress", leave=True) as pbar:
                for subject_id in subjects_list:
                    pbar.set_postfix_str(f"{Fore.CYAN}Current subject: {Fore.LIGHTBLUE_EX}{subject_id}{Fore.CYAN}")
                    pbar.update(1)

                    params = {
                        "path_ground_truth_dataset": path_ground_truth_dataset,
                        "path_predictions": path_predictions,
                        "numeric_label": numeric_label,
                        "subject_id": subject_id,
                        "label_names": label_names,
                        "metrics_to_extract": metrics_to_extract,
                        "model_name": model_name
                    }

                    data = pd.DataFrame()
                    subject_info_df = process_subject(data, params, cpu_cores)
                    raw_metrics = pd.concat([raw_metrics, subject_info_df], ignore_index=True)

            logger.info(f"Finishing metric extraction for model {model_name}")

        return raw_metrics.sort_values(by=["model", "ID", "region"], ascending=[True, True, True])

    if cpu_cores > 1:

        manager = Manager()
        shared_data = manager.dict()
        lock = Lock()

        with Pool(processes=cpu_cores, initializer=initializer, initargs=(shared_data, lock)) as pool:
            for model_name, path_predictions in models.items():
                fancy_print(f"\nStarting metric extraction for model {model_name}", Fore.LIGHTMAGENTA_EX, "✨")
                logger.info(f"Starting metric extraction for model {model_name}")

                tasks = []
                for subject_id in subjects_list:
                    params = {
                        "path_ground_truth_dataset": path_ground_truth_dataset,
                        "path_predictions": path_predictions,
                        "numeric_label": numeric_label,
                        "subject_id": subject_id,
                        "label_names": label_names,
                        "metrics_to_extract": metrics_to_extract,
                        "model_name": model_name
                    }

                    tasks.append(pool.apply_async(process_subject, args=(shared_data, params, cpu_cores)))

                with fancy_tqdm(total=len(subjects_list), desc=f"{Fore.CYAN}Progress", leave=True) as pbar:
                    for task in tasks:
                        task.wait()
                        pbar.update(1)

                for subject_id, subject_info_df in shared_data.items():
                    raw_metrics = pd.concat([raw_metrics, subject_info_df], ignore_index=True)

                logger.info(f"Finishing metric extraction for model {model_name}")

        return raw_metrics.sort_values(by=["model", "ID", "region"], ascending=[True, True, True])


"""
PYMIA METRICS
"""


def post_process_metrics(df_metrics):
    # Convert all metrics to a DataFrame
    output = pd.DataFrame(df_metrics)
    output = output.pivot_table(index=["ID", "region", "model"], columns="metric", values="value")
    output.reset_index(inplace=True)
    output.sort_values(by=["model", "ID", "region"], inplace=True)

    return output


def perform_evaluation(pymia_evaluator, path_gt, path_pred, subject):
    path_gt = os.path.join(str(path_gt), subject, f"{subject}_seg.nii.gz")
    path_pred = os.path.join(str(path_pred), subject, f"{subject}_pred.nii.gz")

    try:
        if not os.path.exists(path_gt):
            raise FileNotFoundError(f'Ground truth file "{path_gt}" does not exist')

        if not os.path.exists(path_pred):
            raise FileNotFoundError(f'Prediction file "{path_pred}" does not exist')

        ground_truth = sitk.ReadImage(path_gt)
        prediction = sitk.ReadImage(path_pred)
        pymia_evaluator.evaluate(prediction, ground_truth, subject)
    except Exception as e:
        print(f"{subject} -> {e}")

    return pymia_evaluator


def aggregate_results(pymia_evaluator, model_name):
    raw_metrics = []
    for result in pymia_evaluator.results:
        result_dict = {
            "ID": result.id_,
            "region": result.label,
            "metric": result.metric,
            "value": result.value,
            "model": model_name,
        }
        raw_metrics.append(result_dict)

    return raw_metrics


def compute_statistics(pymia_evaluator, config, model_name):
    functions = {
        'MEAN': np.mean,
        'MEDIAN': np.median,
        'STD': np.std,
        'MIN': np.min,
        'MAX': np.max,
        'Q1': lambda x: np.percentile(x, 25),
        'Q3': lambda x: np.percentile(x, 75),
        'CI_2.5': lambda x: np.percentile(x, 2.5),
        'CI_5': lambda x: np.percentile(x, 5),
        'CI_95': lambda x: np.percentile(x, 95),
        'CI_97.5': lambda x: np.percentile(x, 97.5),
    }
    CSVStatisticsWriter(f"{config['output_path']}/stats/{model_name}/{config['filename']}.csv", delimiter=',',
                        functions=functions).write(pymia_evaluator.results)


def instantiate_pymia_metrics(selected_metrics: list):
    # Dict of available pymia metrics
    metric_map = {
        'haus': (metric.HausdorffDistance, {'percentile': 100}),
        'dice': (metric.DiceCoefficient, {}),
        'sens': (metric.Sensitivity, {}),
        'spec': (metric.Specificity, {}),
        'accu': (metric.Accuracy, {}),
        'jacc': (metric.JaccardCoefficient, {}),
        'prec': (metric.Precision, {}),
        'auc': (metric.AreaUnderCurve, {}),
        'fnr': (metric.FalseNegativeRate, {}),
        # add here more
    }

    def create_metrics(selected_metrics):
        metrics = []
        for metric_name in selected_metrics:
            if metric_name in metric_map:
                metric_class, params = metric_map[metric_name]
                # add parameters if needed
                metrics.append(metric_class(metric=metric_name, **params))
            else:
                print(
                    f"The '{metric_name}' is not available. Go to src.metric.main.instantiate_pymia_metrics method to include it.")
        return metrics

    return create_metrics(selected_metrics)


def extract_pymia_metrics(config_file):
    labels, processed_labels = config_file["labels"], {}
    for key, value in labels.items():
        if isinstance(value, list):
            value = tuple(value)
        processed_labels[value] = key

    # load paths to the datasets
    path_ground_truth_dataset = config_file["data_path"]
    metrics_to_extract = [key for key, value in config_file["metrics"].items() if value]
    subjects_list = list_dirs(path_ground_truth_dataset)

    # metrics to extract
    metrics = instantiate_pymia_metrics(metrics_to_extract)

    # initializing output metrics
    evaluator = eval_.SegmentationEvaluator(metrics, processed_labels)

    # load paths to predictions
    models = config_file["model_predictions_paths"]
    for model_name, path_predictions in models.items():
        fancy_print(f"\nStarting metric extraction for model {model_name}", Fore.LIGHTMAGENTA_EX, "✨")
        logger.info(f"Starting metric extraction for model {model_name}")

        # loop over all the elements in the root_dir folder
        with fancy_tqdm(total=len(subjects_list), desc=f"{Fore.CYAN}Progress", leave=True) as pbar:
            for n, subject_id in enumerate(subjects_list):

                pbar.set_postfix_str(f"{Fore.CYAN}Current subject: {Fore.LIGHTBLUE_EX}{subject_id}{Fore.CYAN}")
                pbar.update(1)
                if n % 10 == 0 and n > 0:
                    fancy_print(f"Processed {n} subjects", Fore.CYAN, "🔹")

                logger.info(f"Processing subject: {subject_id}")
                evaluator = perform_evaluation(evaluator, path_ground_truth_dataset, path_predictions, subject_id)

            # accumulate the results for each of the models
            raw_metrics = aggregate_results(evaluator, model_name)

            if config_file.get("calculate_stats", None):
                Path(os.path.join(config_file['output_path'], 'stats', f'{model_name}')).mkdir(parents=True, exist_ok=True)
                compute_statistics(evaluator, config_file, model_name)
            evaluator.clear()

    extracted_metrics = post_process_metrics(raw_metrics)

    return extracted_metrics
