
import numpy as np
from Tools import *
from sklearn.cluster import KMeans

class K_Means:
    def __init__(self, samples, num_clusters) -> None:
        self.samples = samples
        self.num_clusters = num_clusters
    def __call__(self):
         model = KMeans(n_clusters=self.num_clusters, random_state=42)
         model.fit_predict(self.samples)
         return model.cluster_centers_, model.labels_