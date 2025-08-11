import numpy as np

def to_numpy_array(input_data):
    if isinstance(input_data, np.ndarray):
        if input_data.ndim == 0:
            return np.array([input_data.item()])
        return input_data
    elif isinstance(input_data, int):
        return np.array([input_data])
    elif isinstance(input_data, list):
        if len(input_data) == 0:
            return None
        return np.array(input_data)
    else:
        return input_data # be None or others

def to_integer(input_value):
    if isinstance(input_value, np.ndarray):
        return int(input_value.item())
    elif isinstance(input_value, list):
        return int(input_value[0])
    elif isinstance(input_value, int):
        return input_value
    elif isinstance(input_value, str):
        return int(input_value)
    else:
        input_value

def to_float(input_value):
    if isinstance(input_value, np.ndarray):
        return float(input_value.item())
    elif isinstance(input_value, list):
        return float(input_value[0])
    elif isinstance(input_value, (int, float)):
        return float(input_value)
    else:
        return input_value