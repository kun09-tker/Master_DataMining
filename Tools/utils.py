import numpy as np
import pandas as pd

def euclidean_distance(a, b, axis=1):
    return np.sqrt(np.sum((a - b) ** 2, axis=axis))

def distance_matrix(matrix):
    n = len(matrix)
    distance_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i+1, n):
            distance = euclidean_distance(matrix[i], matrix[j])
            distance_matrix[i, j] = distance
            distance_matrix[j, i] = distance
    return distance_matrix

def load_file_json(path_database):
    df = pd.read_json(path_database)
    df = df.drop(columns=["Index"])

    array = df.to_numpy()
    return array, array.shape, list(df.columns)