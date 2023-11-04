from ilp.model import Model
from utils.json import read_json_from_file, save_to_json_file

BASE_PATH = 'D:/Uloziste/Skola/DP/Algorithm/rce-optimizer/_inputs/optimization'
INPUT = '01'

input_filename = '{}/robotic_cell_{}.json'.format(BASE_PATH, INPUT)
output_filename = '{}/robotic_cell_{}_result.json'.format(BASE_PATH, INPUT)
gantt_chart_filename = '{}/robotic_cell_{}_gantt_chart.png'.format(BASE_PATH, INPUT)

model = Model()

json = read_json_from_file(input_filename)
model.load_from_json(json)
model.optimize()
print(model.model.display())

for activity in model.activities.values():
    print(activity)

solution = model.solution_json_dict()
print(solution)
save_to_json_file(output_filename, solution)

if gantt_chart_filename is not None:
    model.create_gantt_chart(gantt_chart_filename, (10, 5))
