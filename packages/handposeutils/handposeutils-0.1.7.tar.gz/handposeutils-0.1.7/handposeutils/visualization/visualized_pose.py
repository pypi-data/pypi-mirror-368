from handposeutils.data.handpose import HandPose
from typing import Optional, Tuple


class VisualizedPose(HandPose):
    """
    Extended HandPose with enhanced visualization properties:
    visibility, opacity, annotation, finger highlighting, and color scheme.

    Attributes
    ----------
    visible : bool
        Whether the pose is visible.
    opacity : float
        Transparency level (0.0 = invisible, 1.0 = opaque).
    annotation : Optional[str]
        Label annotation (e.g., gesture type).
    highlighted_finger : Optional[str]
        Finger name currently highlighted.
    highlight_color : Tuple[float, float, float]
        RGB color for highlighted finger.
    color_scheme : dict
        RGB colors for landmarks, finger joints, and palm.
    """
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
        """
        Set RGB color scheme for pose visualization components.

        Parameters
        ----------
        landmarks : tuple, optional
            RGB for landmarks.
        fingers : list of tuple, optional
            RGB for proximal, intermediate, distal finger joints (length 3).
        joints : tuple, optional
            RGB for joints (overrides landmarks).
        palm : tuple, optional
            RGB for palm.
        """
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
        """
        Get current RGB color scheme.

        Returns
        -------
        dict
            Mapping of component names to RGB tuples.
        """

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
        """Get current annotation label."""
        return self.annotation

    def highlight(self, finger: str, color: Tuple[float, float, float] = (1, 1, 1)):
        """Highlights a specific finger with a custom color"""
        self.highlighted_finger = finger.lower()
        self.highlight_color = color

    def getHighlightedFinger(self) -> Optional[str]:
        """Get currently highlighted finger."""
        return self.highlighted_finger

    def getHighlightColor(self) -> Tuple[float, float, float]:
        """Get RGB color of highlighted finger."""
        return self.highlight_color

    def hidePose(self):
        """Make the pose invisible."""
        self.visible = False

    def showPose(self):
        """Make the pose visible."""
        self.visible = True

    def isVisible(self) -> bool:
        """Check if pose is visible."""
        return self.visible

    def __str__(self):
        """String representation showing side, visibility, and annotation.

        Returns
        -------
        str
            <VisualizedPose ({self.side}, {visibility status (Visible or Hidden)}){self.annotation if exists}>"
        """
        status = "Visible" if self.visible else "Hidden"
        label = f" [{self.annotation}]" if self.annotation else ""
        return f"<VisualizedPose ({self.side}, {status}){label}>"
