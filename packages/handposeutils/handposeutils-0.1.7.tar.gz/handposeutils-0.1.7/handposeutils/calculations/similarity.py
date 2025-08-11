import numpy as np
from typing import Tuple, List
from handposeutils.data.handpose import HandPose

def procrustes_alignment(pose1: HandPose, pose2: HandPose) -> Tuple[np.ndarray, np.ndarray, float]:
    """
    Perform Procrustes alignment between two 3D hand poses.

    The alignment process removes translation, scale, and rotation differences
    between two `HandPose` objects, returning their aligned coordinates and
    the Procrustes distance (sum of squared differences).

    It is STRONGLY recommended to normalize HandPoses before computing Euclidean distance.

    Parameters
    ----------
    pose1 : HandPose
        First hand pose to align.
    pose2 : HandPose
        Second hand pose to align against.

    Returns
    -------
    aligned_pose1 : ndarray of shape (n_landmarks, 3)
        Aligned version of `pose1` after Procrustes transformation.
    aligned_pose2 : ndarray of shape (n_landmarks, 3)
        Normalized version of `pose2` for comparison.
    distance : float
        Procrustes distance between aligned poses. Lower values indicate
        greater similarity.

    Raises
    ------
    ValueError
        If the number of landmarks (or their dimensionality) differs between poses.

    Notes
    -----
    - This method uses the Kabsch algorithm to compute the optimal rotation.
    - The Procrustes distance is **not** invariant to landmark correspondence errors.
    """

    # Step 1: Convert HandPoses to N x 3 numpy arrays
    p1 = np.array([coord.as_tuple() for coord in pose1.get_all_coordinates()])
    p2 = np.array([coord.as_tuple() for coord in pose2.get_all_coordinates()])

    if p1.shape != p2.shape:
        raise ValueError(f"Shape mismatch: pose1 has shape {p1.shape}, pose2 has shape {p2.shape}")

    # Step 2: Center both poses at the origin
    p1_centered = p1 - p1.mean(axis=0)
    p2_centered = p2 - p2.mean(axis=0)

    # Step 3: Normalize scale (Frobenius norm)
    p1_scaled = p1_centered / np.linalg.norm(p1_centered)
    p2_scaled = p2_centered / np.linalg.norm(p2_centered)

    # Step 4: Compute optimal rotation matrix using Kabsch algorithm
    H = p1_scaled.T @ p2_scaled
    U, S, Vt = np.linalg.svd(H)
    R = Vt.T @ U.T

    # Fix reflection issues
    if np.linalg.det(R) < 0:
        Vt[-1, :] *= -1
        R = Vt.T @ U.T

    # Step 5: Apply rotation to pose1
    p1_aligned = p1_scaled @ R
    p2_aligned = p2_scaled

    # Step 6: Compute Procrustes distance (residual sum of squares)
    distance = np.sum((p1_aligned - p2_aligned) ** 2)

    return p1_aligned, p2_aligned, distance

def euclidean_distance(pose1: HandPose, pose2: HandPose) -> float:
    """
    Compute the mean Euclidean distance between two hand poses.

    This function calculates the average distance between corresponding
    landmarks of two `HandPose` objects. Distances are computed directly
    in 3D space and are sensitive to both scale and translation.

    It is STRONGLY recommended to normalize HandPoses before computing Euclidean distance.

    Parameters
    ----------
    pose1 : HandPose
        First hand pose.
    pose2 : HandPose
        Second hand pose.

    Returns
    -------
    mean_distance : float
        Mean Euclidean distance between corresponding landmarks. Lower values
        indicate greater similarity.

    Raises
    ------
    ValueError
        If the number of landmarks (or their dimensionality) differs between poses.
    """
    p1 = np.array([coord.as_tuple() for coord in pose1.get_all_coordinates()])
    p2 = np.array([coord.as_tuple() for coord in pose2.get_all_coordinates()])

    if p1.shape != p2.shape:
        raise ValueError(f"Shape mismatch: pose1 has shape {p1.shape}, pose2 has shape {p2.shape}")

    distances = np.linalg.norm(p1 - p2, axis=1)
    return np.mean(distances)

def cosine_similarity(pose1: HandPose, pose2: HandPose) -> float:
    """
    Compute cosine similarity between two 3D hand poses.

    Each pose is represented as a flattened 63-dimensional vector
    (21 landmarks × 3 coordinates). The cosine similarity measures the
    angular difference between the vectors, making it invariant to scale
    but not to translation, so position is first normalized.

    Parameters
    ----------
    pose1 : HandPose
        First hand pose.
    pose2 : HandPose
        Second hand pose.

    Returns
    -------
    similarity : float
        Cosine similarity in the range [-1, 1].
        - `1.0` indicates identical orientation.
        - `0.0` indicates orthogonal poses.
        - `-1.0` indicates opposite orientation.

    Notes
    -----
    - This method normalizes translation by centering poses before comparison.
    - Similarity is undefined for zero-length pose vectors (returns 0.0).
    """
    pose1.normalize_position()
    pose2.normalize_position()

    vec1 = np.array([c for coord in pose1.get_all_coordinates() for c in coord.as_tuple()])
    vec2 = np.array([c for coord in pose2.get_all_coordinates() for c in coord.as_tuple()])

    dot = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0.0  # Cannot compare with a zero vector

    similarity = dot / (norm1 * norm2)
    return similarity

def _joint_angle_descriptor(pose: HandPose) -> List[float]:
    """
    Helper to extract joint angles in radians from a hand pose.

    The angles are calculated between consecutive segments in each finger,
    forming a compact biomechanical descriptor of the pose.

    Parameters
    ----------
    pose : HandPose
        The hand pose to describe. Must contain 21 landmarks in MediaPipe format.

    Returns
    -------
    list of float
        List of joint angles in radians, ordered finger by finger.
        Each value corresponds to the angle at a specific finger joint.
    """
    angles = []
    finger_joints = {
        "thumb": [1, 2, 3, 4],
        "index": [5, 6, 7, 8],
        "middle": [9, 10, 11, 12],
        "ring": [13, 14, 15, 16],
        "pinky": [17, 18, 19, 20],
    }

    for finger, indices in finger_joints.items():
        for i in range(1, len(indices) - 1):
            a = pose.get_coordinate_by_index(indices[i - 1])
            b = pose.get_coordinate_by_index(indices[i])
            c = pose.get_coordinate_by_index(indices[i + 1])

            # Vectors: b→a and b→c
            v1 = np.array([a.x - b.x, a.y - b.y, a.z - b.z])
            v2 = np.array([c.x - b.x, c.y - b.y, c.z - b.z])

            # Angle between v1 and v2
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)
            if norm1 == 0 or norm2 == 0:
                angle = 0.0
            else:
                cos_angle = np.clip(np.dot(v1, v2) / (norm1 * norm2), -1.0, 1.0)
                angle = np.arccos(cos_angle)

            angles.append(angle)

    return angles

def joint_angle_similarity(pose1: HandPose, pose2: HandPose) -> float:
    """
    Computes biomechanical similarity between two hand poses using joint angles.

    The joint angles of each pose are extracted and compared using mean squared
    difference. Lower values indicate more similar poses.

    Parameters
    ----------
    pose1 : HandPose
        First hand pose.
    pose2 : HandPose
        Second hand pose.

    Returns
    -------
    float
        Mean squared difference between joint angles.
        A value of 0.0 indicates identical angles.

    Raises
    ------
    ValueError
        If the angle descriptors have different lengths.

    Notes
    -----
    - Useful in determining similarity in joint curvature across regions of the hand,
    when used consecutively.
    - Can represent the same information as geometry.get_finger_curvature() when multiple function calls are fused.

    See Also
    --------
    geometry.get_finger_curvature()

    """
    angles1 = _joint_angle_descriptor(pose1)
    angles2 = _joint_angle_descriptor(pose2)

    if len(angles1) != len(angles2):
        raise ValueError("Angle descriptors must be of same length")

    diff = np.array(angles1) - np.array(angles2)
    return float(np.mean(diff ** 2))

def compute_joint_angle_errors(pose1: HandPose, pose2: HandPose) -> List[float]:
    """
    Computes per-joint absolute angle differences between two hand poses.

    This method assumes the standard 21-landmark MediaPipe format. Angles are
    measured in radians for each consecutive finger joint triplet.

    Parameters
    ----------
    pose1 : HandPose
        First hand pose.
    pose2 : HandPose
        Second hand pose.

    Returns
    -------
    list of float
        Absolute differences in radians for each joint, ordered finger by finger.
    """
    from math import acos
    from numpy.linalg import norm

    def angle_between(v1, v2):
        dot = np.dot(v1, v2)
        return acos(np.clip(dot / (norm(v1) * norm(v2) + 1e-6), -1.0, 1.0))

    pairs = [
        (1, 2, 3), (2, 3, 4),     # Thumb
        (5, 6, 7), (6, 7, 8),     # Index
        (9, 10, 11), (10, 11, 12),# Middle
        (13, 14, 15), (14, 15, 16),# Ring
        (17, 18, 19), (18, 19, 20) # Pinky
    ]

    angles1 = []
    angles2 = []

    for a, b, c in pairs:
        v1a = pose1[b] - pose1[a]
        v1b = pose1[c] - pose1[b]
        angles1.append(angle_between(v1a.as_tuple(), v1b.as_tuple()))

        v2a = pose2[b] - pose2[a]
        v2b = pose2[c] - pose2[b]
        angles2.append(angle_between(v2a.as_tuple(), v2b.as_tuple()))

    return np.abs(np.array(angles1) - np.array(angles2))


def pose_similarity(pose1: HandPose, pose2: HandPose, method: str = 'procrustes') -> float:
    """
    Computes similarity between two hand poses using the specified method.

    Supported methods
    -----------------
    - 'procrustes': Procrustes distance (lower = more similar)
    - 'euclidean' : Euclidean distance
    - 'cosine'    : Cosine similarity
    - 'joint_angle': Mean squared joint angle difference

    Parameters
    ----------
    pose1 : HandPose
        First hand pose.
    pose2 : HandPose
        Second hand pose.
    method : str, default='procrustes'
        Similarity computation method.

    Returns
    -------
    float
        Similarity score according to the chosen method.
        Scale and interpretation vary depending on the method.

    Raises
    ------
    NotImplementedError
        If the given method is not supported.
    """
    if method == 'procrustes':
        _, _, distance = procrustes_alignment(pose1, pose2)
        return distance
    elif method == 'euclidean':
        return euclidean_distance(pose1, pose2)
    elif method == 'cosine':
        return cosine_similarity(pose1, pose2)
    elif method == 'joint_angle':
        return joint_angle_similarity(pose1, pose2)
    else:
        raise NotImplementedError(f"Similarity method '{method}' is not implemented.")


## --- Implementations for Embedding Similarity --- ##

def embedding_similarity(vec1: np.ndarray, vec2: np.ndarray, method: str = "cosine", **kwargs) -> float:
    """
    Computes similarity or distance between two embedding vectors or sequences.

    Supports:
    - Single embeddings (1D arrays)
    - Temporal embeddings (2D arrays of shape [sequence_length, embedding_dim]),
      where similarity is computed per frame and averaged.

    Parameters
    ----------
    vec1 : numpy.ndarray
        First embedding vector or sequence.
    vec2 : numpy.ndarray
        Second embedding vector or sequence.
    method : str, default="cosine"
        Method to compute similarity. Options:
        - 'cosine'
        - 'euclidean'
        - 'manhattan'
        - 'mahalanobis'
    **kwargs
        Additional parameters for specific methods. For example:
        - cov : numpy.ndarray
            Covariance matrix for Mahalanobis distance.

    Returns
    -------
    tuple of (str, float)
        The method name and the computed similarity or distance score.
        For cosine similarity, higher is more similar.
        For distances, lower is more similar.

    Raises
    ------
    ValueError
        If vectors have different shapes, or covariance matrix shape is invalid.
    NotImplementedError
        If the given method is not supported.
    """
    if vec1.shape != vec2.shape:
        raise ValueError(f"Vectors must be same shape. Got {vec1.shape} vs {vec2.shape}")

    # If both are 2D (sequence case), compute per-frame similarity and average
    if vec1.ndim == 2 and vec2.ndim == 2:
        scores = []
        for frame1, frame2 in zip(vec1, vec2):
            _, score = embedding_similarity(frame1, frame2, method=method, **kwargs)
            scores.append(score)
        return method, float(np.mean(scores))

    # --- Single vector similarity ---
    if method == "cosine":
        dot_product = np.dot(vec1, vec2)
        norm_a = np.linalg.norm(vec1)
        norm_b = np.linalg.norm(vec2)
        if norm_a == 0 or norm_b == 0:
            return "cosine", 0.0
        return "cosine", float(dot_product / (norm_a * norm_b))

    elif method == "euclidean":
        diff = vec1 - vec2
        return "euclidean", float(np.sqrt(np.sum(diff ** 2)))

    elif method == "manhattan":
        return "manhattan", float(np.sum(np.abs(vec1 - vec2)))

    elif method == "mahalanobis":
        diff = vec1 - vec2
        cov = kwargs.get("cov", np.eye(len(vec1)))
        if cov.shape != (len(vec1), len(vec1)):
            raise ValueError(f"Covariance matrix must be shape ({len(vec1)}, {len(vec1)}), got {cov.shape}")
        try:
            inv_cov = np.linalg.inv(cov)
        except np.linalg.LinAlgError:
            raise ValueError("Covariance matrix is not invertible.")
        dist = np.dot(np.dot(diff.T, inv_cov), diff)
        return "mahalanobis", float(np.sqrt(dist))

    else:
        raise NotImplementedError(f"Unknown method '{method}'.")
