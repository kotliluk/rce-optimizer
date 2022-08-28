from typing import List, Dict, Tuple

from nn.position_nn import PositionNNTrainingData
from preprocessing.position import Position
from preprocessing.robot import Robot
from utils.json import read_json_from_file, robot_from_json, point3d_from_json


def _position_nn_training_data_from_json(json: Dict, robots: Dict[str, Robot]) -> PositionNNTrainingData:
    position = Position(
        point3d_from_json(json['coordinates']),
        json['mass'],
        robots[json['robot_id']]
    )

    return position.to_nn_params(), json['p_coef']


def read_positions_for_nn_training(filename: str) -> Tuple[List[PositionNNTrainingData], Dict[str, Robot]]:
    """
    Reads given JSON file with positions data and parses them into list and dict of used robots.
    """
    data = read_json_from_file(filename)
    robots = {
        robot_json['id']: robot_from_json(robot_json)
        for robot_json in data['robots']
    }
    positions = [
        _position_nn_training_data_from_json(position_json, robots)
        for position_json in data['positions']
    ]
    return positions, robots
