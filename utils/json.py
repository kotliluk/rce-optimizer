import json
from typing import Dict, Any

from preprocessing.movement import SimpleMovement, LinearMovement, JointMovement, Movement, CompoundMovement
from preprocessing.position import Position
from preprocessing.robot import Robot
from utils.bad_input_file_error import BadInputFileError
from utils.geometry_3d import Point3D


def read_json_from_file(filename: str) -> Any:
    with open(filename) as file:
        data = json.load(file)
        return data


def save_to_json_file(filename: str, data: Any):
    with open(filename, "w") as file:
        json.dump(data, file)


def point3d_from_json(point_json: Dict) -> Point3D:
    return Point3D(point_json['x'], point_json['y'], point_json['z'])


def robot_from_json(robot_json: Dict) -> Robot:
    return Robot(
        robot_json['id'],
        point3d_from_json(robot_json['position']),
        robot_json['weight'],
        robot_json['load_capacity'],
        robot_json['input_power'],
    )


def simple_movement_from_partial_json(
    partial_movement_json: Dict,
    payload_weight: float,
    robot: Robot,
) -> SimpleMovement:
    movement_type = partial_movement_json['movement_type']
    start = partial_movement_json['start']
    end = partial_movement_json['end']

    if movement_type == 'linear':
        return LinearMovement(start, end, payload_weight, robot)
    elif movement_type == 'joint':
        return JointMovement(start, end, payload_weight, robot)
    else:
        raise BadInputFileError(
            'Partial movement type must be "linear" or "joint", not {}'.format(movement_type)
        )


def linear_movement_from_json(json_dict: Dict, robots: Dict[str, Robot]) -> Movement:
    return LinearMovement(
        point3d_from_json(json_dict['start']),
        point3d_from_json(json_dict['end']),
        json_dict['mass'],
        robots[json_dict['robot_id']]
    )


def joint_movement_from_json(json_dict: Dict, robots: Dict[str, Robot]) -> Movement:
    return JointMovement(
        point3d_from_json(json_dict['start']),
        point3d_from_json(json_dict['end']),
        json_dict['mass'],
        robots[json_dict['robot_id']]
    )


def compound_movement_from_json(json_dict: Dict, robots: Dict[str, Robot]) -> Movement:
    mass = json_dict['mass']
    robot = robots[json_dict['robot_id']]
    part_movements = [
        simple_movement_from_partial_json(partial_json, mass, robot)
        for partial_json in json_dict['parts']
    ]

    return CompoundMovement(part_movements, mass, robot)


def movement_from_json(json_dict: Dict, robots: Dict[str, Robot]) -> Movement:
    if json_dict['movement_type'] == 'linear':
        return linear_movement_from_json(json_dict, robots)
    elif json_dict['movement_type'] == 'joint':
        return joint_movement_from_json(json_dict, robots)
    elif json_dict['movement_type'] == 'compound':
        return compound_movement_from_json(json_dict, robots)
    else:
        raise BadInputFileError(
            'Movement type must be "linear", "joint", or "compound", not "{}"'.format(json_dict['movement_type'])
        )


def position_from_json(json_dict: Dict, robots: Dict[str, Robot]) -> Position:
    return Position(
        point3d_from_json(json_dict['coordinates']),
        json_dict['mass'],
        robots[json_dict['robot_id']],
    )
