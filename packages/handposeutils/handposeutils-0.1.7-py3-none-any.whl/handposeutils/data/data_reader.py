import pandas as pd
from typing import List, Dict, Any
from .handpose import HandPose
from .handpose_sequence import HandPoseSequence, TimedHandPose
from .coordinate import Coordinate
from .constants import POINTS_NAMES_LIST, FINGER_MAPPING
import os, json
## The DataReader class for
# I highkey don't think you'll ever need to convert from OpenPose to HandPoses,
# but I somehow found myself in a situation where I did.
# Thus, I implemented the OpenPose conversions.
# However, json conversions are considered standard format for transfer and storage.
# Functions are selfexplanatory.

class DataReader:
    # --- MediaPipe Conversion ---
    @staticmethod
    def convert_mediapipe_to_HandPose(mp_landmarks, handedness: str = None) -> HandPose:
        """
        Convert MediaPipe landmarks to a HandPose object.

        MediaPipe landmarks are normalized 3D coordinates with x, y in [0,1]
        and z roughly in [-0.5, 0.5]. This function scales x and y by 100,
        inverts y axis, and scales z by 100.

        Parameters
        ----------
        mp_landmarks : mediapipe.framework.formats.landmark_pb2.NormalizedLandmarkList
            MediaPipe landmarks object containing 21 hand landmarks.
        handedness : str, optional
            'left' or 'right' to indicate hand side (default None).

        Returns
        -------
        HandPose
            The converted hand pose with scaled coordinates.

        Notes
        -----
        The coordinate system is transformed so y is flipped vertically.
        """
        SCALE = 100  # scale 0–1 coordinates to 0–100 units to make them visible
        coords = [Coordinate(lm.x * SCALE, (1-lm.y) * SCALE, lm.z * SCALE) for lm in mp_landmarks.landmark]

        match str(handedness):
            case "left":
                return HandPose(coords, "left_hand")
            case "right":
                return HandPose(coords, "right_hand")
        return HandPose(coords, None)


    @staticmethod
    def convert_HandPose_to_mediapipe(pose: HandPose):
        """
        Convert a HandPose object to MediaPipe NormalizedLandmarkList format.

        Coordinates are converted directly without scaling (expected normalized).

        Parameters
        ----------
        pose : HandPose
            Hand pose to convert.

        Returns
        -------
        mediapipe.framework.formats.landmark_pb2.NormalizedLandmarkList
            MediaPipe landmarks list matching the pose's coordinates.
        """
        from mediapipe.framework.formats import landmark_pb2
        landmarks = [
            landmark_pb2.NormalizedLandmark(x=c.x, y=c.y, z=c.z)
            for c in pose.get_all_coordinates()
        ]
        return landmark_pb2.NormalizedLandmarkList(landmark=landmarks)

    # --- OpenPose Conversion ---

    @staticmethod
    def convert_openpose_to_HandPose(openpose_data: List[float], side=None) -> HandPose:
        """
        Convert OpenPose flat hand keypoint data to a HandPose object.

        OpenPose format is a flat list of floats:
        [x0, y0, c0, x1, y1, c1, ..., x20, y20, c20]
        where xi, yi are 2D coordinates and ci is confidence (ignored).
        Depth (z) is set to 0.0 by default.

        Parameters
        ----------
        openpose_data : List[float]
            Flat list with 63 elements (21 points × 3 values).
        side : str, optional
            Hand side label ('left_hand' or 'right_hand'), default None.

        Returns
        -------
        HandPose
            Hand pose with 21 landmarks converted from OpenPose data.
        """
        coords = []
        for i in range(21):
            x = openpose_data[i * 3]
            y = openpose_data[i * 3 + 1]
            z = 0.0  # OpenPose does not provide depth... learned that the hard way smh
            coords.append(Coordinate(x, y, z))
        return HandPose(coords, side)

    @staticmethod
    def convert_HandPose_to_openpose(pose: HandPose) -> List[float]:
        """
        Convert a HandPose object to OpenPose flat keypoint format.

        Output format is a list:
        [x0, y0, c0, x1, y1, c1, ..., x20, y20, c20]
        with confidence c_i set to 1.0 by default.

        Parameters
        ----------
        pose : HandPose
            Hand pose to convert.

        Returns
        -------
        List[float]
            Flat list representing OpenPose keypoints.
        """
        openpose_format = []
        for coord in pose.get_all_coordinates():
            openpose_format.extend([coord.x, coord.y, 1.0])  # default confidence -> 1.0
        return openpose_format

    # --- CSV Conversion ---

    @staticmethod
    def convert_csv_to_HandPose(df: pd.DataFrame, side="right_hand") -> HandPose:
        """
        Convert a CSV DataFrame of hand landmark coordinates to a HandPose object.

        Expected CSV format: DataFrame with columns 'x', 'y', and 'z',
        with one row per landmark in order.

        Parameters
        ----------
        df : pandas.DataFrame
            DataFrame containing columns ['x', 'y', 'z'] for 21 hand landmarks.
        side : str, optional
            Hand side label, default is 'right_hand'.

        Returns
        -------
        HandPose
            Converted hand pose with coordinates from the DataFrame.
        """
        coords = [Coordinate(row['x'], row['y'], row['z']) for _, row in df.iterrows()]
        return HandPose(coords, side)

    @staticmethod
    def export_HandPose_to_csv(pose: HandPose) -> pd.DataFrame:
        """
        Export a HandPose object to a CSV-format pandas DataFrame.

        Output DataFrame columns:
        'name' (landmark name), 'x', 'y', 'z' (coordinates).

        Parameters
        ----------
        pose : HandPose
            Hand pose to export.

        Returns
        -------
        pandas.DataFrame
            DataFrame with one row per landmark and columns ['name', 'x', 'y', 'z'].
        """
        data = []
        for i in range(21):
            coord = pose[i]
            data.append({
                "name": POINTS_NAMES_LIST[i],
                "x": coord.x,
                "y": coord.y,
                "z": coord.z
            })
        return pd.DataFrame(data)

    # --- JSON Conversion ---

    @staticmethod
    def convert_json_to_HandPose(json_data: Dict[str, Any]) -> HandPose:
        """
        Convert JSON-formatted hand landmarks to a HandPose object.

        Parameters
        ----------
        json_data : dict
            JSON dictionary representing a hand pose, expected format:
            {
                "side": "right_hand",            # optional, default to 'right_hand'
                "landmarks": [
                    {"x": float, "y": float, "z": float},  # 21 landmarks
                    ...
                ]
            }
            Some formats may nest landmarks under a "pose" key:
            {
                "pose": {
                    "landmarks": [...]
                },
                "side": "left_hand"
            }

        Returns
        -------
        HandPose
            HandPose instance with landmarks converted from JSON.
        """
        side = json_data.get("side", "right_hand")
        try:
            landmarks = json_data["landmarks"]
        except:
            landmarks = json_data["pose"]["landmarks"]

        coords = [Coordinate(pt["x"], pt["y"], pt["z"]) for pt in landmarks]
        return HandPose(coords, side)

    @staticmethod
    def export_HandPose_to_json(pose: HandPose) -> Dict:
        """
        Export a HandPose object to a JSON-serializable dictionary.

        Output format:
        {
          "side": "right_hand",
          "name": "pose_name",                   # optional pose identifier
          "landmarks": [
            {"x": float, "y": float, "z": float,
             "name": str, "finger": str},        # 21 landmarks with metadata
            ...
          ]
        }

        Example
        -------
        {
          "side": "right_hand",
          "landmarks": [
            { "x": 0.1, "y": 0.2, "z": 0.0, "name": "WRIST", "finger": "PALM" },
            { "x": 0.15, "y": 0.22, "z": 0.0, "name": "THUMB_CMC", "finger": "THUMB" },
            ...
          ]
        }

        Parameters
        ----------
        pose : HandPose
            HandPose to convert.

        Returns
        -------
        dict
            JSON-compatible dictionary describing the hand pose.
        """
        data = {
            "side": pose.side,
            "name": pose.name,  # new field
            "landmarks": []
        }
        for i in range(21):
            coord = pose[i]
            data["landmarks"].append({
                "x": coord.x,
                "y": coord.y,
                "z": coord.z,
                "name": POINTS_NAMES_LIST[i],
                "finger": pose.points[i]["finger"]
            })
        return data

    @staticmethod
    def convert_json_to_HandPoseSequence(json_data: Dict[str, Any]) -> HandPoseSequence:
        """
        Convert a JSON dictionary representing a timed hand pose sequence
        into a HandPoseSequence object.

        Expected JSON format:
        {
          "sequence": [
            {
              "start_time": float,
              "end_time": float,
              "pose": { ... }  # HandPose JSON format, see export_HandPose_to_json
            },
            ...
          ]
        }

        Example
        -------
        {
          "sequence": [
            {
              "start_time": 0.0,
              "end_time": 0.033,
              "pose": { ... }  // HandPose JSON -- reference convert_HandPose_to_json
            },
            {
              "start_time": 0.033,
              "end_time": 0.066,
              "pose": { ... }
            }
          ]
        }

        Parameters
        ----------
        json_data : dict
            JSON dictionary representing a sequence of timed hand poses.

        Returns
        -------
        HandPoseSequence
            Sequence object containing timed hand poses.

        See Also
        --------
        convert_json_to_HandPose
            runs on each pose found in the HandPoseSequence
        HandPose
        HandPoseSequence
        """
        sequence = []
        for item in json_data["sequence"]:
            try:
                pose = DataReader.convert_json_to_HandPose(item["pose"])
            except:
                pose = DataReader.convert_json_to_HandPose(item)
            sequence.append(TimedHandPose(
                pose=pose,
                start_time=item["start_time"],
                end_time=item["end_time"]
            ))
        return HandPoseSequence(sequence)

    @staticmethod
    def convert_HandPoseSequence_to_json(sequence: HandPoseSequence, fps: int = 30) -> Dict:
        """
        Convert a HandPoseSequence into a JSON-serializable dictionary
        containing timed hand poses.

        Output format:
        {
          "fps": int,          # frames per second
          "sequence": [
            {
              "start_time": float,
              "end_time": float,
              "pose": { ... }  # HandPose JSON format
            },
            ...
          ]
        }

        Parameters
        ----------
        sequence : HandPoseSequence
            Sequence of timed hand poses.
        fps : int, optional
            Frames per second metadata (default is 30).

        Returns
        -------
        dict
            JSON-compatible dictionary representing the sequence.
        """
        return {
            "fps": fps,
            "sequence": [
                {
                    "start_time": round(tp.start_time, 4),
                    "end_time": round(tp.end_time, 4),
                    "pose": DataReader.export_HandPose_to_json(tp.pose)
                }
                for tp in sequence
            ]
        }

    @staticmethod
    def save_frames_to_folder(sequence: HandPoseSequence, folder_name: str, file_prefix: str,
                              handpose_prefix_name: str, verbose: bool = True):
        """
        Save each frame of a HandPoseSequence as an individual JSON file.

        Files are saved as: {folder_name}/{file_prefix}_{frame_index}.json

        Each file contains:
        {
          "start_time": float,
          "end_time": float,
          "pose": { ... }  # HandPose JSON
        }

        Parameters
        ----------
        sequence : HandPoseSequence
            The sequence of timed hand poses to save.
        folder_name : str
            Path to the directory to save JSON files (created if missing).
        file_prefix : str
            Prefix for filenames, e.g., 'frame' produces files like 'frame_1.json'.
        handpose_prefix_name : str
            Prefix to assign to HandPose.name for each saved frame.
        verbose : bool, optional
            Whether to print progress messages (default True).

        Returns
        -------
        None
        """
        # Create folder if it doesn't exist
        os.makedirs(folder_name, exist_ok=True)

        for idx, timed_pose in enumerate(sequence.sequence, start=1):
            # Give the pose a name
            timed_pose.pose.name = f"{handpose_prefix_name}_{idx}"

            # Convert to JSON
            pose_json = DataReader.export_HandPose_to_json(timed_pose.pose)

            # Include timing info so the saved data is fully reconstructable
            frame_data = {
                "start_time": timed_pose.start_time,
                "end_time": timed_pose.end_time,
                "pose": pose_json
            }

            # Save to file
            file_path = os.path.join(folder_name, f"{file_prefix}_{idx}.json")
            with open(file_path, 'w') as f:
                json.dump(frame_data, f, indent=2)

        if verbose:
            print(f"[DataReader] Saved {len(sequence)} frames to '{folder_name}'")