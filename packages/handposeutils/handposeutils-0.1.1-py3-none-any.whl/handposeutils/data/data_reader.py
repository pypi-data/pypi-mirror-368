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
        SCALE = 100  # scale 0–1 coordinates to 0–100 units
        coords = [Coordinate(lm.x * SCALE, (1-lm.y) * SCALE, lm.z * SCALE) for lm in mp_landmarks.landmark]

        match str(handedness):
            case "left":
                return HandPose(coords, "left_hand")
            case "right":
                return HandPose(coords, "right_hand")
        return HandPose(coords, None)


    @staticmethod
    def convert_HandPose_to_mediapipe(pose: HandPose):
        from mediapipe.framework.formats import landmark_pb2
        landmarks = [
            landmark_pb2.NormalizedLandmark(x=c.x, y=c.y, z=c.z)
            for c in pose.get_all_coordinates()
        ]
        return landmark_pb2.NormalizedLandmarkList(landmark=landmarks)

    # --- OpenPose Conversion ---

    @staticmethod
    def convert_openpose_to_HandPose(openpose_data: List[float], side=None) -> HandPose:
        # OpenPose flat format: [x0, y0, c0, x1, y1, c1, ...]
        coords = []
        for i in range(21):
            x = openpose_data[i * 3]
            y = openpose_data[i * 3 + 1]
            z = 0.0  # OpenPose does not provide depth
            coords.append(Coordinate(x, y, z))
        return HandPose(coords, side)

    @staticmethod
    def convert_HandPose_to_openpose(pose: HandPose) -> List[float]:
        openpose_format = []
        for coord in pose.get_all_coordinates():
            openpose_format.extend([coord.x, coord.y, 1.0])  # default confidence -> 1.0
        return openpose_format

    # --- CSV Conversion ---

    @staticmethod
    def convert_csv_to_HandPose(df: pd.DataFrame, side="right_hand") -> HandPose:
        coords = [Coordinate(row['x'], row['y'], row['z']) for _, row in df.iterrows()]
        return HandPose(coords, side)

    @staticmethod
    def export_HandPose_to_csv(pose: HandPose) -> pd.DataFrame:
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
        side = json_data.get("side", "right_hand")
        try:
            landmarks = json_data["landmarks"]
        except:
            landmarks = json_data["pose"]["landmarks"]

        coords = [Coordinate(pt["x"], pt["y"], pt["z"]) for pt in landmarks]
        return HandPose(coords, side)

    @staticmethod
    def export_HandPose_to_json(pose: HandPose) -> Dict:
        '''
        {
          "side": "right_hand",
          "landmarks": [
            { "x": 0.1, "y": 0.2, "z": 0.0, "name": "WRIST", "finger": "PALM" },
            { "x": 0.15, "y": 0.22, "z": 0.0, "name": "THUMB_CMC", "finger": "THUMB" },
            ...
          ]
        }
        '''
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
        '''
        :param json_data:
        :return:
        '''

        '''
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

        '''
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
        Converts a HandPoseSequence to a JSON-serializable list of timed poses.
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
                              handpose_prefix_name: str):
        """
        Save each frame of a HandPoseSequence to a separate JSON file.

        Args:
            sequence (HandPoseSequence): The sequence to save.
            folder_name (str): Path to the folder where JSON files will be stored.
            file_prefix (str): Prefix for each saved file (e.g., 'frame' -> frame_1.json).
            handpose_prefix_name (str): Prefix for the HandPose.name in each saved file.
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

        print(f"[✅] Saved {len(sequence)} frames to '{folder_name}'")