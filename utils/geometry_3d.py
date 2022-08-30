from numpy import sqrt, arccos


class Point3D:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return '[{}, {}, {}]'.format(self.x, self.y, self.z)

    def __add__(self, other: 'Point3D') -> 'Point3D':
        return Point3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: 'Point3D') -> 'Point3D':
        return Point3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other: float) -> 'Point3D':
        return Point3D(self.x * other, self.y * other, self.z * other)

    def __truediv__(self, other: float) -> 'Point3D':
        return Point3D(self.x / other, self.y / other, self.z / other)

    def is_zero(self) -> bool:
        return self.x == 0 and self.y == 0 and self.z == 0

    def magnitude(self) -> float:
        return sqrt(self.x * self.x + self.y * self.y + self.z * self.z)


def distance(a: Point3D, b: Point3D) -> float:
    """
    Computes euclidean distance between given points.
    """
    dx = (a.x - b.x)
    dy = (a.y - b.y)
    dz = (a.z - b.z)
    return sqrt(dx * dx + dy * dy + dz * dz)


def angle(u: Point3D, v: Point3D) -> float:
    """
    Computes angle between two non-zero vectors.
    """
    cos_angle = (u.x * v.x + u.y * v.y + u.z * v.z) / (u.magnitude() * v.magnitude())
    return arccos(cos_angle)


def null_z(a: Point3D) -> Point3D:
    """
    Creates a new point with the same 'x' and 'y' coordinates but 0 'z'.
    """
    return Point3D(a.x, a.y, 0)
