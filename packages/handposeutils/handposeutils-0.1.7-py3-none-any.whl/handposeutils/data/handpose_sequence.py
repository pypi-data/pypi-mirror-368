from typing import List, Optional, Callable
from dataclasses import dataclass
from .handpose import HandPose
import threading
import time

@dataclass
class TimedHandPose:
    """
    A hand pose with associated start and end timestamps.

    Attributes
    ----------
    pose : HandPose
        The hand pose captured during this time window.
    start_time : float
        The starting time of this pose in seconds.
    end_time : float
        The ending time of this pose in seconds.
    """
    pose: HandPose
    start_time: float  # seconds
    end_time: float    # seconds


class HandPoseSequence:
    """
    A sequence of hand poses with their timing information.

    This class allows you to store, retrieve, and record hand poses over time,
    enabling playback, analysis, and live capture from a pose source.

    Parameters
    ----------
    timed_poses : list of TimedHandPose, optional
        Initial list of timed hand poses. If provided, they are sorted
        by `start_time`.

    Attributes
    ----------
    sequence : list of TimedHandPose
        The ordered list of timed poses.
    _recording_thread : threading.Thread or None
        The background thread for live recording.
    _recording : bool
        Whether a recording session is currently active.
    _record_start_time : float or None
        The wall-clock time when recording started.

    See Also
    ----------
    HandPose
        HandPoseSequence is effectively a storage system for multiple HandPoses, indexed by time.
    """

    def __init__(self, timed_poses: List[TimedHandPose] = None):
        self.sequence = sorted(timed_poses, key=lambda x: x.start_time) if timed_poses else []
        self._recording_thread = None
        self._recording = False
        self._record_start_time = None

    def get_pose_at_time(self, timestamp: float) -> Optional[HandPose]:
        """
        Get the hand pose active at a given timestamp.

        Parameters
        ----------
        timestamp : float
            The time in seconds for which to retrieve the pose.

        Returns
        -------
        HandPose or None
            The hand pose active at the specified time, or None if no
            pose was active.
        """
        for timed_pose in self.sequence:
            if timed_pose.start_time <= timestamp < timed_pose.end_time:
                return timed_pose.pose
        return None

    def get_all_timestamps(self) -> List[float]:
        """
        Get the start times of all poses in the sequence.

        Returns
        -------
        list of float
            List of all pose start times in seconds.
        """
        return [tp.start_time for tp in self.sequence]

    def get_pose_by_index(self, index: int) -> HandPose:
        """
        Get a pose by its index in the sequence.

        Parameters
        ----------
        index : int
            Index of the pose in the sequence.

        Returns
        -------
        HandPose
            The pose at the given index.

        Raises
        ------
        IndexError
            If the index is out of range.
        """
        return self.sequence[index].pose

    @property
    def current_pose(self) -> Optional[HandPose]:
        """
        Get the most recent pose in the sequence.

        If no time-tracking is active, this defaults to the last pose
        in the sequence.

        Returns
        -------
        HandPose or None
            The latest recorded pose, or None if the sequence is empty.
        """
        if self.sequence:
            return self.sequence[-1].pose
        return None

    def __getitem__(self, index: int) -> TimedHandPose:
        """
        Get a timed pose by its index.

        Parameters
        ----------
        index : int
            Index of the timed pose.

        Returns
        -------
        TimedHandPose
            The timed pose at the given index.
        """
        return self.sequence[index]

    def __len__(self) -> int:
        """
        Get the number of poses in the sequence.

        Returns
        -------
        int
            Number of timed poses.
        """
        return len(self.sequence)

    def __str__(self) -> str:
        """
        Outputs <HandPoseSequence with {number of poses} poses>

        Returns
        -------
        str
            Human-readable description of the sequence.
        """
        return f"<HandPoseSequence with {len(self.sequence)} poses>"

    def start_recording(self, get_pose_fn: Callable[[], Optional[HandPose]], fps: int = 30):
        """
        Start recording poses from a callable source at a fixed frame rate.

        Parameters
        ----------
        get_pose_fn : callable
            A function returning a `HandPose` or None when no pose is available.
        fps : int, default=30
            Frames per second to capture.

        Notes
        -----
        Recording is performed in a background thread and continues until
        `stop_recording` is called.
        """
        if self._recording:
            print("[!] Already recording.")
            return

        self._recording = True
        self._record_start_time = time.time()
        interval = 1.0 / fps

        def _record_loop():
            print(f"[HandPoseSequence] Started recording at {fps} FPS.")
            while self._recording:
                start = time.time()
                current_time = start - self._record_start_time
                pose = get_pose_fn()
                if pose:
                    self._append_pose(pose, current_time)
                elapsed = time.time() - start
                time.sleep(max(0, interval - elapsed))
            print("[HandPoseSequence] Stopped recording.")

        self._recording_thread = threading.Thread(target=_record_loop, daemon=True)
        self._recording_thread.start()

    def stop_recording(self):
        """
        Stop an active recording session.

        Notes
        -----
        This waits for the recording thread to finish and fixes the end
        times for recorded poses.
        """
        self._recording = False
        if self._recording_thread:
            self._recording_thread.join()
        self._fix_end_times()

    def _append_pose(self, pose: HandPose, start_time: float):
        """
        Append a new pose to the sequence with an estimated end time.

        Parameters
        ----------
        pose : HandPose
            The pose to append.
        start_time : float
            The start time of the pose in seconds.
        """
        frame_duration = 1.0 / 30.0  # could make dynamic later
        self.sequence.append(TimedHandPose(pose, start_time, start_time + frame_duration))

    def _fix_end_times(self):
        """
        Adjust end times of all recorded poses to match the start time of
        the next pose.

        Notes
        -----
        For the last pose, the end time is estimated as `start_time + 1/30s`.
        """
        for i in range(len(self.sequence) - 1):
            self.sequence[i].end_time = self.sequence[i + 1].start_time
        if self.sequence:
            self.sequence[-1].end_time = self.sequence[-1].start_time + 1.0 / 30.0
