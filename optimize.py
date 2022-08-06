from ilp.model import Model
from nn.movement_duration_nn import MovementDurationNN
from nn.movement_energy_nn import MovementEnergyNN
from nn.position_nn import PositionNN
from utils.json import read_json_from_file, save_to_json_file

input_filename = 'D:/Uloziste/Skola/DP/Algorithm/_test_inputs/robotic_cell_01.json'
output_filename = 'D:/Uloziste/Skola/DP/Algorithm/_test_inputs/robotic_cell_01_result.json'

movement_energy_nn = MovementEnergyNN()
movement_duration_nn = MovementDurationNN()
position_nn = PositionNN()

model = Model(position_nn, movement_energy_nn, movement_duration_nn)

json = read_json_from_file(input_filename)
model.load_from_json(json)
model.optimize()

for activity in model.activities.values():
    print(activity)

solution = model.solution_json_dict()
print(solution)
save_to_json_file(output_filename, solution)
