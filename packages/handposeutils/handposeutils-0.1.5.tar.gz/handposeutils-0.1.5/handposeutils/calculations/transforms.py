# transforms.py
from __future__ import annotations
import math
from typing import Literal

def normalize_handpose_positioning(pose: "HandPose") -> "HandPose":
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
    pose = normalize_handpose_positioning(pose)
    pose = normalize_handpose_scaling(pose)
    return pose

def mirror_pose(pose: "HandPose", axis: Literal['x', 'y', 'z'] = 'x') -> "HandPose":
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
    '''
    :param pose: HandPose
    :param finger: finger to straighten
    :return: HandPose with finger straightened in the direction of
    '''
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