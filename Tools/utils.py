import numpy as np
import pandas as pd

def euclidean_distance(a, b, axis=1):
    return np.sqrt(np.sum((a - b) ** 2, axis=axis))

def load_file_json(path_database):
    df = pd.read_json(path_database)
    df = df.drop(columns=["Index"])

    array = df.to_numpy()
    return array, array.shape, list(df.columns)


def compute_centroid(cluster, data):
    cluster_points = data[cluster]
    centroid = np.mean(cluster_points, axis=0)
    return centroid

def labels_and_get_centroids(data, labels, n_clusters):
    centroids = []
    for cluster_idx in range(n_clusters):
        cluster = np.where(labels == cluster_idx)[0]
        centroid = compute_centroid(cluster, data)
        centroids.append(centroid)
    return np.array(centroids), labels