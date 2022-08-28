from typing import List, Dict, Tuple

from nn.movement_energy_nn import MovementEnergyNNTrainingData
from preprocessing.movement import LinearMovement, JointMovement, CompoundMovement
from preprocessing.robot import Robot
from utils.bad_input_file_error import BadInputFileError
from utils.json import read_json_from_file, robot_from_json, point3d_from_json, simple_movement_from_partial_json


def _parse_linear_movement(json: Dict, robots: Dict[str, Robot]) -> MovementEnergyNNTrainingData:
    movement = LinearMovement(
        point3d_from_json(json['start']),
        point3d_from_json(json['end']),
        json['mass'],
        robots[json['robot_id']]
    )

    return movement, tuple(json['energy_4_coefs'])


def _parse_joint_movement(json: Dict, robots: Dict[str, Robot]) -> MovementEnergyNNTrainingData:
    movement = JointMovement(
        point3d_from_json(json['start']),
        point3d_from_json(json['end']),
        json['mass'],
        robots[json['robot_id']]
    )

    return movement, tuple(json['energy_4_coefs'])


def _parse_compound_movement(json: Dict, robots: Dict[str, Robot]) -> MovementEnergyNNTrainingData:
    mass = json['mass']
    robot = robots[json['robot_id']]
    part_movements = [
        simple_movement_from_partial_json(partial_json, mass, robot)
        for partial_json in json['parts']
    ]

    return CompoundMovement(part_movements, mass, robot), tuple(json['energy_4_coefs'])


def _movement_energy_nn_training_data_from_json(json: Dict, robots: Dict[str, Robot]) -> MovementEnergyNNTrainingData:
    if json['movement_type'] == 'linear':
        return _parse_linear_movement(json, robots)
    elif json['movement_type'] == 'joint':
        return _parse_joint_movement(json, robots)
    elif json['movement_type'] == 'compound':
        return _parse_compound_movement(json, robots)
    else:
        raise BadInputFileError(
            'Movement type must be "linear", "joint", or "compound", not "{}"'.format(json['movement_type'])
        )


def read_movements_for_nn_training(filename: str) -> Tuple[List[MovementEnergyNNTrainingData], Dict[str, Robot]]:
    """
    Reads given file with movements JSON data and parses them into list and dict of used robots.
    """
    data = read_json_from_file(filename)
    robots = {
        robot_json['id']: robot_from_json(robot_json)
        for robot_json in data['robots']
    }
    movements = [
        _movement_energy_nn_training_data_from_json(movement_json, robots)
        for movement_json in data['movements']
    ]
    return movements, robots
