from typing import List, Dict

from nn.movement_energy_nn import MovementEnergyNNLearningData, MovementEnergyNNOutput
from preprocessing.movement import LinearMovement, JointMovement, CompoundMovement, SimpleMovement
from preprocessing.robot import Robot
from utils.bad_input_file_error import BadInputFileError
from utils.geometry_3d import Point3D
from utils.str import remove_whitespaces


def _parse_learning_output(parts: List[str]) -> MovementEnergyNNOutput:
    return float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])


def _parse_linear_movement(parts: List[str], robots: Dict[str, Robot]) -> MovementEnergyNNLearningData:
    """
    Expected line: 'linear', a, b, c, d, mass, robot id, start x, start y, start z, end x, end y, end z
    """

    if len(parts) != 13:
        raise BadInputFileError('Expected 13 values in linear movement definition line, got {}'.format(len(parts)))

    movement = LinearMovement(
        Point3D(float(parts[7]), float(parts[8]), float(parts[9])),
        Point3D(float(parts[10]), float(parts[11]), float(parts[12])),
        float(parts[5]),
        robots[parts[6]]
    )

    return movement.to_nn_params(), _parse_learning_output(parts)


def _parse_joint_movement(parts: List[str], robots: Dict[str, Robot]) -> MovementEnergyNNLearningData:
    """
    Expected line: 'joint', a, b, c, d, mass, robot id, start x, start y, start z, end x, end y, end z
    """

    if len(parts) != 13:
        raise BadInputFileError('Expected 13 values in linear movement definition line, got {}'.format(len(parts)))

    movement = JointMovement(
        Point3D(float(parts[7]), float(parts[8]), float(parts[9])),
        Point3D(float(parts[10]), float(parts[11]), float(parts[12])),
        float(parts[5]),
        robots[parts[6]]
    )

    return movement.to_nn_params(), _parse_learning_output(parts)


def _parse_compound_movement(parts: List[str], robots: Dict[str, Robot]) -> MovementEnergyNNLearningData:
    """
    Expected line: 'compound', a, b, c, d, mass, robot id [, start x, start y, start z, end x, end y, end z, type]
    """

    if len(parts) % 7 != 0 or len(parts) < 14:
        raise BadInputFileError(
            'Expected (7*k + 7) values (k >= 1) in compound movement definition line, got {}'.format(len(parts))
        )

    mass = float(parts[5])
    robot = robots[parts[6]]

    def parse_part_movement(i: int) -> SimpleMovement:
        start = Point3D(float(parts[7 + 7 * i + 0]), float(parts[7 + 7 * i + 1]), float(parts[7 + 7 * i + 2]))
        end = Point3D(float(parts[7 + 7 * i + 3]), float(parts[7 + 7 * i + 4]), float(parts[7 + 7 * i + 5]))
        part_type = parts[7 + 7 * i + 6]
        if part_type == 'linear':
            return LinearMovement(start, end, mass, robot)
        elif part_type == 'joint':
            return JointMovement(start, end, mass, robot)
        else:
            raise BadInputFileError(
                'Compound movement part type must be "linear" or "joint", not "{}"'.format(part_type)
            )

    part_movements_count = (len(parts) - 7) // 7
    part_movements = list(map(parse_part_movement, range(part_movements_count)))

    movement = CompoundMovement(part_movements, mass, robot)

    return movement.to_nn_params(), _parse_learning_output(parts)


def _parse_file_line(line: str, robots: Dict[str, Robot]) -> MovementEnergyNNLearningData:
    parts = remove_whitespaces(line).split(',')

    if parts[0] == 'linear':
        return _parse_linear_movement(parts, robots)
    elif parts[0] == 'joint':
        return _parse_joint_movement(parts, robots)
    elif parts[0] == 'compound':
        return _parse_compound_movement(parts, robots)
    else:
        raise BadInputFileError('Movement type must be "linear", "joint", or "compound", not "{}"'.format(parts[0]))


def read_movement_nn_learning_data(filename: str, robots: Dict[str, Robot]) -> List[MovementEnergyNNLearningData]:
    """
    Reads given file with movements data and parses them into list.
    Expects first line to contain single integer value "count" of movements,
    second line to describe columns (it is skipped in parsing)
    and then next "count" lines with comma separated values:

    - type - type of the movement, e.g. "linear", "joint", or "compound"
    - a, b, c, d - coefficients values (4 floats)
    - mass - payload mass in kilograms (float)
    - robot id - id of the moving robot (string)

    If the "type" is "linear" or "joint", the line should continue with:
    - start x, start y, start z - start coordinates in millimeters (3 floats)
    - end x, end y, end z - end coordinates in millimeters (3 floats)

    If the "type" is "compound", the line should continue with at least one repetition of partial movement description:
    - start x, start y, start z - start coordinates of partial movement in millimeters (3 floats)
    - end x, end y, end z - end coordinates of partial movement in millimeters (3 floats)
    - partial type - type of the partial movement, e.g. "linear" or "joint"

    All whitespaces are ignored (do not use them in robot ids).
    """
    file = open(filename, "r")
    movements_count = int(file.readline())
    # skips second line
    file.readline()

    return list(map(lambda i: _parse_file_line(file.readline(), robots), range(movements_count)))


if __name__ == '__main__':
    from utils.read_robot_data import read_robot_data

    robot_filename = 'D:\\Uloziste\\Skola\\DP\\Algorithm\\_test_inputs\\robots_01.txt'
    robots = read_robot_data(robot_filename)
    filename = 'D:\\Uloziste\\Skola\\DP\\Algorithm\\_test_inputs\\movements_01.txt'
    params = read_movement_nn_learning_data(filename, robots)
    print(params)
