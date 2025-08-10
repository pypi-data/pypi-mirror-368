from typing import List, Optional, Callable
from dataclasses import dataclass
from .handpose import HandPose
import threading
import time

@dataclass
class TimedHandPose:
    pose: HandPose
    start_time: float  # seconds
    end_time: float    # seconds


class HandPoseSequence:
    def __init__(self, timed_poses: List[TimedHandPose] = None):
        self.sequence = sorted(timed_poses, key=lambda x: x.start_time) if timed_poses else []
        self._recording_thread = None
        self._recording = False
        self._record_start_time = None

    def get_pose_at_time(self, timestamp: float) -> Optional[HandPose]:
        """
        Returns the pose active at a given timestamp.
        """
        for timed_pose in self.sequence:
            if timed_pose.start_time <= timestamp < timed_pose.end_time:
                return timed_pose.pose
        return None

    def get_all_timestamps(self) -> List[float]:
        """
        Returns the list of start_times for all poses.
        """
        return [tp.start_time for tp in self.sequence]

    def get_pose_by_index(self, index: int) -> HandPose:
        """
        :param index: index to get
        :return:
        """
        return self.sequence[index].pose

    @property
    def current_pose(self) -> Optional[HandPose]:
        """
        Returns the current pose based on the latest available timestamp.
        Defaults to the last one if no time-tracking is active.
        """
        if self.sequence:
            return self.sequence[-1].pose
        return None

    def __getitem__(self, index: int) -> TimedHandPose:
        return self.sequence[index]

    def __len__(self):
        return len(self.sequence)

    def __str__(self):
        return f"<HandPoseSequence with {len(self.sequence)} poses>"


    def start_recording(self, get_pose_fn: Callable[[], Optional[HandPose]], fps: int = 30):
        if self._recording:
            print("[!] Already recording.")
            return

        self._recording = True
        self._record_start_time = time.time()
        interval = 1.0 / fps

        def _record_loop():
            print(f"[⏺️] Started recording at {fps} FPS.")
            while self._recording:
                start = time.time()
                current_time = start - self._record_start_time
                pose = get_pose_fn()
                if pose:
                    self._append_pose(pose, current_time)
                elapsed = time.time() - start
                time.sleep(max(0, interval - elapsed))
            print("[⏹️] Stopped recording.")

        self._recording_thread = threading.Thread(target=_record_loop, daemon=True)
        self._recording_thread.start()

    def stop_recording(self):
        self._recording = False
        if self._recording_thread:
            self._recording_thread.join()
        self._fix_end_times()

    def _append_pose(self, pose: HandPose, start_time: float):
        # Guess end_time as +1 frame unless overwritten later
        frame_duration = 1.0 / 30.0  # could make dynamic later
        self.sequence.append(TimedHandPose(pose, start_time, start_time + frame_duration))

    def _fix_end_times(self):
        for i in range(len(self.sequence) - 1):
            self.sequence[i].end_time = self.sequence[i + 1].start_time
        if self.sequence:
            self.sequence[-1].end_time = self.sequence[-1].start_time + 1.0 / 30.0  # fallback for last