class Point2D:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __str__(self):
        return '[{}, {}]'.format(self.x, self.y)


class Line2D:
    def __init__(self, q: float, c: float):
        self.q = q
        self.c = c

    def __str__(self):
        return 'y = {}x + {}'.format(round(self.q, 2), round(self.c, 2))

    def __repr__(self):
        return self.__str__()


def line_through_points(a: Point2D, b: Point2D) -> Line2D:
    q = (a.y - b.y) / (a.x - b.x)
    c = a.y - q * a.x
    return Line2D(q, c)


# class Line2D:
#     """
#     General form of a 2D line: ax + by + c = 0
#     """
#     def __init__(self, a: float, b: float, c: float):
#         self.a = a
#         self.b = b
#         self.c = c
# 
#     def shift_to_point(self, point: Point2D):
#         """
#         Changes 'c' parameter so that the line crosses the given point. 'a' and 'b' parameters are not changed.
#         """
#         self.c = 0 - self.a * point.x - self.b * point.y
# 
#     def get_perpendicular_line(self, point: Optional[Point2D] = None):
#         """
#         Creates a perpendicular line to itself. If the point is given, shifts the created line in it.
#         """
#         line = Line2D(0 - self.b, self.a, 0)
#         if point is not None:
#             line.shift_to_point(point)
#         return line
# 
#     def get_intersection_with_line(self, line: 'Line2D') -> Point2D:
#         # case of horizontal 'self' line
#         if self.a == 0:
#             y = self.c
#             x = (line.b * y + line.c) / (0 - line.a)
#             return Point2D(x, y)
# 
#         q = line.a / self.a
#         y = (line.c - self.c * q) / (self.b * q - line.b)
#         x = (self.b * y + self.c) / (0 - self.a)
#         return Point2D(x, y)
# 
#     def get_closest_point_to_point(self, point: Point2D) -> Point2D:
#         perpendicular_line = self.get_perpendicular_line(point)
#         return self.get_intersection_with_line(perpendicular_line)
# 
#     def __str__(self):
#         return '{}*x + {}*y + {} = 0'.format(self.a, self.b, self.c)
# 
# 
# def create_line_from_points(u: Point2D, v: Point2D) -> Line2D:
#     dx = v.x - u.x
# 
#     # case of vertical line
#     if dx == 0:
#         return Line2D(1, 0, 0 - v.x)
# 
#     dy = v.y - u.y
#     q = dy / dx
#     return Line2D(q, -1, u.y - q * u.x)
# 
# 
# def get_distance(a: Point2D, b: Point2D) -> float:
#     dx = (a.x - b.x)
#     dy = (a.y - b.y)
#     return sqrt(dx * dx + dy * dy)
# 
# 
# def get_point_in_middle(a: Point2D, b: Point2D) -> Point2D:
#     return Point2D((a.x + b.x) / 2, (a.y + b.y) / 2)
# 
# 
# def is_point_between(a: Point2D, b: Point2D, c: Point2D) -> bool:
#     """
#     Checks whether the point 'c' is between points 'a' and 'b', where all the points are expected to be on one line.
#     """
#     a_to_b_dist = get_distance(a, b)
#     a_to_c_dist = get_distance(a, c)
#     b_to_c_dist = get_distance(b, c)
#     return a_to_c_dist < a_to_b_dist and b_to_c_dist < a_to_b_dist
