import numpy as np
from sklearn.metrics import pairwise_distances


def nr_plus_score(X, labels):
    unique_labels = np.unique(labels)
    noise_label = -1

    if noise_label not in unique_labels:
        return 1
    if len(unique_labels) < 2:
        return 1
    max_distances = []
    for label in unique_labels:
        if label == noise_label:
            continue
        cluster_points = X[labels == label]
        if len(cluster_points) > 1:
            distances = pairwise_distances(cluster_points)
            max_distance = np.max(distances)
            max_distances.append(max_distance)

    #neighborhood radius
    neighborhood_radius = min(max_distances) * 0.5

    def count_neighbors_within_radius(point, radius):
        distances = pairwise_distances(X, point.reshape(1, -1)).flatten()
        return np.sum(distances <= radius) - 1

    neighbor_counts = np.array(
        [count_neighbors_within_radius(point, neighborhood_radius) for point in X]
    )

    noise_neighbor_counts = neighbor_counts[labels == noise_label]
    cluster_neighbor_counts = neighbor_counts[labels != noise_label]

    #neighbor-Ratio
    if len(noise_neighbor_counts) == 0 or len(cluster_neighbor_counts) == 0:
        return 1

    mean_noise_neighbors = np.mean(noise_neighbor_counts)
    mean_cluster_neighbors = np.mean(cluster_neighbor_counts)

    neighbor_ratio = scaled_ratio(mean_noise_neighbors, mean_cluster_neighbors)
    return neighbor_ratio


def scaled_ratio(mean_noise, mean_clust):
    
    return 1 - np.exp(-(mean_clust - mean_noise))