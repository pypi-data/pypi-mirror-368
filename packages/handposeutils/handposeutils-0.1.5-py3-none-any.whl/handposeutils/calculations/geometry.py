import numpy as np


def vector_between(c1, c2):
    """
    Returns a NumPy vector from Coordinate c1 to c2.

    :param c1: Coordinate object.
    :param c2: Coordinate object.
    :return: A NumPy array representing the vector from c1 to c2.
    """
    return np.array([c2.x - c1.x, c2.y - c1.y, c2.z - c1.z])


def get_finger_length(finger_name: str, pose) -> float:
    """
    Computes the total length of a finger by summing Euclidean distances between joints.

    :param finger_name: Name of the finger ('thumb', 'index', etc.).
    :return: float — total 3D length of the finger in the given pose.
    """
    finger_name = finger_name.upper()
    from handposeutils.data.constants import FINGER_MAPPING
    indices = FINGER_MAPPING[finger_name]
    coords = [pose[i] for i in indices]

    # Sum distances between adjacent joints along the finger
    length = 0.0
    for i in range(len(coords) - 1):
        v = vector_between(coords[i], coords[i+1])
        length += np.linalg.norm(v)
    return length

def get_finger_segment_lengths(finger_name: str, pose) -> list[float]:
    """
    Computes the individual segment lengths of a finger (proximal, intermediate, distal).

    :param finger_name: Name of the finger.
    :return: List of three floats representing segment lengths.
    """
    finger_name = finger_name.upper()
    from handposeutils.data.constants import FINGER_MAPPING
    indices = FINGER_MAPPING[finger_name]
    coords = [pose[i] for i in indices]

    # Return lengths between successive joints (3 segments per finger)
    return [np.linalg.norm(vector_between(coords[i], coords[i+1])) for i in range(3)]

def get_finger_curvature(finger_name: str, pose) -> float:
    """
    Estimates the average angular curvature of a finger.

    :param finger_name: Name of the finger.
    :return: Float — average angle (in radians) between finger segments. Lower is straighter.
    """
    finger_name = finger_name.upper()
    from handposeutils.data.constants import FINGER_MAPPING
    indices = FINGER_MAPPING[finger_name]
    a, b, c, d = [pose[i] for i in indices]

    # Get vectors between adjacent joints
    v1 = vector_between(a, b)
    v2 = vector_between(b, c)
    v3 = vector_between(c, d)

    def angle_between(v1, v2):
        # Classic cosine angle formula
        dot = np.dot(v1, v2)
        norms = np.linalg.norm(v1) * np.linalg.norm(v2)
        cos_theta = np.clip(dot / (norms + 1e-6), -1.0, 1.0)
        return np.arccos(cos_theta)

    # Average the two segment angles
    return (angle_between(v1, v2) + angle_between(v2, v3)) / 2.0

def get_total_hand_span(pose) -> float:
    """
    Measures total hand span between thumb tip and pinky tip.

    :return: Float distance between landmarks 4 and 20.
    """
    thumb_tip = pose[4]
    pinky_tip = pose[20]

    # Simple Euclidean distance
    return np.linalg.norm(vector_between(thumb_tip, pinky_tip))

def get_finger_spread(pose) -> dict[str, float]:
    """
    Measures the angular spread between adjacent fingers at their MCP joints.

    :return: Dict mapping each finger pair (e.g., "INDEX-MIDDLE") to angle in radians.
    """
    base_indices = [5, 9, 13, 17]  # MCPs for index → pinky
    names = ["INDEX", "MIDDLE", "RING", "PINKY"]
    spread = {}

    for i in range(len(base_indices) - 1):
        a = pose[base_indices[i]]
        b = pose[0]  # Wrist
        c = pose[base_indices[i + 1]]

        # Vectors from wrist to adjacent MCPs
        v1 = vector_between(b, a)
        v2 = vector_between(b, c)

        # Angle between MCP direction vectors
        dot = np.dot(v1, v2)
        norms = np.linalg.norm(v1) * np.linalg.norm(v2)
        angle = np.arccos(np.clip(dot / (norms + 1e-6), -1.0, 1.0))

        spread[f"{names[i]}-{names[i+1]}"] = angle
    return spread

def get_hand_aspect_ratio(pose) -> float:
    """
    Calculates the aspect ratio (width/height) of the hand in XY plane.

    :return: Float representing width divided by height.
    """
    coords = np.array([c.as_tuple() for c in pose.get_all_coordinates()])
    min_x, max_x = coords[:, 0].min(), coords[:, 0].max()
    min_y, max_y = coords[:, 1].min(), coords[:, 1].max()

    width = max_x - min_x
    height = max_y - min_y
    return width / (height + 1e-6)

def get_pose_flatness(pose, axis='z') -> float:
    """
    Measures flatness of the pose as standard deviation along one axis.

    :param axis: Axis to compute flatness along ('x', 'y', or 'z').
    :return: Float — std deviation along axis; lower = flatter.
    """
    coords = np.array([c.as_tuple() for c in pose.get_all_coordinates()])
    axis_map = {'x': 0, 'y': 1, 'z': 2}
    return np.std(coords[:, axis_map[axis]])

def get_joint_angle(triplet: tuple[int, int, int], pose) -> float:
    """
    Computes the simple internal angle at the middle joint of a 3-point chain.

    :param triplet: Tuple of 3 landmark indices (a, b, c) where b is the joint.
    :return: Angle at point b in radians.
    """
    a, b, c = (pose[i] for i in triplet)
    v1 = vector_between(b, a)
    v2 = vector_between(b, c)

    dot = np.dot(v1, v2)
    norms = np.linalg.norm(v1) * np.linalg.norm(v2)
    return np.arccos(np.clip(dot / (norms + 1e-6), -1.0, 1.0))

def get_palm_normal_vector(pose) -> np.ndarray:
    """
    Returns the palm normal vector using three base landmarks.

    :return: A normalized NumPy 3D vector (wrist–index_mcp × wrist–pinky_mcp).
    """
    a = np.array(pose[0].as_tuple())   # Wrist
    b = np.array(pose[5].as_tuple())   # Index MCP
    c = np.array(pose[17].as_tuple())  # Pinky MCP

    # Cross product of two vectors from wrist to edges of palm
    v1 = b - a
    v2 = c - a
    normal = np.cross(v1, v2)
    return normal / (np.linalg.norm(normal) + 1e-6)

def get_cross_finger_angles(pose) -> dict[str, float]:
    """
    Measures the angle between direction vectors of adjacent fingers.

    :return: Dict of angles (radians) between finger direction vectors.
    """
    from handposeutils.data.constants import FINGER_MAPPING
    finger_names = ["THUMB", "INDEX", "MIDDLE", "RING", "PINKY"]
    vectors = {}

    # Compute normalized vector from base to tip for each finger
    for name in finger_names:
        indices = FINGER_MAPPING[name]
        base, tip = pose[indices[0]], pose[indices[-1]]
        vec = vector_between(base, tip)
        vectors[name] = vec / (np.linalg.norm(vec) + 1e-6)

    angles = {}
    for i in range(len(finger_names) - 1):
        f1, f2 = finger_names[i], finger_names[i+1]
        angle = np.arccos(np.clip(np.dot(vectors[f1], vectors[f2]), -1.0, 1.0))
        angles[f"{f1}-{f2}"] = angle
    return angles
