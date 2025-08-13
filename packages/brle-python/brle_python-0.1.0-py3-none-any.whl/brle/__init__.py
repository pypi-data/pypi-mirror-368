"""Binary run length encoding"""

import numpy as np
import array


def encode(arr: np.ndarray):
    if not isinstance(arr, np.ndarray):
        raise TypeError("Input must be a numpy array")
    if not arr.ndim == 2:
        raise ValueError("Input must be a 2D array")
    if not arr.dtype == np.uint8:
        raise ValueError("Input array must be of type uint8")
    if not np.all(np.isin(arr, [0, 1])):
        raise ValueError("Input array must only contain 0s and 1s")
    height, width = arr.shape
    encoded = array.array("I", [height, width])
    current_count = 0
    current_value = 1
    for val in arr.flatten():
        if val == current_value:
            current_count += 1
        else:
            encoded.append(current_count)
            current_value = val
            current_count = 1
    encoded.append(current_count)
    return encoded


def decode(encoded: array.array):
    if not isinstance(encoded, array.array):
        raise TypeError("Encoded data must be an array")
    if len(encoded) < 2:
        raise ValueError("Encoded data must contain at least height and width")
    height = encoded.pop(0)
    width = encoded.pop(0)
    arr = np.zeros((height * width), dtype=np.uint8)
    current_value = 1
    current_index = 0
    while encoded:
        count = encoded.pop(0)
        arr[current_index : current_index + count] = current_value
        current_index += count
        current_value = 1 - current_value
    return arr.reshape((height, width))
