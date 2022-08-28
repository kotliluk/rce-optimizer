from os import listdir
from typing import List, Tuple

from nn.train_common import read_nn_data_from_file
from utils.json import read_json_from_file, robot_from_json, movement_from_json

BASE_PART = 'D:/Uloziste/Skola/DP/Algorithm/rce-optimizer/_inputs/training'
nn_folder_name = '{}/movement_duration_nns'.format(BASE_PART)
movements_filename = '{}/movements_01.json'.format(BASE_PART)

movements_json_data = read_json_from_file(movements_filename)
robots = {
    robot_json['id']: robot_from_json(robot_json)
    for robot_json in movements_json_data['robots']
}
movements_data = [
    (movement_from_json(movement_json, robots), tuple(movement_json['min_max_duration']))
    for movement_json in movements_json_data['movements']
]

nn_filenames = ['{}/{}'.format(nn_folder_name, f) for f in listdir(nn_folder_name) if f.endswith('.json')]
nns_data = []


def train(nn_layers: List[int], parameters: List[str]) -> Tuple[float, List[float]]:
    """
    Trains a NN with given layers and used input parameters.
    Returns its achieved accuracy and trained inner parameters.
    """
    return 0.0, []


for nn_filename in nn_filenames:
    nn_data = read_nn_data_from_file(nn_filename)

    nn_data['accuracy'], nn_data['nn_parameters'] = train(nn_data['nn_layers'], nn_data['parameters'])

    nns_data.append(nn_data)
