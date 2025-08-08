import numpy as np

def sf_plus_score(data, labels):
    unique_labels = np.unique(labels)
    clusters = {k: data[labels == k] for k in unique_labels}
    cluster_centroids = {k: np.mean(clusters[k], axis=0) for k in clusters}
    global_centroid = np.mean(data, axis=0)
    N = data.shape[0]
    K = len(clusters)
    if -1 in unique_labels:
        K -= 1

    bcd = calculate_bcd(clusters, cluster_centroids, global_centroid, N, K)
    wcd = calculate_wcd(clusters, cluster_centroids)

    sf = 1 - 1 / (np.exp(np.exp(bcd - wcd)))
    return sf

def euclidean_distance(a, b):
    return np.linalg.norm(a - b)


def calculate_bcd(clusters, cluster_centroids, global_centroid, N, K):
    #between-cluster distance
    bcd = 0
    for k in clusters:
        cluster_size = len(clusters[k])
        ed = euclidean_distance(cluster_centroids[k], global_centroid)
        if k == -1:
            val = cluster_size * (1 / ed)
            bcd += val
        else:
            val = cluster_size * ed
            bcd += val
    bcd /= N * K
    return bcd


#within-cluster distance
def calculate_wcd(clusters, cluster_centroids):
    wcd = 0
    for k in clusters:
        cluster = clusters[k]
        centroid = cluster_centroids[k]
        cluster_size = len(cluster)
        val=np.sum([euclidean_distance(x, centroid) for x in cluster]) 
        if cluster_size > 0:
            if k == -1:
                intra_cluster_distances = (
                    1 / val
                )
            else:
                intra_cluster_distances = val
            wcd += intra_cluster_distances / cluster_size
    return wcd


