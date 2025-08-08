import numpy as np
from scipy.spatial.distance import cdist

def d33_plus_score(data, labels):
    unique_labels = np.unique(labels)
    intra_cluster_distances = []
    inter_cluster_distances = []
    if -1 not in unique_labels:
        return calculate_dunn33(data, labels)
    
    for label in unique_labels:
        cluster_points = data[labels == label]
        centroid = np.mean(cluster_points, axis=0)
        
        intra_cluster_distance = np.mean(cdist(cluster_points, [centroid]))
        if label==-1:
            intra_cluster_distances.append((2/intra_cluster_distance))  # Δ3
        else:
            intra_cluster_distances.append(2 * intra_cluster_distance)  # Δ3
        
    for i, label1 in enumerate(unique_labels):
        for label2 in unique_labels[i + 1:]:
            if label1 ==-1 or label2 ==-1:
                continue
            else:
                cluster1_points = data[labels == label1]
                cluster2_points = data[labels == label2]
                inter_cluster_distance = np.mean(cdist(cluster1_points, cluster2_points))  # δ3
                inter_cluster_distances.append(inter_cluster_distance)
    
    noise_cluster_points = data[labels == -1]  
    num_noise_instances = len(noise_cluster_points)
    
    for label in unique_labels:
        if label ==-1:
            continue
        else:
            cluster_points = data[labels == label]
            
            cluster_to_noise_distances = cdist(cluster_points, noise_cluster_points)
            sorted_distances = np.sort(cluster_to_noise_distances, axis=1)
            
            #min one
            num_nearest_noise_instances = max(1, int(0.10 * num_noise_instances))
            nearest_noise_distances = sorted_distances[:, :num_nearest_noise_instances]
            
            avg_nearest_noise_distance = np.mean(nearest_noise_distances, axis=1)
            
            inter_cluster_distances.append(np.mean(avg_nearest_noise_distance))  

    min_inter_cluster_distance = np.min(inter_cluster_distances)
    max_intra_cluster_distance = np.max(intra_cluster_distances)
    
    dunn_index = min_inter_cluster_distance / max_intra_cluster_distance
    return dunn_index

def calculate_dunn33(data, labels):
    unique_labels = np.unique(labels)
    intra_cluster_distances = []
    inter_cluster_distances = []
    
    for label in unique_labels:
        cluster_points = data[labels == label]
        centroid = np.mean(cluster_points, axis=0)
        if label==-1:
            intra_cluster_distance = np.mean(cdist(cluster_points, [centroid]))
        else:
            intra_cluster_distance = np.mean(cdist(cluster_points, [centroid]))
        #Berechnet durchschnittlichen Abstand jedes Punktes zum Centroid und * 2
        intra_cluster_distances.append(2 * intra_cluster_distance)  # Δ3
        
    for i, label1 in enumerate(unique_labels):
        for label2 in unique_labels[i + 1:]:
            cluster1_points = data[labels == label1]
            cluster2_points = data[labels == label2]
            #Verwendet Durchschnitt Distanzen zwischen allen Punkten in zwei verschiedenen Clustern
            inter_cluster_distance = np.mean(cdist(cluster1_points, cluster2_points))  # δ3
            inter_cluster_distances.append(inter_cluster_distance)
      

    min_inter_cluster_distance = np.min(inter_cluster_distances)
    max_intra_cluster_distance = np.max(intra_cluster_distances)
    
    dunn_index = min_inter_cluster_distance / max_intra_cluster_distance
    return dunn_index