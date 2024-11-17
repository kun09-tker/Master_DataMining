# from Tools import *

# class HierarchicalClustering():
#     def __init__(self, samples, num_clusters) -> None:
#         self.samples = samples
#         self.num_samples = len(samples)
#         self.num_clusters = num_clusters

#     def agglomerative_clustering(self):
#         clusters = [[i] for i in range(self.num_samples)]
#         distance_matrix = distance_matrix(self.samples)
#         while len(clusters) > self.num_clusters:
#             min_distance = float('inf')
#             closest_clusters = None
#             for i in range(len(clusters)):
#                 for j in range(i+1, len(clusters)):
#                     distance 