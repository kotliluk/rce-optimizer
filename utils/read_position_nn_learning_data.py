from typing import List, Dict

from nn.position_nn import PositionNNLearningData
from preprocessing.robot import Robot
from preprocessing.position import Position
from utils.bad_input_file_error import BadInputFileError
from utils.geometry_3d import Point3D
from utils.str import remove_whitespaces


def _parse_file_line(line: str, robots: Dict[str, Robot]) -> PositionNNLearningData:
    parts = remove_whitespaces(line).split(',')

    if len(parts) != 6:
        raise BadInputFileError('Expected 6 values in position definition line, got {}'.format(len(parts)))

    position = Position(
        Point3D(float(parts[1]), float(parts[2]), float(parts[3])),
        float(parts[4]),
        robots[parts[5]]
    )

    return position.to_nn_params(), float(parts[0])


def read_position_nn_learning_data(filename: str, robots: Dict[str, Robot]) -> List[PositionNNLearningData]:
    """
    Reads given file with positions data and parses them into list.
    Expects first line to contain single integer value "count" of positions,
    second line to describe columns (it is skipped in parsing)
    and then next "count" lines with comma separated values:

    - p - coefficient value (floats)
    - x, y, z - coordinates in millimeters (3 floats)
    - mass - payload mass in kilograms (float)
    - robot id - id of the moving robot (string)

    All whitespaces are ignored (do not use them in robot ids).
    """
    file = open(filename, "r")
    positions_count = int(file.readline())
    # skips second line
    file.readline()

    return list(map(lambda _: _parse_file_line(file.readline(), robots), range(positions_count)))


if __name__ == '__main__':
    from utils.read_robot_data import read_robot_data

    robot_filename = 'D:\\Uloziste\\Skola\\DP\\Algorithm\\_test_inputs\\robots_01.txt'
    robots = read_robot_data(robot_filename)
    filename = 'D:\\Uloziste\\Skola\\DP\\Algorithm\\_test_inputs\\positions_01.txt'
    params = read_position_nn_learning_data(filename, robots)
    print(params)
