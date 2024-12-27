# similarity.py
import numpy as np

def compute_similarity(vector1: list, vector2: list):
    """
    Computes the cosine similarity between two vectors.

    Args:
        vector1 (list): The first vector.
        vector2 (list): The second vector.

    Returns:
        float: The cosine similarity between the two vectors.
    """
    v1 = np.nan_to_num(vector1)  # Replace NaN values with 0
    v2 = np.nan_to_num(vector2)
    
    #mask = ~np.isnan(vector1) & ~np.isnan(vector2)
    #v1, v2 = vector1[mask], vector2[mask]
    
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    if norm_v1 == 0 or norm_v2 == 0:
        return 0  # Handle cases where one or both vectors have zero norm
    return np.dot(v1, v2) / (norm_v1 * norm_v2)

if __name__ == "__main__":
    
    vector_a, vector_b = [1, 2, 3, 4], [4, 3, 2, 1]
    compute_similarity(vector_a, vector_b)
    