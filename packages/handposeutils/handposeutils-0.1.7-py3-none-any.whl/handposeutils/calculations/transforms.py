# transforms.py
from __future__ import annotations
import math
from typing import Literal

def normalize_handpose_positioning(pose: "HandPose") -> "HandPose":
    """
    Translates a hand pose so that its centroid is at the origin.

    Each coordinate is shifted such that the average x, y, and z positions
    across all landmarks are zero.

    Parameters
    ----------
    pose : HandPose
        The hand pose to normalize.

    Returns
    -------
    HandPose
        The translated hand pose, centered at the origin.
    """
    coords = pose.get_all_coordinates()
    center_x = sum(c.x for c in coords) / len(coords)
    center_y = sum(c.y for c in coords) / len(coords)
    center_z = sum(c.z for c in coords) / len(coords)

    for coord in coords:
        coord.x -= center_x
        coord.y -= center_y
        coord.z -= center_z
    return pose

def normalize_handpose_scaling(pose: "HandPose") -> "HandPose":
    """
    Scales a hand pose to fit within a [-1, 1] cube across all axes.

    The scaling is uniform and based on the largest axis range
    (max range of x, y, or z coordinates).

    Parameters
    ----------
    pose : HandPose
        The hand pose to scale.

    Returns
    -------
    HandPose
        The uniformly scaled hand pose, preserving proportions.

    Notes
    -----
    - If the maximum range is zero (all points are identical),
      the pose is returned unchanged.
    """
    coords = pose.get_all_coordinates()
    min_x = min(c.x for c in coords)
    max_x = max(c.x for c in coords)
    min_y = min(c.y for c in coords)
    max_y = max(c.y for c in coords)
    min_z = min(c.z for c in coords)
    max_z = max(c.z for c in coords)

    range_x = max_x - min_x
    range_y = max_y - min_y
    range_z = max_z - min_z
    max_range = max(range_x, range_y, range_z)

    if max_range == 0:
        return pose

    for coord in coords:
        coord.x = (coord.x - min_x) / max_range * 2 - 1
        coord.y = (coord.y - min_y) / max_range * 2 - 1
        coord.z = (coord.z - min_z) / max_range * 2 - 1
    return pose

def normalize_handpose(pose: "HandPose") -> "HandPose":
    """
    Normalizes a hand pose's position and scale.

    This function applies:
    1. Translation so the centroid is at the origin.
    2. Uniform scaling to fit in [-1, 1] on all axes.

    Parameters
    ----------
    pose : HandPose
        The hand pose to normalize.

    Returns
    -------
    HandPose
        The normalized hand pose.

    See Also
    --------
    normalize_handpose_positioning()
    normalize_handpose_scaling()
    """
    pose = normalize_handpose_positioning(pose)
    pose = normalize_handpose_scaling(pose)
    return pose

def mirror_pose(pose: "HandPose", axis: Literal['x', 'y', 'z'] = 'x') -> "HandPose":
    """
    Mirrors a hand pose across the specified axis.

    Parameters
    ----------
    pose : HandPose
        The hand pose to mirror.
    axis : {'x', 'y', 'z'}, default='x'
        Axis to mirror around.

    Returns
    -------
    HandPose
        The mirrored hand pose.

    Raises
    ------
    ValueError
        If the axis is not 'x', 'y', or 'z'.
    """
    coords = pose.get_all_coordinates()
    for coord in coords:
        if axis == 'x':
            coord.x = -coord.x
        elif axis == 'y':
            coord.y = -coord.y
        elif axis == 'z':
            coord.z = -coord.z
        else:
            raise ValueError("Axis must be 'x', 'y', or 'z'")
    return pose

def rotate_pose_by_axis(pose: "HandPose", degrees: float, axis: Literal['x', 'y', 'z']) -> "HandPose":
    """
    Rotates a hand pose by a given angle around a specified axis.

    Parameters
    ----------
    pose : HandPose
        The hand pose to rotate.
    degrees : float
        Rotation angle in degrees.
    axis : {'x', 'y', 'z'}
        Axis around which to rotate.

    Returns
    -------
    HandPose
        The rotated hand pose.

    Raises
    ------
    ValueError
        If the axis is not 'x', 'y', or 'z'.
    """
    radians = math.radians(degrees)
    cos_a = math.cos(radians)
    sin_a = math.sin(radians)
    coords = pose.get_all_coordinates()

    for c in coords:
        x, y, z = c.x, c.y, c.z
        if axis == 'x':
            c.y = y * cos_a - z * sin_a
            c.z = y * sin_a + z * cos_a
        elif axis == 'y':
            c.x = x * cos_a + z * sin_a
            c.z = -x * sin_a + z * cos_a
        elif axis == 'z':
            c.x = x * cos_a - y * sin_a
            c.y = x * sin_a + y * cos_a
        else:
            raise ValueError("Axis must be 'x', 'y', or 'z'")
    return pose

def straighten_finger(pose, finger: str) -> "HandPose":
    """
    Straightens a specified finger so that its joints align in a straight line.

    The finger's base and first joint define the direction, and each joint
    is repositioned proportionally along this direction, preserving
    original segment lengths.

    Parameters
    ----------
    pose : HandPose
        The hand pose containing the finger to straighten.
    finger : str
        Finger name to straighten. Must match a key in
        `handposeutils.data.constants.FINGER_MAPPING`.

    Returns
    -------
    HandPose
        The modified hand pose with the finger straightened.

    Raises
    ------
    ValueError
        If the finger name is invalid or has fewer than two joints.
    """
    from handposeutils.data.constants import FINGER_MAPPING
    indices = FINGER_MAPPING.get(finger.upper())
    if not indices or len(indices) < 2:
        raise ValueError(f"Invalid or too-short finger: {finger}")

    # Base and first joint determine direction
    base = pose.get_coordinate_by_index(indices[0])
    next_joint = pose.get_coordinate_by_index(indices[1])
    direction = (next_joint - base).normalize()

    # Step 1: Compute distances between each consecutive point
    segment_lengths = []
    total_length = 0.0
    for i in range(1, len(indices)):
        prev_coord = pose.get_coordinate_by_index(indices[i - 1])
        curr_coord = pose.get_coordinate_by_index(indices[i])
        dist = (curr_coord - prev_coord).magnitude()
        segment_lengths.append(dist)
        total_length += dist

    # Step 2: Compute cumulative percentage position of each joint
    cumulative = 0.0
    new_positions = [base]
    for length in segment_lengths:
        cumulative += length
        ratio = cumulative / total_length
        new_coord = base + direction.scale(total_length * ratio)
        new_positions.append(new_coord)

    # Step 3: Update coordinates
    for i in range(len(indices)):
        pose.points[indices[i]]["coordinate"] = new_positions[i]

    return pose