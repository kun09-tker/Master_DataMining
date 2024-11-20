
import numpy as np
from Tools import *
from sklearn.cluster import AgglomerativeClustering

class HierarchicalClustering:
    def __init__(self, samples, num_clusters) -> None:
        self.samples = samples
        self.num_clusters = num_clusters
    def agglomerative_clustering(self):
         model = AgglomerativeClustering(n_clusters=self.num_clusters)
         labels = model.fit_predict(self.samples)
         return labels_and_get_centroids(self.samples, labels, self.num_clusters)