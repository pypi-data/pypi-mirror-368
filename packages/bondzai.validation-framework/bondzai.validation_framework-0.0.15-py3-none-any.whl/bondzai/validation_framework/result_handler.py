import numpy as np
import json
from pathlib import Path
from bondzai.gateway_sdk.enums import AgentAIType
from bondzai.gateway_sdk.agent import Agent

EXPECTED = "expected"
PREDICTED = "predicted"


class NumpyEncoder(json.JSONEncoder):
    """
    JSON encoder for Maestro CLI JSON
    """

    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def get_MRAE_score(expected_data: np.ndarray, predicted_data: np.ndarray) -> float:
    """
    Get Mean Relative Absolute Error score for regression
    Args:
        expected_data: list of expected output
        predicted_data: list of predicted output
    Returns:
        mrae: MRAE score
    """
    relative_matrix = np.abs(expected_data - predicted_data) / (
                1e-10 + 0.5 * (np.abs(expected_data) + np.abs(predicted_data)))
    mrae = float(np.mean(relative_matrix))
    mrae = min(1.0, mrae)
    return mrae


def get_cosine_distance(expected_data: np.ndarray, predicted_data: np.ndarray) -> float:
    """
    Compute cosine distance for regression
    Args:
        expected_data: list of expected output
        predicted_data: list of predicted output
    Returns:
        cos_dict: cosinus distance score
    """
    expected_data = expected_data.flatten()
    predicted_data = predicted_data.flatten()
    x1 = np.dot(expected_data, expected_data)
    x2 = np.dot(predicted_data, predicted_data)
    ps = np.dot(expected_data, predicted_data)
    cos_dict = 1 - ps / np.sqrt(x1 * x2 + 10e-8)
    return cos_dict


def get_confusion_matrix(expected_data: list, predicted_data: list, percent: bool = False) -> np.ndarray:
    """
    From expected and predicted data, get confusion matrix
    Args:
        expected_data: list of expected output
        predicted_data: list of predicted output
        percent: It True, display the confusion matrix in percent
    Returns:
        confusion_matrix: each column represent a predicted class, each row an expected class
    """
    label_list = np.unique(np.concatenate((expected_data, predicted_data))).tolist()
    for unknown in ["unknown", 0]:
        if unknown in label_list:
            label_list.pop(label_list.index(unknown))
            label_list.append(unknown)
    n_dim_out = len(label_list)
    confusion_matrix = np.zeros((n_dim_out + 1, n_dim_out + 1))
    for index, data in enumerate(expected_data):
        confusion_matrix[label_list.index(data) + 1, label_list.index(predicted_data[index]) + 1] += 1
    sum_array = np.sum(confusion_matrix, axis=1) + 1e-8
    sum_array = np.reshape(sum_array, (-1, 1))
    if percent:
        confusion_matrix = np.divide(confusion_matrix, sum_array)
        apply_all = np.vectorize(lambda i: f"{np.round(i * 100, 1)}%")
    else:
        apply_all = np.vectorize(lambda i: str(i))
    confusion_matrix = apply_all(confusion_matrix)
    confusion_matrix = confusion_matrix.astype("U25")
    confusion_matrix[0, 1:] = label_list
    confusion_matrix[1:, 0] = label_list
    confusion_matrix[0, 0] = "\\"
    return confusion_matrix


def get_accuracy_score(expected_data: list, predicted_data: list) -> float:
    """
    Calculate the accuracy
    Args:
        expected_data: list of expected output
        predicted_data: list of predicted output
    Returns:
        accuracy_score: accuracy score
    """
    accuracy_score = np.sum(np.array(expected_data) == np.array(predicted_data)) / len(expected_data)
    return accuracy_score


def get_F1_score(expected_data: list, predicted_data: list) -> float:
    """
    Calculate the weighted F1 score
    Args:
        expected_data: list of expected output
        predicted_data: list of predicted output

    Returns:
        f1_score: weighted F1 score
    """
    expected_data = np.asarray(expected_data)
    predicted_data = np.asarray(predicted_data)
    total_weight = 0
    f1_score = 0
    for classNb in np.unique(expected_data):
        weight = np.sum(expected_data == classNb)
        tp = np.sum((predicted_data == classNb) * (expected_data == classNb))
        fp = np.sum((expected_data != classNb) * (predicted_data == classNb))
        fn = np.sum((expected_data == classNb) * (predicted_data != classNb))
        precision = 0 if tp + fp == 0 else tp / (tp + fp)
        recall = 0 if tp + fn == 0 else tp / (tp + fn)
        f1_score += weight * 2 * (precision * recall) / (precision + recall + 1e-18)
        total_weight += weight
    f1_score /= total_weight
    return f1_score


class ResultGatherer:
    """
    Class to add results one by one and compare them to get results
    """
    def __init__(self, agent: Agent):
        self.result_dict = {}
        self.ai_type = agent.get_asl_meta()["apps"][0]["meta"]["ai_type"]

    def _add_result(self, id: str, label_type: str, value, key: str):
        """
        Add one expected result
        Args:
            id: id of the recording that result is saved
            label_type: label type as string
            value: label value (int or string / list for regression)
            key: key of the dict to saved current value
        """
        if label_type not in self.result_dict.keys():
            self.result_dict[label_type] = {}
        if id not in self.result_dict[label_type].keys():
            self.result_dict[label_type][id] = {}
        self.result_dict[label_type][id][key] = value

    def add_expected(self, id: str, label_type: str, value):
        """
        Add one expected result
        Args:
            id: id of the recording that result is saved
            label_type: label type as string
            value: label value (int or string / list for regression)
        """
        self._add_result(id, label_type, value, EXPECTED)
    
    def add_predicted(self, id: str, label_type: str, value):
        """
        Add one predicted result
        Args:
            id: id of the recording that result is saved
            label_type: label type as string
            value: label value (int or string / list for regression)
        """
        self._add_result(id, label_type, value, PREDICTED)

    def get_results(self, export_path: Path = None) -> dict:
        """
        Get results for added data
        Args:
            export_path: If given, save results in JSON file
        Returns:
            result_dict: results as dict
        """
        result_dict = None
        if self.ai_type == AgentAIType.APP_AI_TYPE_CLASSIFICATION.name:
            result_dict = self.get_classification_results()
        elif self.ai_type == AgentAIType.APP_AI_TYPE_REGRESSION.name:
            result_dict = self.get_regression_results()

        for key, result_list in self.result_dict.items():
            result_dict[key]["raw_results"] = result_list

        if None not in [result_dict, export_path]:
            export_path.parent.mkdir(parents=True, exist_ok=True)
            with open(export_path, "w") as file:
                json.dump(result_dict, file, indent=4, cls=NumpyEncoder)
        return result_dict

    def get_classification_results(self) -> dict:
        """
        Get results for added data for classification
        Returns:
            result_dict: results as dict
        """
        res = {}
        result_dict = self.get_results_as_list()
        for key, element in result_dict.items():
            expected_list = element[EXPECTED]
            predicted_list = element[PREDICTED]
            if 0 in [len(expected_list), len(predicted_list)]:
                confusion_matrix = None
                accuracy = None
                f1_score = None
            else:
                confusion_matrix = get_confusion_matrix(expected_list, predicted_list)
                accuracy = get_accuracy_score(expected_list, predicted_list)
                f1_score = get_F1_score(expected_list, predicted_list)
            res[key] = {
                "confusion_matrix": confusion_matrix,
                "accuracy": accuracy,
                "f1_score": f1_score
            }
        return res

    def get_regression_results(self) -> dict:
        """
        Get results for added data for regression
        Returns:
            result_dict: results as dict
        """
        res = {}
        result_dict = self.get_results_as_list()
        for key, element in result_dict.items():
            expected_list = element[EXPECTED]
            predicted_list = element[PREDICTED]
            if 0 in [len(expected_list), len(predicted_list)]:
                mrae = None
                cosine_distance = None
            else:
                mrae = get_MRAE_score(expected_list, predicted_list)
                cosine_distance = get_cosine_distance(expected_list, predicted_list)
            res[key] = {
                "MRAE": mrae,
                "cosine_distance": cosine_distance
            }
        return res

    def get_results_as_list(self) -> dict:
        """
        Convert result dict into lists of expected and predicted, only keeping data that are both filled
        Returns:
            result_dict: transformed result dict
        """
        result_dict = {}
        for key, _result_dict in self.result_dict.items():
            expected_list = []
            predicted_list = []
            for element in _result_dict.values():
                if EXPECTED in element.keys() and PREDICTED in element.keys():
                    expected_list.append(element[EXPECTED])
                    predicted_list.append(element[PREDICTED])
            result_dict[key] = {EXPECTED: expected_list, PREDICTED: predicted_list}
        return result_dict

    def clear(self):
        """
        Clear result buffer
        """
        self.result_dict = {}
