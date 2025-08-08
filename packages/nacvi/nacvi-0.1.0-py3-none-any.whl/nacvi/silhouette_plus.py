import numpy as np


def sil_plus_score(data, labels):
    num_samples = len(data)
    silhouette_vals = np.zeros(num_samples)
    #further clusters except -1?
    if -1 in labels:
        if len(np.unique(labels)) < 3:
            return 0
    #at least 2 clusters
    elif len(np.unique(labels)) < 2:
        return 0
    for i in range(num_samples):
        if labels[i] >= 0:
            a_i = av_dist_within_cluster(i, labels[i], data, labels)
            b_i = av_dist_to_next_cluster(i, labels[i], data, labels)
            silhouette_vals[i] = silhouette_i(a_i, b_i)
        else:
            b_i = av_dist_to_next_cluster(i, labels[i], data, labels)
            c_i = av_dist_to_nextButOne_cluster(i, labels[i], data, labels)
            silhouette_vals[i] = min(
                1, 1 - silhouette_i(b_i, c_i)
            )  #maximum value 1
    silhouette_avg = np.mean(silhouette_vals)
    return silhouette_avg


def av_dist_within_cluster(i, cluster_i, data, labels):
    indices_cluster_i = np.where(labels == cluster_i)[0]
    distances = []
    for j in indices_cluster_i:
        if j != i:
            distances.append(np.linalg.norm(data[i] - data[j]))
    if len(distances) > 0:
        av_dist_cluster_i = np.mean(distances)
        return av_dist_cluster_i
    else:
        return 0


def av_dist_to_next_cluster(i, cluster_i, data, labels):
    unique_clusters = np.unique(labels)
    distances_to_other_clusters = []

    for j in unique_clusters:
        dist_to_others_in_j = []
        if j != cluster_i:
            #no dist calculation to noise
            if j < 0:
                continue
            samples_in_other_cluster = data[labels == j]
            for k in range(len(samples_in_other_cluster)):
                dist_to_others_in_j.append(
                    np.linalg.norm(data[i] - samples_in_other_cluster[k])
                )

            distances_to_other_clusters.append(np.mean(dist_to_others_in_j))
    #distance to the next cluster
    min_distance_to_other_clusters = min(distances_to_other_clusters)
    return min_distance_to_other_clusters


def av_dist_to_nextButOne_cluster(i, cluster_i, data, labels):
    unique_clusters = np.unique(labels)
    distances_to_other_clusters = []

    for j in unique_clusters:
        dist_to_others_in_j = []
        if j != cluster_i:
            #no dist calculation to noise
            if j < 0:
                continue
            samples_in_other_cluster = data[labels == j]
            for k in range(len(samples_in_other_cluster)):
                dist_to_others_in_j.append(
                    np.linalg.norm(data[i] - samples_in_other_cluster[k])
                )

            distances_to_other_clusters.append(np.mean(dist_to_others_in_j))
    #distance to the next cluster
    distances_to_other_clusters.sort()
    if len(distances_to_other_clusters) > 1:
        return distances_to_other_clusters[1]
    else:
        return -100


def silhouette_i(a_i, b_i):
    if max(a_i, b_i) == 0:
        return 0
    else:
        return (b_i - a_i) / max(a_i, b_i)