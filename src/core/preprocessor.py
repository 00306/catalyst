import numpy as np
from scipy.ndimage import gaussian_filter

def normalize_min_max(data_array):
    min_val, max_val = np.min(data_array), np.max(data_array)
    if max_val - min_val == 0:
        return np.copy(data_array)
    return (data_array - min_val) / (max_val - min_val)

def apply_gaussian_smoothing(data_array, sigma=1.0):
    return gaussian_filter(data_array, sigma=sigma)