import numpy as np
from itertools import combinations


def dbi_plus_score(data, labels):

    cluster_labels = np.unique(labels)
    minimum = np.amin(cluster_labels)
    num_clusters = len(np.unique(labels))
    #further clusters except -1?
    if -1 in labels:
        noise_points = len(data[labels == -1])
        if num_clusters < 3:
            return (3 - 0) / (3 - 0)
    #at least 2 clusters?
    elif num_clusters < 2:
        return (3 - 0) / (3 - 0)

    centroids = []
    for i in cluster_labels:
        cluster_points = data[labels == i]
        centroid = np.mean(cluster_points, axis=0)
        centroids.append(centroid)

    intra_cluster_distances = []
    for cluster_i in cluster_labels:
        indices_cluster_i = [i for i, x in enumerate(labels) if x == cluster_i]
        distances = []
        for index in indices_cluster_i:
            if cluster_i == -1:
                distances.append(0)
            else:
                if -1 in cluster_labels:
                    distances.append(
                        np.linalg.norm(data[index] - centroids[cluster_i + 1])
                    )
                elif minimum == 0:
                    distances.append(np.linalg.norm(data[index] - centroids[cluster_i]))
                else:
                    distances.append(
                        np.linalg.norm(data[index] - centroids[cluster_i - 1])
                    )
        avg_intra_cluster_distance = np.mean(distances)
        intra_cluster_distances.append(avg_intra_cluster_distance)

    inter_cluster_distances = np.zeros((num_clusters, num_clusters))
    noise_indices = [i for i, x in enumerate(labels) if x == -1]
    for cluster1, cluster2 in combinations(cluster_labels, 2):
        if cluster1 != cluster2:
            if -1 in cluster_labels:
                if cluster1 == -1:
                    dist = calculate_average_distance_to_centroid(
                        data[noise_indices], centroids[cluster2]
                    )
                    inter_cluster_distances[cluster1 + 1, cluster2 + 1] = dist
                    inter_cluster_distances[cluster2 + 1, cluster1 + 1] = dist
                elif cluster2 == -1:
                    dist = calculate_average_distance_to_centroid(
                        data[noise_indices], centroids[cluster1]
                    )
                    inter_cluster_distances[cluster1 + 1, cluster2 + 1] = dist
                    inter_cluster_distances[cluster2 + 1, cluster1 + 1] = dist
                else:
                    dist = np.linalg.norm(centroids[cluster1] - centroids[cluster2])
                    inter_cluster_distances[cluster1 + 1, cluster2 + 1] = dist
                    inter_cluster_distances[cluster2 + 1, cluster1 + 1] = dist
            elif minimum == 0:
                dist = np.linalg.norm(centroids[cluster1] - centroids[cluster2])
                inter_cluster_distances[cluster1, cluster2] = dist
                inter_cluster_distances[cluster2, cluster1] = dist
            else:
                dist = np.linalg.norm(centroids[cluster1 - 1] - centroids[cluster2 - 1])
                inter_cluster_distances[cluster1 - 1, cluster2 - 1] = dist
                inter_cluster_distances[cluster2 - 1, cluster1 - 1] = dist

    davies_bouldin_values = []
    for i in cluster_labels:
        max_ratio = -1000
        for j in cluster_labels:
            if i != j:
                if i == -1:
                    noise_ratio = noise_points / len(data)
                    add = np.max(inter_cluster_distances) * noise_ratio
                    ratio = (
                        add
                    ) / inter_cluster_distances[i + 1, j + 1]
                elif j == -1:
                    noise_ratio = noise_points / len(data)
                    add = np.max(inter_cluster_distances) * noise_ratio
                    ratio = (
                        add
                    ) / inter_cluster_distances[i + 1, j + 1]
                else:
                    if -1 in cluster_labels:
                        ratio = (
                            intra_cluster_distances[i + 1]
                            + intra_cluster_distances[j + 1]
                        ) / inter_cluster_distances[i + 1, j + 1]
                    elif minimum == 0:
                        ratio = (
                            intra_cluster_distances[i] + intra_cluster_distances[j]
                        ) / inter_cluster_distances[i, j]
                    else:
                        ratio = (
                            intra_cluster_distances[i - 1]
                            + intra_cluster_distances[j - 1]
                        ) / inter_cluster_distances[i - 1, j - 1]
                if ratio > max_ratio:
                    max_ratio = ratio
        davies_bouldin_values.append(max_ratio)

    davies_bouldin_index = np.mean(davies_bouldin_values)
    if davies_bouldin_index > 3:
        davies_bouldin_index = 3
    if davies_bouldin_index < 0:
        davies_bouldin_index = 3
    return (davies_bouldin_index - 0) / (3 - 0)


def calculate_average_distance_to_centroid(noise_data, centroid):
    distances = [np.linalg.norm(point - centroid) for point in noise_data]
    return np.min(distances)