import numpy as np


def vector_between(c1, c2):
    """
    Returns a NumPy vector from Coordinate c1 to c2.

    Parameters
    ----------
    c1 : Coordinate
         First point (x,y,z)
    c2 : Coordinate
         Second point (x,y,z)

    Returns
    -------
    np.array
        A NumPy array representing the vector from c1 to c2.
    """
    return np.array([c2.x - c1.x, c2.y - c1.y, c2.z - c1.z])



def get_finger_length(finger_name: str, pose) -> float:
    """
    Calculate the total 3D length of a finger.

    Highkey, this information is pretty arbitrary, since unless you normalize scaling, absolute distances aren't
    particularly useful, compared to relative distances.
    TODO: write a relative bone length function. That would be more useful.

    The length is computed by summing the Euclidean distances between
    each pair of adjacent joints for the given finger.

    Parameters
    ----------
    finger_name : str
        Name of the finger (case-insensitive). Must be a key in
        `handposeutils.data.constants.FINGER_MAPPING`
        (e.g., "thumb", "index", "middle", "ring", "pinky").
    pose : Pose
        Hand pose object or sequence supporting index-based access to `Coordinate` objects.

    Returns
    -------
    float
        Total finger length in the same units as the pose coordinates.
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
    Get the individual segment lengths of a finger.

    Returns the lengths of the proximal, intermediate, and distal segments
    by computing Euclidean distances between successive joints.

    Parameters
    ----------
    finger_name : str
        Name of the finger (case-insensitive). Must be a key in
        `handposeutils.data.constants.FINGER_MAPPING`.
    pose : Pose
        Hand pose object or sequence supporting index-based access to `Coordinate` objects.

    Returns
    -------
    list of float
        Three lengths (same units as coordinates), ordered from base to tip.

    See Also
    --------
    get_finger_length
        gets the summed length of the full finger
    """
    finger_name = finger_name.upper()
    from handposeutils.data.constants import FINGER_MAPPING
    indices = FINGER_MAPPING[finger_name]
    coords = [pose[i] for i in indices]

    # Return lengths between successive joints (3 segments per finger)
    return [np.linalg.norm(vector_between(coords[i], coords[i+1])) for i in range(3)]

def get_finger_curvature(finger_name: str, pose) -> float:
    """
    Estimate the average angular curvature of a finger.

    Curvature is measured as the mean angle (in radians) between consecutive
    segment vectors. Lower values indicate a straighter finger.

    Parameters
    ----------
    finger_name : str
        Name of the finger (case-insensitive).
    pose : Pose
        Hand pose object or sequence supporting index-based access to `Coordinate` objects.

    Returns
    -------
    float
        Average curvature angle in radians.
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
    Compute the Euclidean distance between thumb tip and pinky tip.

    Parameters
    ----------
    pose : Pose
        Hand pose object or sequence supporting index-based access to `Coordinate` objects.

    Returns
    -------
    float
        Distance between landmarks 4 (thumb tip) and 20 (pinky tip).
    """
    thumb_tip = pose[4]
    pinky_tip = pose[20]

    # Simple Euclidean distance
    return np.linalg.norm(vector_between(thumb_tip, pinky_tip))

def get_finger_spread(pose) -> dict[str, float]:
    """
    Measure the angular spread between adjacent fingers at their MCP joints.

    Parameters
    ----------
    pose : Pose
        Hand pose object or sequence supporting index-based access to `Coordinate` objects.

    Returns
    -------
    dict of str to float
        Mapping from finger pair names (e.g., "INDEX-MIDDLE") to spread angle in radians.
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
    Calculate the aspect ratio (width / height) of the hand in the XY plane.

    Parameters
    ----------
    pose : Pose
        Hand pose object

    Returns
    -------
    float
        Ratio of hand width to height in the XY plane.
    """
    coords = np.array([c.as_tuple() for c in pose.get_all_coordinates()])
    min_x, max_x = coords[:, 0].min(), coords[:, 0].max()
    min_y, max_y = coords[:, 1].min(), coords[:, 1].max()

    width = max_x - min_x
    height = max_y - min_y
    return width / (height + 1e-6)

def get_pose_flatness(pose, axis='z') -> float:
    """
    Measure the flatness of the hand pose along a given axis.

    Flatness is defined as the standard deviation of all coordinates
    along the specified axis.

    Parameters
    ----------
    pose : Pose
        Hand pose object with `get_all_coordinates()` method.
    axis : {'x', 'y', 'z'}, optional
        Axis along which to compute flatness. Default is 'z'.

    Returns
    -------
    float
        Standard deviation along the specified axis. Lower values mean flatter pose.
    """
    coords = np.array([c.as_tuple() for c in pose.get_all_coordinates()])
    axis_map = {'x': 0, 'y': 1, 'z': 2}
    return np.std(coords[:, axis_map[axis]])

def get_joint_angle(triplet: tuple[int, int, int], pose) -> float:
    """
    Compute the internal angle at the middle joint of a 3-point chain.

    Parameters
    ----------
    triplet : tuple of int
        Landmark indices (a, b, c) where `b` is the vertex joint.
    pose : Pose
        Hand pose object or sequence supporting index-based access to `Coordinate` objects.

    Returns
    -------
    float
        Angle at point `b` in radians.
    """
    a, b, c = (pose[i] for i in triplet)
    v1 = vector_between(b, a)
    v2 = vector_between(b, c)

    dot = np.dot(v1, v2)
    norms = np.linalg.norm(v1) * np.linalg.norm(v2)
    return np.arccos(np.clip(dot / (norms + 1e-6), -1.0, 1.0))

def get_palm_normal_vector(pose) -> np.ndarray:
    """
    Compute the palm normal vector using three base landmarks.

    Uses the cross product of the wrist-to-index_mcp and wrist-to-pinky_mcp
    vectors to obtain the palm's outward normal.

    Parameters
    ----------
    pose : Pose
        Hand pose object or sequence supporting index-based access to `Coordinate` objects.

    Returns
    -------
    numpy.ndarray
        Normalized 3D vector representing the palm normal.
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
    Measure the angle between direction vectors of adjacent fingers.

    Parameters
    ----------
    pose : Pose
        Hand pose object or sequence supporting index-based access to `Coordinate` objects.

    Returns
    -------
    dict of str to float
        Mapping from adjacent finger name pairs (e.g., "THUMB-INDEX") to
        angle in radians.
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
