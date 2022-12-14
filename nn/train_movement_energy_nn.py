from os import listdir
from typing import List, Tuple

from nn.train_common import read_nn_data_from_file
from utils.json import read_json_from_file, robot_from_json, movement_from_json

BASE_PART = 'D:/Uloziste/Skola/DP/Algorithm/rce-optimizer/_inputs/training'
nn_folder_name = '{}/movement_energy_nns'.format(BASE_PART)
movements_filename = '{}/movements_01.json'.format(BASE_PART)

movements_json_data = read_json_from_file(movements_filename)
robots = {
    robot_json['id']: robot_from_json(robot_json)
    for robot_json in movements_json_data['robots']
}
movements_data = [
    (movement_from_json(movement_json, robots), tuple(movement_json['energy_4_coefs']))
    for movement_json in movements_json_data['movements']
]

nn_filenames = ['{}/{}'.format(nn_folder_name, f) for f in listdir(nn_folder_name) if f.endswith('.json')]
nns_data = []


def train(nn_layers: List[int], parameters: List[str]) -> Tuple[float, List[float]]:
    """
    Trains a NN with given layers and used input parameters.
    Returns its achieved accuracy and trained inner parameters.
    """
    # batch_sz = 32
    # learning_rate = 0.05
    # epochs = 20
    # trn_size = int(0.07 * len(movements_data))
    # val_size = len(movements_data) - trn_size
    #
    # trn_dataset, val_dataset = torch.utils.data.random_split(movements_data, [trn_size, val_size])
    # trn_loader = torch.utils.data.DataLoader(trn_dataset, batch_size=batch_sz, shuffle=True)
    # val_loader = torch.utils.data.DataLoader(val_dataset, batch_size=batch_sz, shuffle=False)
    #
    # device = torch.device("cpu")
    # model = TestMovementEnergyNN(nn_layers).to(device)
    # optimizer = optim.SGD(model.parameters(), lr=learning_rate)

    return 0.0, []


for nn_filename in nn_filenames:
    nn_data = read_nn_data_from_file(nn_filename)

    nn_data['energy_accuracy'], nn_data['nn_parameters'] = train(nn_data['nn_layers'], nn_data['parameters'])

    nns_data.append(nn_data)
