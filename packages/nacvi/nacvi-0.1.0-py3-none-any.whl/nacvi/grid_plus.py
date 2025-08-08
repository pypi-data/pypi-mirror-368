from itertools import combinations
import numpy as np
from collections import defaultdict

def grid_plus_score(data, labels):
    unique_labels = np.unique(labels)
    noise_label = -1

    if noise_label not in unique_labels:
        return 1
    if len(unique_labels) < 2:
        return 1
    clust_points, noise_points, num_cells = grid_evaluation(data, labels)
    clust_vals = list(clust_points.values())
    all_points = clust_points.copy()
    for cell_index, count in noise_points.items():
        all_points[cell_index] += count

    noise_vals = list(noise_points.values())
    if len(noise_vals) == 0:
        return 1  

    cluster_cell_points = []
    noise_cell_points = []

    for cell_index in all_points.keys():
        if cell_index in clust_points:
            cluster_cell_points.append(all_points[cell_index])
        else:
            noise_cell_points.append(all_points[cell_index])

    mean_noise_cells = np.mean(noise_cell_points) if len(noise_cell_points) > 0 else 0
    mean_clust_cells = (
        np.mean(cluster_cell_points) if len(cluster_cell_points) > 0 else 0
    )

    gridval_b = (
        1 - ((mean_noise_cells) / mean_clust_cells) if mean_clust_cells > 0 else 0
    )
    return gridval_b

def minimum_cluster_maxDist(data, cluster_labels):
    min_diameter = 100.0
    unique_labels = np.unique(cluster_labels)
    max_distance = 0.0

    for label in unique_labels:
        if label == -1:  #jump over noise
            continue
        cluster_points = data[cluster_labels == label]
        if len(cluster_points) < 2:
            continue
        for pair in combinations(cluster_points, 2):
            distance = np.linalg.norm(pair[0] - pair[1])
            if distance > max_distance:
                max_distance = distance
        if max_distance > 0.0:
            if max_distance < min_diameter:
                min_diameter = max_distance
    return min_diameter


def minimum_cluster_meanDist(data, cluster_labels):
    min_diameter = 100.0
    unique_labels = np.unique(cluster_labels)
    max_distance = 0.0

    for label in unique_labels:
        if label == -1:  #jump over noise
            continue
        cluster_points = data[cluster_labels == label]
        if len(cluster_points) < 2:
            continue
        distance = np.mean(cluster_points)
        if distance > max_distance:
            max_distance = distance
        if max_distance > 0.0:
            if max_distance < min_diameter:
                min_diameter = max_distance
    return min_diameter


def grid_evaluation(data, cluster_labels):
    num_dimensions = len(data[0])
    cell_size = minimum_cluster_maxDist(data, cluster_labels) * 0.5
    min_values = np.min(data, axis=0)
    max_values = np.max(data, axis=0)

    cluster_points_count = defaultdict(int)
    noise_points_count = defaultdict(int)

    for point, label in zip(data, cluster_labels):
        #calculate cell index for each instance
        cell_indices = []
        for i in range(num_dimensions):
            p = point[i]
            mv = min_values[i]
            cell_indices.append(int((p - mv) / cell_size))

        cell_indices = tuple(cell_indices)

        #counter for cluster and noise instances
        if label >= 0:
            cluster_points_count[cell_indices] += 1
        else:
            noise_points_count[cell_indices] += 1

    num_cells = []
    for i in range(num_dimensions):
        nc = int(np.ceil((max_values[i] - min_values[i]) / cell_size)) + 1
        num_cells.append(nc if nc > 1 else 2)
    num_cellsl = np.prod(num_cells)
    return cluster_points_count, noise_points_count, num_cellsl


