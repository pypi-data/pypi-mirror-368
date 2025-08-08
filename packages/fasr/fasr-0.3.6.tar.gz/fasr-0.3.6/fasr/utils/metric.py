import re
from typing import List, Dict, Union

import numpy as np
import editdistance

from fasr.normalizer import Normalizer


def compute_char_error_rate(
    x: str,
    y: str,
    ignore_space: bool = True,
    ignore_punc: bool = True,
    normalize: bool = False,
) -> float:
    """Compute the character error rate between two strings.

    Args:
        x (str): the source string
        y (str): the target string
        ignore_space (bool, optional): whether to ignore spaces. Defaults to True.
        ignore_punc (bool, optional): whether to ignore punctuation. Defaults to True.
        normalizer (Normalizer, optional): the normalizer used to normalize the strings, must have a normalize method. Defaults to None.

    Returns:
        float: the character error rate
    """
    assert isinstance(x, str) and isinstance(y, str)
    normalizer = (
        Normalizer(remove_erhua=True, enable_0_to_9=True, lang="zh", operator="itn")
        if normalize
        else None
    )
    if normalizer is not None:
        x = normalizer.normalize(x)
        y = normalizer.normalize(y)
    x = x.replace(" ", "") if ignore_space else x
    x = re.sub(r"[^\w\s]", "", x) if ignore_punc else x
    y = y.replace(" ", "") if ignore_space else y
    y = re.sub(r"[^\w\s]", "", y) if ignore_punc else y
    if len(y) == 0:
        if len(x) == 0:
            return 1.0
        else:
            return 0.0
    return round(editdistance.eval(x, y) / len(y), 4)


def match_token(hyp: str, ref: str) -> List:
    """Match the tokens between two strings.

    Args:
        hyp (str): the hypothesis string
        ref (str): the reference string

    Returns:
        List: the list of matched results, eg. [(0, 0), (1, 1), (2, 2), (3, 3)], where the first element is the index of the reference string and the second element is the index of the hypothesis string.
    """
    hyp = list(map(lambda x: x.lower(), hyp))
    ref = list(map(lambda x: x.lower(), ref))

    len_hyp = len(hyp)
    len_ref = len(ref)

    cost_matrix = np.zeros((len_hyp + 1, len_ref + 1), dtype=np.int16)
    ops_matrix = np.zeros((len_hyp + 1, len_ref + 1), dtype=np.int8)

    for i in range(len_hyp + 1):
        cost_matrix[i][0] = i
    for j in range(len_ref + 1):
        cost_matrix[0][j] = j

    for i in range(1, len_hyp + 1):
        for j in range(1, len_ref + 1):
            if hyp[i - 1] == ref[j - 1]:
                cost_matrix[i][j] = cost_matrix[i - 1][j - 1]
            else:
                substitution = cost_matrix[i - 1][j - 1] + 1
                insertion = cost_matrix[i - 1][j] + 1
                deletion = cost_matrix[i][j - 1] + 1

                compare_val = [substitution, insertion, deletion]

                min_val = min(compare_val)
                operation_idx = compare_val.index(min_val) + 1
                cost_matrix[i][j] = min_val
                ops_matrix[i][j] = operation_idx

    match_idx = []
    i = len_hyp
    j = len_ref
    rst = {"nwords": len_ref, "cor": 0, "wrong": 0, "ins": 0, "del": 0, "sub": 0}
    while i >= 0 or j >= 0:
        i_idx = max(0, i)
        j_idx = max(0, j)

        if ops_matrix[i_idx][j_idx] == 0:  # correct
            if i - 1 >= 0 and j - 1 >= 0:
                match_idx.append((j - 1, i - 1))
                rst["cor"] += 1

            i -= 1
            j -= 1

        elif ops_matrix[i_idx][j_idx] == 2:  # insert
            i -= 1
            rst["ins"] += 1

        elif ops_matrix[i_idx][j_idx] == 3:  # delete
            j -= 1
            rst["del"] += 1

        elif ops_matrix[i_idx][j_idx] == 1:  # substitute
            i -= 1
            j -= 1
            rst["sub"] += 1

        if i < 0 and j >= 0:
            rst["del"] += 1
        elif j < 0 and i >= 0:
            rst["ins"] += 1

    match_idx.reverse()
    wrong_cnt = cost_matrix[len_hyp][len_ref]
    rst["wrong"] = wrong_cnt
    return match_idx


def streaming_delay(
    t_send: List[Dict[str, float]],
    t_response: List[Dict[str, float]],
    return_results: bool = False,
) -> List[Dict[str, Union[str, float]]] | float:
    """calculate the delay between the fire and response tokens

    Args:
        t_send (Dict[str, float]): send tokens with timestamp. eg. [{'token': 'a', 'timestamp': 0.1}, {'token': 'b', 'timestamp': 0.2}]
        t_response (Dict[str, float]): response tokens with timestamp. eg. [{'token': 'a', 'timestamp': 0.3}, {'token': 'b', 'timestamp': 0.4}]
        return_results (bool, optional): whether to return the results. Defaults to False.

    Returns:
        List[float]: the delay between the fire and response tokens. eg. [{'token': 'a', 'send': 0.1, 'response': 0.3, 'delay': 0.2}, {'token': 'b', 'send': 0.2, 'response': 0.4, 'delay': 0.2}]
    """
    ref = "".join([t["token"] for t in t_send])
    hyp = "".join([t["token"] for t in t_response])

    matched = match_token(hyp, ref)
    delay = []
    for m in matched:
        t = {}
        t["token"] = t_send[m[0]]["token"]
        t["send"] = t_send[m[0]]["timestamp"]
        t["response"] = t_response[m[1]]["timestamp"]
        t["delay"] = t["response"] - t["send"]
        delay.append(t)
    if return_results:
        return delay
    else:
        return round(sum([t["delay"] for t in delay]) / len(delay), 4)
