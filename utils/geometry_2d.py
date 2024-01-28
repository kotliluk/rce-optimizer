from typing import Optional

from numpy import sqrt


class Point2D:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __str__(self):
        return '[{}, {}]'.format(self.x, self.y)

    def magnitude(self) -> float:
        """
        Computes magnitude sqrt(x**2 + y**2) of the point.
        """
        return sqrt(self.x * self.x + self.y * self.y)


class Line2D:
    def __init__(self, q: float, c: float):
        self.q = q
        self.c = c

    def __str__(self):
        return 'y = {}x + {}'.format(round(self.q, 5), round(self.c, 5))

    def __repr__(self):
        return self.__str__()

    def distance_to_point(self, point: Point2D) -> float:
        """
        Computes euclidean distance of the line to the given point.
        """
        a = self.q
        b = -1
        c = self.c
        return abs(a * point.x + b * point.y + c) / sqrt(a * a + b * b)

    def perpendicular_in_point(self, point: Point2D):
        """
        Computes perpendicular line to the line in the given point.
        """
        # parameters of original line (a*x + b*y + k = 0)
        a = self.q
        b = -1
        # parameters of perpendicular line (pa*x + pb*y + pk = 0)
        pa = -b
        pb = a
        pk = -(pa * point.x + pb * point.y)
        # parameters of perpendicular line (y = pq*x + pc)
        pq = -(pa / pb)
        pc = -(pk / pb)
        return Line2D(pq, pc)

    def intersection_with_line(self, line) -> Optional[Point2D]:
        """
        Computes intersection point of the line and the given line.
        Returns None if lines are parallel.
        """
        if self.q == line.q:
            return None

        x = (line.c - self.c) / (self.q - line.q)
        y = self.q * x + self.c
        return Point2D(x, y)

    def closest_point(self, point: Point2D) -> Point2D:
        """
        Computes closest point to the given point on the line (i.e. project the point on the line).
        """
        if self.q == 0.0:
            return Point2D(point.x, self.c)

        perpendicular = self.perpendicular_in_point(point)
        return self.intersection_with_line(perpendicular)


def distance(a: Point2D, b: Point2D) -> float:
    """
    Computes euclidean distance between given points.
    """
    dx = (a.x - b.x)
    dy = (a.y - b.y)
    return sqrt(dx * dx + dy * dy)


def line_through_points(a: Point2D, b: Point2D) -> Line2D:
    """
    Creates a line through given points.
    """
    q = (a.y - b.y) / (a.x - b.x)
    c = a.y - q * a.x
    return Line2D(q, c)


if __name__ == '__main__':
    line = Line2D(1, 0)
    point = Point2D(2, 0)
    dist = line.distance_to_point(point)
    per = line.perpendicular_in_point(point)
    inter = line.intersection_with_line(per)
    inter2 = line.closest_point(point)
    print(dist)
    print(per)
    print(inter)
    print(inter2)
