import json
from typing import Dict, Any

from preprocessing.movement import SimpleMovement, LinearMovement, JointMovement
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


def simple_movement_from_partial_json(
    partial_movement_json: Dict,
    payload_weight: float,
    robot: Robot,
) -> SimpleMovement:
    movement_type = partial_movement_json['movement_type']
    if movement_type == 'linear':
        return LinearMovement(
            point3d_from_json(partial_movement_json['start']),
            point3d_from_json(partial_movement_json['end']),
            payload_weight,
            robot,
        )
    elif movement_type == 'joint':
        return JointMovement(
            point3d_from_json(partial_movement_json['start']),
            point3d_from_json(partial_movement_json['end']),
            payload_weight,
            robot,
        )
    else:
        raise BadInputFileError(
            'Partial movement type must be "linear" or "joint", not {}'.format(movement_type)
        )
