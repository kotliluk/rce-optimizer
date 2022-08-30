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
