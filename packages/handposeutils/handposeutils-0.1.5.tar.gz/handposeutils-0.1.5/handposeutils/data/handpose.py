from typing import List, Literal, Dict
from .coordinate import Coordinate
from .constants import POINTS_NAMES_LIST, FINGER_MAPPING
from handposeutils.calculations import transforms


class HandPose:
    def __init__(self, coordinates: List[Coordinate], side: Literal["left_hand", "right_hand"], name: str = None):
        if len(coordinates) != 21:
            raise ValueError("Expected 21 coordinates for hand landmarks (MediaPipe format).")

        self.side = side
        self.name = name  # Optional identifier for the pose
        self.points: Dict[int, Dict] = {}

        for i, coord in enumerate(coordinates):
            finger = next((fname for fname, idxs in FINGER_MAPPING.items() if i in idxs), "PALM")
            self.points[i] = {
                "coordinate": coord,
                "side": side,
                "common_name": POINTS_NAMES_LIST[i],
                "finger": finger
            }

    def get_coordinate_by_index(self, index: int) -> Coordinate:
        return self.points[index]["coordinate"]

    def get_index_by_common_name(self, name: str) -> int:
        for i, data in self.points.items():
            if data["common_name"] == name:
                return i
        raise ValueError(f"No point found with common name {name}")

    def get_all_coordinates(self) -> List[Coordinate]:
        return [self.points[i]["coordinate"] for i in range(21)]

    def get_handedness(self) -> Literal["left_hand", "right_hand"]:
        return self.side

    def __str__(self):
        return f"<HandPose {self.side}, {len(self.points)} landmarks>"

    def __getitem__(self, index_or_name: int | str) -> Coordinate:
        if isinstance(index_or_name, int):
            return self.get_coordinate_by_index(index_or_name)
        elif isinstance(index_or_name, str):
            idx = self.get_index_by_common_name(index_or_name)
            return self.get_coordinate_by_index(idx)
        raise TypeError("Index must be int (0–20) or common_name string.")

    def normalize(self) -> "HandPose":
        return transforms.normalize_handpose(self)

    def normalize_scaling(self) -> "HandPose":
        return transforms.normalize_handpose_scaling(self)

    def normalize_position(self) -> "HandPose":
        return transforms.normalize_handpose_positioning(self)

    def mirror(self, axis: Literal['x', 'y', 'z'] = 'x') -> "HandPose":
        return transforms.mirror_pose(self, axis)

    def rotate(self, degrees: float, axis: Literal['x', 'y', 'z'] = 'z') -> "HandPose":
        return transforms.rotate_pose_by_axis(self, degrees, axis)

    def straighten_finger(self, finger: str) -> "HandPose":
        return transforms.straighten_finger(self, finger)
