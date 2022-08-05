from typing import Dict

from preprocessing.robot import Robot
from utils.bad_input_file_error import BadInputFileError
from utils.geometry_3d import Point3D
from utils.str import remove_whitespaces


def _parse_file_line_to_robot(line: str) -> Robot:
    parts = remove_whitespaces(line).split(',')

    if len(parts) != 7:
        raise BadInputFileError('Expected 7 values in robot definition line, got {}'.format(len(parts)))

    return Robot(
        parts[0],
        Point3D(float(parts[1]), float(parts[2]), float(parts[3])),
        float(parts[4]),
        float(parts[5]),
        float(parts[6])
    )


def read_robot_data(filename: str) -> Dict[str, Robot]:
    """
    Reads given file with robots data and parses them into dictionary with id keys and robot values.
    Expects first line to contain single integer value "count" of robots,
    second line to describe columns (it is skipped in parsing)
    and then next "count" lines with comma separated values:

    - id - unique among robot ids (str)
    - x coordinate - in millimeters (float)
    - y coordinate - in millimeters (float)
    - z coordinate - in millimeters (float)
    - weight - in kilograms (float)
    - load capacity - in kilograms (float)
    - input power - in Watts (float)

    All whitespaces are ignored (do not use them in robot ids).
    """
    file = open(filename, "r")
    robots_count = int(file.readline())
    # skips second line
    file.readline()
    robots = list(map(lambda i: _parse_file_line_to_robot(file.readline()), range(robots_count)))
    return {robot.id: robot for robot in robots}


if __name__ == '__main__':
    filename = 'D:\\Uloziste\\Skola\\DP\\Algorithm\\_test_inputs\\robots_01.txt'
    robots = read_robot_data(filename)
    print(robots)
