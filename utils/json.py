import json
from typing import Dict, Any

from preprocessing.movement import PTPMovement, Movement
from preprocessing.robot import Robot
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
        robot_json['maximum_reach'],
    )


def joint_movement_from_json(json_dict: Dict, robot: Robot) -> Movement:
    return PTPMovement(
        point3d_from_json(json_dict['start']),
        point3d_from_json(json_dict['end']),
        robot,
        json_dict['payload_weight'],
    )
