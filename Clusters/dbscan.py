import numpy as np
from Tools import *
from sklearn.cluster import DBSCAN as DBs

class DBSCAN:
    def __init__(self, samples, eps) -> None:
        self.samples = samples
        self.eps = eps
    def __call__(self):
         model = DBs(eps=self.eps, min_samples=2)
         labels = model.fit_predict(self.samples)
         return labels_and_get_centroids(self.samples, labels, len(list(set(labels))))