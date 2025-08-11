# List of Mediapipe point names in order --- this naming convention is "common_name" for HandPoses
POINTS_NAMES_LIST = [
    "WRIST", "THUMB_CMC", "THUMB_MCP", "THUMB_IP", "THUMB_TIP",
    "INDEX_FINGER_MCP", "INDEX_FINGER_PIP", "INDEX_FINGER_DIP", "INDEX_FINGER_TIP",
    "MIDDLE_FINGER_MCP", "MIDDLE_FINGER_PIP", "MIDDLE_FINGER_DIP", "MIDDLE_FINGER_TIP",
    "RING_FINGER_MCP", "RING_FINGER_PIP", "RING_FINGER_DIP", "RING_FINGER_TIP",
    "PINKY_MCP", "PINKY_PIP", "PINKY_DIP", "PINKY_TIP"
]

FINGER_MAPPING = {
    "THUMB": range(1, 5),
    "INDEX": range(5, 9),
    "MIDDLE": range(9, 13),
    "RING": range(13, 17),
    "PINKY": range(17, 21)
}