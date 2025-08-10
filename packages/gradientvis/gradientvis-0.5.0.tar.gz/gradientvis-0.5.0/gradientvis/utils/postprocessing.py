import numpy as np

def normalize_map(activation_map):
    activation_map = (activation_map - activation_map.min()) / (activation_map.max() - activation_map.min())
    return activation_map
