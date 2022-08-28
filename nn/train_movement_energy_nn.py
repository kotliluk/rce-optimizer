from typing import List

from utils.json import read_json_from_file
from utils.read_movements_for_nn_training import read_movements_for_nn_training

BASE_PART = 'D:/Uloziste/Skola/DP/Algorithm/rce-optimizer/_inputs/training'

nn_folder_name = '{}/nns'.format(BASE_PART)
movements_filename = '{}/movements_01.json'.format(BASE_PART)

# reads data
movements_energy_data, _ = read_movements_for_nn_training(movements_filename)

print(movements_energy_data)

# TODO - get file names in folder
nn_filenames = ['{}/nn_01.json'.format(nn_folder_name)]
nns_data = []


def train(nn_layers: List[int], parameters: List[str]) -> float:
    # batch_sz = 32
    # learning_rate = 0.05
    # epochs = 20
    # trn_size = int(0.07 * len(movements_energy_data))
    # val_size = len(movements_energy_data) - trn_size
    #
    # trn_dataset, val_dataset = torch.utils.data.random_split(movements_data, [trn_size, val_size])
    # trn_loader = torch.utils.data.DataLoader(trn_dataset, batch_size=batch_sz, shuffle=True)
    # val_loader = torch.utils.data.DataLoader(val_dataset, batch_size=batch_sz, shuffle=False)
    #
    # device = torch.device("cpu")
    # model = TestMovementEnergyNN(nn_layers).to(device)
    # optimizer = optim.SGD(model.parameters(), lr=learning_rate)

    return 0.0


for nn_filename in nn_filenames:
    nn_data = read_json_from_file(nn_filename)

    nn_layers = nn_data.get('hidden_layers', [])
    nn_layers.insert(0, len(nn_data['parameters']))
    nn_layers.append(nn_data['outputs'])

    nn_data['nn_layers'] = nn_layers
    nn_data['nn_parameters_count'] = sum([nn_layers[i] * nn_layers[i + 1] for i in range(len(nn_layers) - 1)])
    nn_data['nn_parameters'] = None

    nn_data['energy_accuracy'] = train(nn_layers, nn_data['parameters'])

    nns_data.append(nn_data)


print(nns_data)
