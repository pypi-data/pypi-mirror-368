# vector.py
# encoder for geometric, latent, and graph-based embeddings

import numpy as np
from math import acos
from typing import List
from handposeutils.data.handpose import HandPose
from handposeutils.data.coordinate import Coordinate
from typing import Callable, Optional, Tuple


def get_joint_angle_vector(pose: HandPose) -> np.ndarray:
    """
    Generate a 15D joint-angle embedding vector for a HandPose.
    Each finger contributes 3 angles: two intra-finger and one base-to-knuckle angle.
    ||NORMALIZE HANDPOSE BEFORE EMBEDDING||

    :param pose: HandPose
    :return: np.ndarray of shape (15,) containing angles in radians.
    """

    def compute_angle(a: Coordinate, b: Coordinate, c: Coordinate) -> float:
        """Compute angle at point b formed by (a - b - c) using cosine rule."""
        v1 = np.array([a.x - b.x, a.y - b.y, a.z - b.z])
        v2 = np.array([c.x - b.x, c.y - b.y, c.z - b.z])
        dot = np.dot(v1, v2)
        norm = np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8
        cos_angle = np.clip(dot / norm, -1.0, 1.0)
        return acos(cos_angle)

    # Define angle triplets (a, b, c)
    triplets: List[tuple[int, int, int]] = [
        # Thumb
        (1, 2, 3), (2, 3, 4), (0, 1, 2),
        # Index
        (5, 6, 7), (6, 7, 8), (0, 5, 6),
        # Middle
        (9, 10, 11), (10, 11, 12), (0, 9, 10),
        # Ring
        (13, 14, 15), (14, 15, 16), (0, 13, 14),
        # Pinky
        (17, 18, 19), (18, 19, 20), (0, 17, 18),
    ]

    angles = []
    for a_idx, b_idx, c_idx in triplets:
        a, b, c = pose[a_idx], pose[b_idx], pose[c_idx]
        angle = compute_angle(a, b, c)
        angles.append(angle)

    return np.array(angles)


def get_bone_length_vector(pose: HandPose) -> np.ndarray:
    """
    Compute a 20D bone length vector from a HandPose, representing each bone segment.
    ||NORMALIZE HANDPOSE BEFORE EMBEDDING||

    :param pose: HandPose
    :return: np.ndarray of shape (20,) containing bone lengths.
    """
    bone_pairs: List[tuple[int, int]] = [
        # Thumb
        (0, 1), (1, 2), (2, 3), (3, 4),
        # Index
        (0, 5), (5, 6), (6, 7), (7, 8),
        # Middle
        (0, 9), (9, 10), (10, 11), (11, 12),
        # Ring
        (0, 13), (13, 14), (14, 15), (15, 16),
        # Pinky
        (0, 17), (17, 18), (18, 19), (19, 20)
    ]

    lengths = []
    for i, j in bone_pairs:
        coord_i = pose[i]
        coord_j = pose[j]
        dist = np.linalg.norm(np.array(coord_j.as_tuple()) - np.array(coord_i.as_tuple()))
        lengths.append(dist)

    return np.array(lengths)


def get_relative_vector_embedding(pose: HandPose) -> np.ndarray:
    """
    Compute a 63D vector of relative positions of each landmark from the wrist.
    ||NORMALIZE HANDPOSE BEFORE EMBEDDING||

    :param pose: HandPose
    :return: np.ndarray of shape (63,) representing relative landmark positions.
    """
    wrist = pose[0]
    relative_coords = []

    for i in range(21):
        pt = pose[i]
        vec = np.array([pt.x - wrist.x, pt.y - wrist.y, pt.z - wrist.z])
        relative_coords.extend(vec)

    return np.array(relative_coords)

def get_fused_pose_embedding(pose: HandPose) -> np.ndarray:
    """
    Compute a 98D vector of intrinsic hand qualities (joint angles-15D, bone length-20D, relative landmark locations-63D)
    ||NORMALIZE HANDPOSE BEFORE EMBEDDING||
    :param pose: HandPose
    :return: np.ndarray of shape (98,), a full representation of hand qualities from a HandPose. 98D vector = 15D+20D+63D.
    """
    angles = get_joint_angle_vector(pose)
    lengths = get_bone_length_vector(pose)
    rel = get_relative_vector_embedding(pose)

    return np.concatenate([angles, lengths, rel])

from handposeutils.data.handpose_sequence import HandPoseSequence

def _sinusoidal_time_encoding(timestamps: np.ndarray, dim: int, time_scale: float = 1.0) -> np.ndarray:
    """
    Continuous sinusoidal positional encoding (Transformer-style) adapted for timestamps.

    Parameters
    ----------
    timestamps : np.ndarray, shape (T,)
        Time values in seconds.
    dim : int
        Desired encoding dimension; if odd, last column uses sine.
    time_scale : float
        Scale factor that shifts the frequency spectrum. Larger = slower oscillations.

    Returns
    -------
    enc : np.ndarray, shape (T, dim)
    """
    if timestamps.size == 0:
        return np.zeros((0, dim), dtype=float)

    t = timestamps.astype(np.float64) * time_scale  # scale timestamps
    enc = np.zeros((t.shape[0], dim), dtype=float)

    # Use same formula as transformer: pos / (10000^(2i/dim))
    # But with continuous time t instead of integer position.
    # We compute angles = t / (base ** (2i/dim)), where base is 10000.
    base = 10000.0
    half = dim // 2
    denom = base ** (2.0 * np.arange(half) / float(dim))
    angles = np.outer(t, 1.0 / denom)  # shape (T, half)

    enc[:, 0::2] = np.sin(angles)
    if dim % 2 == 0:
        enc[:, 1::2] = np.cos(angles)
    else:
        # if odd, last column take cos of angles[:, -1] (pad)
        enc[:, 1::2][:, :angles.shape[1]] = np.cos(angles)
        # remaining last column left as zeros or copy a cos; keep zeros to avoid confusion
    return enc


def _compute_velocities(embeddings: np.ndarray, timestamps: Optional[np.ndarray] = None) -> np.ndarray:
    """
    Compute first-order temporal differences (velocities) of per-frame embeddings.
    If timestamps provided, compute dt-scaled velocities: (e_t - e_{t-1}) / dt

    Returns same shape as embeddings (T, D) with first row zeros.
    """
    if embeddings.shape[0] == 0:
        return np.zeros_like(embeddings)

    if timestamps is None:
        # simple frame-to-frame diff, prepend zeros
        diffs = np.vstack([np.zeros((1, embeddings.shape[1])), np.diff(embeddings, axis=0)])
        return diffs
    else:
        t = timestamps
        dt = np.diff(t, prepend=t[0])
        dt[dt == 0] = 1.0  # avoid division by zero (if same timestamp, treat as unit time)
        diffs = np.vstack([np.zeros((1, embeddings.shape[1])), np.diff(embeddings, axis=0)])
        # scale by 1/dt per row
        diffs = diffs / dt[:, None]
        return diffs


def _uniform_downsample(array: np.ndarray, target_len: int) -> np.ndarray:
    """
    Uniformly sample rows from `array` to length `target_len`.
    If array shorter than target_len, returns array unchanged (padding handled elsewhere).
    """
    n = array.shape[0]
    if n <= target_len:
        return array.copy()
    indices = np.linspace(0, n - 1, num=target_len, dtype=int)
    return array[indices]


def _pca_reduce(matrix: np.ndarray, n_components: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Simple PCA using SVD. Returns (reduced, components, mean)
    - matrix: shape (N, D)
    - reduced: shape (N, n_components)
    """
    if matrix.size == 0:
        return matrix.copy(), np.zeros((0, matrix.shape[1])), np.zeros((matrix.shape[1],))
    # center
    mean = matrix.mean(axis=0)
    M = matrix - mean
    # SVD
    U, S, Vt = np.linalg.svd(M, full_matrices=False)
    components = Vt[:n_components]  # (n_components, D)
    reduced = M @ components.T  # (N, n_components)
    return reduced, components, mean


def structured_temporal_embedding(
    sequence: HandPoseSequence,
    pose_embedding_fn: Callable[[object], np.ndarray],
    max_length: Optional[int] = None,
    include_velocity: bool = True,
    time_scale: float = 1.0,
    downsample: Optional[str] = "uniform",  # or None
    pca_components: Optional[int] = None,
    verbose: bool = False
) -> np.ndarray:
    """
    Build a structured temporal embedding for a HandPoseSequence.

    Parameters
    ----------
    sequence : HandPoseSequence
        Sequence object containing timed poses. Must expose `.sequence` (list of TimedHandPose)
        and `get_all_timestamps()` returning list of start_times (float).
    pose_embedding_fn : Callable[[HandPose], np.ndarray]
        Function to compute a static embedding for a single HandPose.
    max_length : Optional[int]
        If provided, sequence will be truncated (or padded later) to this length.
    include_velocity : bool
        Whether to append first-order velocity vectors per frame.
    time_scale : float
        Scale factor for continuous positional encoding.
    downsample : Optional[str]
        If 'uniform', will uniformly sample frames if sequence longer than max_length.
        If None, do not downsample (but truncation might still occur).
    pca_components : Optional[int]
        If provided, reduce per-frame dimension to `pca_components` using PCA.
    verbose : bool
        If True, print some debug info.

    Returns
    -------
    embeddings_struct : np.ndarray, shape (T_out, D_out)
        Structured embedding where T_out == max_length (if provided) else original seq length,
        and D_out == per-frame-dim (pose_emb_dim [+ posenc_dim (same as pose_emb_dim)] [+ velocity dim]).
    """
    # 1) Validate and extract
    seq_len = len(sequence)
    if seq_len == 0:
        if verbose:
            print("[structured_temporal_embedding] empty sequence -> returning zeros")
        if max_length is None:
            return np.zeros((0, 0), dtype=float)
        else:
            # return zero padded output: T x D; but we don't know D yet; choose pose_embedding_fn on a dummy?
            dummy = pose_embedding_fn(sequence.current_pose) if sequence.current_pose is not None else None
            if dummy is None:
                # cannot infer dimension; return zeros with shape (max_length, 0)
                return np.zeros((max_length, 0), dtype=float)
            pose_dim = dummy.shape[0]
            per_frame_dim = pose_dim * (2 + (1 if include_velocity else 0))  # pose + posenc + velocity
            return np.zeros((max_length, per_frame_dim), dtype=float)

    timestamps = np.array(sequence.get_all_timestamps(), dtype=float)  # (T,)

    # 2) Compute per-frame pose embeddings
    per_frame = []
    for timed in sequence.sequence:
        e = pose_embedding_fn(timed.pose)
        if e is None:
            raise ValueError("pose_embedding_fn returned None for a pose")
        per_frame.append(np.asarray(e, dtype=float))
    per_frame = np.vstack(per_frame)  # (T, D_pose)
    if verbose:
        print(f"[structured] raw per-frame embeddings shape: {per_frame.shape}")

    # 3) Optional downsample/truncate to max_length
    T, D_pose = per_frame.shape
    if max_length is not None and T > max_length and downsample == "uniform":
        per_frame = _uniform_downsample(per_frame, max_length)
        timestamps = timestamps[np.linspace(0, T - 1, num=max_length, dtype=int)]
        T = max_length
        if verbose:
            print(f"[structured] downsampled to {T} frames")

    # 4) Compute positional encodings (same dimensionality as pose embedding)
    pos_enc = _sinusoidal_time_encoding(timestamps, D_pose, time_scale=time_scale)  # (T, D_pose)

    # 5) Compose embedding per frame: pose + posenc
    composed = per_frame + pos_enc  # (T, D_pose)

    # 6) Optionally compute velocities and append
    if include_velocity:
        velocities = _compute_velocities(per_frame, timestamps)  # (T, D_pose)
        composed = np.hstack([composed, velocities])  # (T, 2*D_pose)
        if verbose:
            print(f"[structured] velocities appended; per-frame dim now {composed.shape[1]}")

    # 7) Optionally PCA reduce per-frame dim
    if pca_components is not None and pca_components > 0 and composed.shape[0] > 0:
        reduced, components, mean = _pca_reduce(composed, pca_components)
        composed = reduced  # (T, pca_components)
        if verbose:
            print(f"[structured] PCA reduced per-frame dim to {pca_components}")

    # 8) Padding if seq shorter than max_length
    if max_length is not None and T < max_length:
        pad_count = max_length - T
        pad = np.zeros((pad_count, composed.shape[1]))
        composed = np.vstack([composed, pad])
        if verbose:
            print(f"[structured] padded from {T} to {max_length} frames")

    return composed  # shape (T_out, D_out)


def flatten_temporal_embedding(
    sequence: HandPoseSequence,
    pose_embedding_fn: Callable[[object], np.ndarray],
    max_length: Optional[int] = 30,
    include_velocity: bool = True,
    time_scale: float = 1.0,
    downsample: Optional[str] = "uniform",
    pca_components: Optional[int] = None,
    verbose: bool = False
) -> np.ndarray:
    """
    Produce a flattened 1D temporal embedding by concatenating rows of structured embedding.

    Parameters mirror `structured_temporal_embedding`. Returns a 1D numpy array:
    length = (max_length or seq_len) * per_frame_dim

    WARNING: If max_length is None and sequences differ in length, returned vectors will differ in size.
    For most ML tasks, pass a fixed max_length to ensure fixed-size outputs.

    Returns
    -------
    flat : np.ndarray, shape (T_out * D_out,)
    """
    structured = structured_temporal_embedding(
        sequence=sequence,
        pose_embedding_fn=pose_embedding_fn,
        max_length=max_length,
        include_velocity=include_velocity,
        time_scale=time_scale,
        downsample=downsample,
        pca_components=pca_components,
        verbose=verbose
    )
    # Flatten row-major
    flat = structured.flatten()
    return flat
