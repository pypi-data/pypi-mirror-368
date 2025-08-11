from dataclasses import dataclass
import math

@dataclass
class Coordinate:
    x: float
    y: float
    z: float

    def __sub__(self, other: "Coordinate") -> "Coordinate":
        return Coordinate(self.x - other.x, self.y - other.y, self.z - other.z)

    def __add__(self, other: "Coordinate") -> "Coordinate":
        return Coordinate(self.x + other.x, self.y + other.y, self.z + other.z)

    def scale(self, scalar: float) -> "Coordinate":
        return Coordinate(self.x * scalar, self.y * scalar, self.z * scalar)

    def magnitude(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def normalize(self) -> "Coordinate":
        # technically a vector, but oopsie
        mag = self.magnitude()
        if mag == 0:
            return Coordinate(0, 0, 0)
        return Coordinate(self.x / mag, self.y / mag, self.z / mag)

    def as_tuple(self) -> tuple:
        return (self.x, self.y, self.z)

    def __repr__(self) -> str:
        return f"Coordinate(x={self.x:.3f}, y={self.y:.3f}, z={self.z:.3f})"
