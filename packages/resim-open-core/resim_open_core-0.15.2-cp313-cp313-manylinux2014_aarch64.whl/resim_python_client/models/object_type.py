from enum import Enum

class ObjectType(str, Enum):
    TYPE_DCURVE_SE3 = "TYPE_DCURVE_SE3"
    TYPE_FRAME = "TYPE_FRAME"
    TYPE_FRAMED_VECTOR = "TYPE_FRAMED_VECTOR"
    TYPE_SE3 = "TYPE_SE3"
    TYPE_SO3 = "TYPE_SO3"
    TYPE_TCURVE_SE3 = "TYPE_TCURVE_SE3"
    TYPE_TRAJECTORY = "TYPE_TRAJECTORY"

    def __str__(self) -> str:
        return str(self.value)
