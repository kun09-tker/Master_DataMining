import numpy as np
from Tools import euclidean_distance

class K_Means ():
    def __init__(self, samples, num_clusters, loop=100) -> None:
        self.samples = samples
        self.num_features = samples.shape[1]
        self.num_samples = len(samples)
        self.num_clusters = num_clusters
        self.loop = loop

    def __call__(self):
        init_index = np.random.choice(
            self.num_samples,
            self.num_clusters,
            replace=False
        )
        centroids = self.samples[init_index]
        for i in range(self.loop):
            labels = np.zeros(self.num_samples)
            for idx, student in enumerate(self.samples):
                distances = euclidean_distance(student, centroids)
                labels[idx] = np.argmin(distances)
            
            new_centroids = np.zeros((self.num_clusters, self.num_features))
            for k in range(self.num_clusters):
                student_in_cluster = self.samples[labels == k]
                if len(student_in_cluster) > 0:
                    new_centroids[k] = student_in_cluster.mean(axis=0)
                else:
                    rand_index = np.random.choice(
                        self.num_samples
                    )
                    new_centroids[k] = self.samples[rand_index]
            
            if np.all(centroids == new_centroids):
                break

            centroids = new_centroids
        
        return labels, centroids






