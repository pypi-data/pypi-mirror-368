import numpy as np
from scipy.stats import pearsonr as _pearsonr
from sklearn.metrics import mean_squared_error, r2_score


def root_mean_square_error(label: list, predict: list) -> float:
    label = np.array(label)
    predict = np.array(predict)
    return np.sqrt(np.mean(np.square(predict - label)))


def pearsonr_numpy(label: list, predict: list) -> float:
    label = np.array(label)
    predict = np.array(predict)
    return np.corrcoef(label, predict)[0, 1]


def pearsonr_scipy(label: list, predict: list) -> float:
    return _pearsonr(label, predict)[0]


def envelope_of_expected_error(label: list, predict: list, relative_error=0.15, absolute_error=0.05) -> tuple:
    """
    预期误差: Expected Error
    预期误差包络线: Envelope of Expected Error

    Args:
        label (list): 真值列表
        predict (list): 非真值列表

    Returns:
        tuple: above_percent, below_percent, within_percent. EE包络线上百分比, EE包络线下百分比, EE包络线内百分比
    """
    above_count = 0
    below_count = 0
    within_count = 0
    label = np.array(label)
    predict = np.array(predict)
    # 判断输入是否合法
    if len(label) != len(predict) or len(label) == 0:
        return np.nan, np.nan, np.nan
    # 计算EE上下包络线
    label_above_envelope = label + (relative_error * label + absolute_error)
    label_below_envelope = label - (relative_error * label + absolute_error)
    # 获取EE包络线上下数组
    flag_above_array = predict > label_above_envelope
    flag_below_array = predict < label_below_envelope
    flag_within_array = np.logical_and(predict <= label_above_envelope, predict >= label_below_envelope)
    # 获取EE包络线上下的数量
    above_count = np.sum(flag_above_array)
    below_count = np.sum(flag_below_array)
    within_count = np.sum(flag_within_array)
    total_count = above_count + below_count + within_count
    # 计算EE包络线上下的百分比
    above_percent = above_count / total_count * 100
    below_percent = below_count / total_count * 100
    within_percent = within_count / total_count * 100
    return above_percent, below_percent, within_percent


def median_bias(label: list, predict: list) -> float:
    """
    中值偏差median bias

    Args:
        label (list): 真值列表
        predict (list): 非真值列表

    Returns:
        float: 结果
    """
    label = np.array(label)
    predict = np.array(predict)
    return np.median(predict) - np.median(label)


def mean_bias(label: list, predict: list) -> float:
    """
    平均偏差mean bias

    Args:
        label (list): 真值列表
        predict (list): 非真值列表

    Returns:
        float: 结果
    """
    label = np.array(label)
    predict = np.array(predict)
    return np.mean(predict) - np.mean(label)


def mean_absolute_error(label: list, predict: list) -> float:
    """
    平均绝对误差mean absolute error

    Args:
        label (list): 真值列表
        predict (list): 非真值列表

    Returns:
        float: 结果
    """
    label = np.array(label)
    predict = np.array(predict)
    return np.mean(np.abs(predict - label))


if __name__ == "__main__":
    print(root_mean_square_error([-2, -1, 0, 1, 2], [4, 1, 3, 2, 0]))
    print(pearsonr_numpy([-2, -1, 0, 1, 2], [4, 1, 3, 2, 0]))
    print(envelope_of_expected_error([-2, -1, 0, 1, 2], [4, 1, 3, 2, 0]))
    print(median_bias([-2, -1, 0, 1, 2], [4, 1, 3, 2, 0]))
    print(pearsonr_scipy([1], [2]))
