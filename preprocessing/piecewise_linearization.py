import numpy as np
from scipy import optimize
from typing import List

from preprocessing.interpolation import InterpolationCoefs
from utils.geometry_2d import Point2D, Line2D
import utils.geometry_2d as g2d


def _find_linear_piece_corners(X: np.ndarray, Y: np.ndarray, count: int):
    """
    Finds (count + 1) corner points of piecewise linear approximation.
    Implementation shared in StackOverflow answer: https://stackoverflow.com/a/70712007/9874768

    :param X: numpy array of x points (x-axis enumeration)
    :param Y: numpy array of y values of the linearized function (values in x points)
    :param count: number of linear pieces
    :return: two lists of x and y coordinates of found corner points
    """
    min_x = X[0]
    max_x = X[-1]
    seg = np.full(count - 1, (max_x - min_x) / count)

    px_init = np.r_[np.r_[min_x, seg].cumsum(), max_x]
    py_init = np.array([Y[np.abs(X - x) < (max_x - min_x) * 0.01].mean() for x in px_init])

    def func(p):
        seg = p[:count - 1]
        py = p[count - 1:]
        px = np.r_[np.r_[min_x, seg].cumsum(), max_x]
        return px, py

    def err(p):
        px, py = func(p)
        Y2 = np.interp(X, px, py)
        return np.mean((Y - Y2)**2)

    r = optimize.minimize(err, x0=np.r_[seg, py_init], method='Nelder-Mead')
    print(r.fun)
    return func(r.x)


def piecewise_linearize(coefs: InterpolationCoefs, min_x: float, max_x: float, count: int = 4) -> List[Line2D]:
    """
    Computes linear approximation of the given interpolating function with "count" pieces.

    :param coefs: interpolating function described by its coefficients
    :param min_x: minimal x coordinate in interpolated input data point
    :param max_x: maximal x coordinate in interpolated input data point
    :param count: number of pieces in linear approximation
    :return:
    """
    floored_min_x = np.floor(min_x)
    if floored_min_x == 0:
        floored_min_x = 0.1

    xs = np.arange(floored_min_x, np.ceil(max_x), 0.1)
    ys = coefs[0] * xs ** -2 + coefs[1] * xs ** -1 + coefs[2] + coefs[3] * xs

    # VERSION WITH LAST PIECE IGNORED
    # fx, fy = find_linear_piece_corners(xs, ys, count + 1)
    # points = list(map(lambda i: Point2D(fx[i], fy[i]), range(count + 2)))
    # pieces = list(map(lambda i: g2d.line_through_points(points[i], points[i + 1]), range(count - 1)))
    # pieces.append(g2d.line_through_points(points[-3], points[-1]))

    fx, fy = _find_linear_piece_corners(xs, ys, count)
    points = list(map(lambda i: Point2D(fx[i], fy[i]), range(count + 1)))
    pieces = list(map(lambda i: g2d.line_through_points(points[i], points[i + 1]), range(count)))

    return pieces


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from preprocessing.interpolation import interpolate

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
    lines = piecewise_linearize(coefs, 7.476, 61.956, 4)

    # approximation error for different piece numbers
    # 1 - 6779060
    # 2 - 461554
    # 3 - 92826
    # 4 - 49215 -
    # 5 - 24563 -
    # 6 - 19226

    xs = np.arange(np.floor(7.476), np.ceil(61.956), 0.1)
    ys = coefs[0] * xs ** -2 + coefs[1] * xs ** -1 + coefs[2] + coefs[3] * xs
    plt.scatter(x, y, label='data')
    plt.plot(xs, ys, label=r"$a x^{-2} + b x^{-1} + c + d x$", linestyle='-')
    for i, line in enumerate(lines):
        lines_ys = line.q * xs + line.c
        plt.plot(xs, lines_ys, linestyle='dotted')
    plt.ylim([20000, 42000])
    plt.legend()
    plt.show()
