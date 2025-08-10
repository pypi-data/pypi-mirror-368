from handposeutils.data.handpose import HandPose
from typing import Optional, Tuple


class VisualizedPose(HandPose):
    def __init__(self, coordinates, side: str = "right_hand"):
        super().__init__(coordinates, side)

        self.visible = True
        self.opacity = 1.0
        self.annotation = None
        self.highlighted_finger = None
        self.highlight_color = (1.0, 1.0, 1.0)  # default white

        self.color_scheme = {
            "landmarks": (1.0, 0.0, 0.0),
            "proximals": (0.5, 0.0, 1.0),
            "intermediates": (0.0, 1.0, 0.5),
            "distals": (0.0, 0.5, 1.0),
            "palm": (1.0, 1.0, 0.0),
        }

    def setColorScheme(
        self,
        landmarks: Optional[Tuple[float, float, float]] = None,
        fingers: Optional[list[Tuple[float, float, float]]] = None,
        joints: Optional[Tuple[float, float, float]] = None,
        palm: Optional[Tuple[float, float, float]] = None
    ):
        if landmarks is not None:
            self.color_scheme["landmarks"] = landmarks
        if fingers is not None and len(fingers) == 3:
            self.color_scheme["proximals"] = fingers[0]
            self.color_scheme["intermediates"] = fingers[1]
            self.color_scheme["distals"] = fingers[2]
        if joints is not None:
            self.color_scheme["landmarks"] = joints
        if palm is not None:
            self.color_scheme["palm"] = palm

    def getColorScheme(self) -> dict:
        return self.color_scheme

    def setOpacity(self, alpha: float):
        """Sets transparency level from 0.0 (invisible) to 1.0 (opaque)"""
        self.opacity = max(0.0, min(1.0, alpha))

    def getOpacity(self) -> float:
        return self.opacity

    def annotate(self, label: str):
        """Stores an annotation label (e.g., for gesture type or user ID)"""
        self.annotation = label

    def getAnnotation(self) -> Optional[str]:
        return self.annotation

    def highlight(self, finger: str, color: Tuple[float, float, float] = (1, 1, 1)):
        """Highlights a specific finger with a custom color"""
        self.highlighted_finger = finger.lower()
        self.highlight_color = color

    def getHighlightedFinger(self) -> Optional[str]:
        return self.highlighted_finger

    def getHighlightColor(self) -> Tuple[float, float, float]:
        return self.highlight_color

    def hidePose(self):
        self.visible = False

    def showPose(self):
        self.visible = True

    def isVisible(self) -> bool:
        return self.visible

    def __str__(self):
        status = "Visible" if self.visible else "Hidden"
        label = f" [{self.annotation}]" if self.annotation else ""
        return f"<VisualizedPose ({self.side}, {status}){label}>"
