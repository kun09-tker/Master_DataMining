import numpy as np
from Tools import euclidean_distance

def silhouette_score(samples, labels):
    n_samples = len(samples)
    total_score = 0.0

    for i in range(n_samples):
        same_cluster = samples[labels == labels[i]]
        distances = [euclidean_distance(samples[i], point, axis=0) for point in same_cluster
                     if not np.array_equal(samples[i], point)]
        a_i = np.mean(distances)

        other_clusters = np.unique(labels[labels != labels[i]])
        b_i_values = []

        for cluster in other_clusters:
            points_in_other_cluster = samples[labels == cluster]
            distances = [euclidean_distance(samples[i], point, axis=0) for point in points_in_other_cluster]
            b_i = np.mean(distances)
            b_i_values.append(b_i)
        
        b_i = min(b_i_values)
        silhouette_i = (b_i - a_i) / max(a_i, b_i)
        total_score += silhouette_i
    
    score = total_score / n_samples
    print(f"Silhouette Score: {score}")
    return score

def davies_bouldin_index(samples, labels):
    n_clusters = len(np.unique(labels))

    cluster_centroids = []
    cluster_scatter = []

    for i in range(n_clusters):
        points_in_cluster = samples[labels == i]
        centroid = np.mean(points_in_cluster, axis=0) 
        cluster_centroids.append(centroid)

        scatter = np.mean(np.linalg.norm(points_in_cluster - centroid, axis=1))
        cluster_scatter.append(scatter)

    db_index = 0
    for i in range(n_clusters):
        max_ratio = 0
        for j in range(n_clusters):
            if i != j:
                centroid_distance = np.linalg.norm(cluster_centroids[i] - cluster_centroids[j])
                ratio = (cluster_scatter[i] + cluster_scatter[j]) / centroid_distance
                max_ratio = max(max_ratio, ratio)
        db_index += max_ratio
    db_index /= n_clusters

    return db_index