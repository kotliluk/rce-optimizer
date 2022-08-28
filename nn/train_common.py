from typing import Dict

from utils.json import read_json_from_file


def read_nn_data_from_file(filename: str) -> Dict:
    nn_data = read_json_from_file(filename)

    nn_layers = list(nn_data.get('hidden_layers', []))
    nn_layers.insert(0, len(nn_data['parameters']))
    nn_layers.append(nn_data['outputs'])

    nn_data['nn_layers'] = nn_layers
    nn_data['nn_parameters_count'] = sum([nn_layers[i] * nn_layers[i + 1] for i in range(len(nn_layers) - 1)])

    return nn_data
