from gurobipy import GRB

from ilp.model import Model
from utils.json import read_json_from_file, save_to_json_file

BASE_PATH = 'D:/Uloziste/Skola/DP/Algorithm/rce-optimizer/_inputs/optimization'
INPUT = '05'

input_filename = '{}/robotic_cell_{}.json'.format(BASE_PATH, INPUT)
output_filename = '{}/robotic_cell_{}_result.json'.format(BASE_PATH, INPUT)
gantt_chart_filename = '{}/robotic_cell_{}_gantt_chart.png'.format(BASE_PATH, INPUT)

model = Model()

json = read_json_from_file(input_filename)
model.load_from_json(json)
model.optimize()

if model.status() != GRB.OPTIMAL:
    print(f'ERROR: Model has status: {model.status()}')
else:
    print(f'OK:    Optimal solution for model found')
    solution = model.solution_json_dict()
    save_to_json_file(output_filename, solution)
    model.create_gantt_chart(gantt_chart_filename, (10, 5))
