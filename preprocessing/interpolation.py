import numpy as np
from typing import List, Tuple

from utils.geometry_2d import Point2D


InterpolationCoefs = Tuple[float, float, float, float]
"""
Tuple with coefficients for ax^{-2} + bx^{-1} + c + dx interpolating function.
"""


def interpolate(points: List[Point2D]) -> InterpolationCoefs:
    """
    Interpolates given points with function ax^{-2} + bx^{-1} + c + dx and returns its coefficients.
    """
    x = np.array(list(map(lambda point: point.x, points)))
    y = np.array(list(map(lambda point: point.y, points)))
    A = np.vstack([x**-2, x**-1, np.ones(len(x)), x]).T
    y = y[:, np.newaxis]
    coefs = np.dot((np.dot(np.linalg.inv(np.dot(A.T, A)), A.T)), y)
    return coefs[0][0], coefs[1][0], coefs[2][0], coefs[3][0]


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    points = [
        Point2D(7.476, 32068),
        Point2D(9, 26673),
        Point2D(12.108, 22682),
        Point2D(20.169, 22030),
        Point2D(61.956, 40581)
    ]
    x = np.array(list(map(lambda point: point.x, points)))
    y = np.array(list(map(lambda point: point.y, points)))
    coefs = interpolate(points)

    x_line = np.arange(6, 65, 0.1)
    plt.scatter(x, y, label='data')
    plt.plot(
        x_line,
        coefs[0] * x_line ** -2 + coefs[1] * x_line ** -1 + coefs[2] + coefs[3] * x_line,
        label=r"$a x^{-2} + b x^{-1} + c + d x$",
        linestyle='--'
    )
    plt.legend()
    plt.show()
