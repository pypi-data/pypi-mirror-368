from typing import List, Literal, Dict
from .coordinate import Coordinate
from .constants import POINTS_NAMES_LIST, FINGER_MAPPING
from handposeutils.calculations import transforms


class HandPose:
    """
    Represents a single 3D hand pose with 21 landmarks in MediaPipe format.

    Each landmark is stored along with its coordinate, side (left or right hand),
    common anatomical name, and the finger grouping it belongs to.

    Parameters
    ----------
    coordinates : list of Coordinate
        A list of exactly 21 `Coordinate` objects representing the hand's landmarks.
    side : {'left_hand', 'right_hand'}
        The handedness of the pose.
    name : str, optional
        An optional identifier for the pose.

    Raises
    ------
    ValueError
        If `coordinates` does not contain exactly 21 elements.
    """

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
        """
        Retrieve a coordinate by its landmark index.

        Parameters
        ----------
        index : int
            The landmark index (0–20).

        Returns
        -------
        Coordinate
            The coordinate object at the specified index.
        """
        return self.points[index]["coordinate"]

    def get_index_by_common_name(self, name: str) -> int:
        """
        Get the landmark index for a given common anatomical name.

        Parameters
        ----------
        name : str
            The common name of the landmark (e.g., "WRIST", "INDEX_FINGER_TIP").

        Returns
        -------
        int
            The index (0–20) of the landmark.

        Raises
        ------
        ValueError
            If no landmark with the given name is found.
        """
        for i, data in self.points.items():
            if data["common_name"] == name:
                return i
        raise ValueError(f"No point found with common name {name}")

    def get_all_coordinates(self) -> List[Coordinate]:
        """
        Get all coordinates for this hand pose.

        Returns
        -------
        list of Coordinate
            All 21 coordinates in index order.
        """
        return [self.points[i]["coordinate"] for i in range(21)]

    def get_handedness(self) -> Literal["left_hand", "right_hand"]:
        """
        Get the handedness of the pose.

        Returns
        -------
        {'left_hand', 'right_hand'}
            The handedness of this pose.
        """
        return self.side

    def __str__(self):
        """
        Return a human-readable string representation of the pose.

        Returns
        -------
        str
            String showing the handedness and number of landmarks.
        """
        return f"<HandPose {self.side}, {len(self.points)} landmarks>"

    def __getitem__(self, index_or_name: int | str) -> Coordinate:
        """
        Retrieve a coordinate by index or common name.

        Parameters
        ----------
        index_or_name : int or str
            The landmark index (0–20) or the common name of the landmark.

        Returns
        -------
        Coordinate
            The coordinate object.

        Raises
        ------
        TypeError
            If the input is neither an integer nor a string.
        ValueError
            If the string does not match any landmark common name.
        """
        if isinstance(index_or_name, int):
            return self.get_coordinate_by_index(index_or_name)
        elif isinstance(index_or_name, str):
            idx = self.get_index_by_common_name(index_or_name)
            return self.get_coordinate_by_index(idx)
        raise TypeError("Index must be int (0–20) or common_name string.")

    def normalize(self) -> "HandPose":
        """
        Normalize the pose in both position and scale.

        Returns
        -------
        HandPose
            A new normalized `HandPose` instance.
        """
        return transforms.normalize_handpose(self)

    def normalize_scaling(self) -> "HandPose":
        """
        Normalize the scale of the pose (without changing position).

        Returns
        -------
        HandPose
            A new `HandPose` instance scaled to a standard size.
        """
        return transforms.normalize_handpose_scaling(self)

    def normalize_position(self) -> "HandPose":
        """
        Normalize the position of the pose (without scaling).

        Returns
        -------
        HandPose
            A new `HandPose` instance translated to a standard position.
        """
        return transforms.normalize_handpose_positioning(self)

    def mirror(self, axis: Literal['x', 'y', 'z'] = 'x') -> "HandPose":
        """
        Mirror the pose across a specified axis.

        Parameters
        ----------
        axis : {'x', 'y', 'z'}, default='x'
            The axis to mirror across.

        Returns
        -------
        HandPose
            A new mirrored `HandPose` instance.
        """
        return transforms.mirror_pose(self, axis)

    def rotate(self, degrees: float, axis: Literal['x', 'y', 'z'] = 'z') -> "HandPose":
        """
        Rotate the pose around a specified axis.

        Parameters
        ----------
        degrees : float
            The angle of rotation in degrees.
        axis : {'x', 'y', 'z'}, default='z'
            The axis to rotate around.

        Returns
        -------
        HandPose
            A new rotated `HandPose` instance.
        """
        return transforms.rotate_pose_by_axis(self, degrees, axis)

    def straighten_finger(self, finger: str) -> "HandPose":
        """
        Straighten the specified finger in the pose.

        Parameters
        ----------
        finger : str
            The name of the finger to straighten (e.g., "INDEX", "THUMB").

        Returns
        -------
        HandPose
            A new `HandPose` instance with the specified finger straightened.
        """
        return transforms.straighten_finger(self, finger)
