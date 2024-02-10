import csv
from typing import List

from gurobipy import GRB

from ilp.activity import MovementActivity
from ilp.model import Model
from utils.json import read_json_from_file, save_to_json_file

INPUT_DIR = 'D:/Uloziste/Skola/DP/Algorithm/rce-optimizer/_inputs/time_windows'
CSV_RESULT_PATH = 'D:/Uloziste/Skola/DP/Algorithm/rce-optimizer/_inputs/time_windows_results.csv'

csv_result: List[List[str]] = [['length', 'num', 'min_d', 'max_d = ct', 'start_idle', 'movement_d', 'end_idle']]

for length in [20, 40, 80, 120]:
    for num in ['01', '02', '03', '04', '05', '06', '07']:
        csv_row = [str(length), num]
        input_filename = f'{INPUT_DIR}/{length}cm_{num}.json'
        output_filename = f'{INPUT_DIR}/{length}cm_{num}_result.json'
        gantt_chart_filename = f'{INPUT_DIR}/{length}cm_{num}_chart.png'

        model = Model()

        json = read_json_from_file(input_filename)
        model.load_from_json(json)
        model.optimize()

        if model.status() != GRB.OPTIMAL:
            print(f'ERROR: Model for {length}cm, num {num} has status: {model.status()}')
            csv_row += [f'Not optimal solution found, status: {model.status()}', '', '', '', '']
        else:
            solution = model.solution_json_dict()
            save_to_json_file(output_filename, solution)
            model.create_gantt_chart(gantt_chart_filename, (10, 5))
            start_idle = model.activities['r01_a01_idle']
            movement: MovementActivity = model.activities['r01_a02_move']
            end_idle = model.activities['r01_a03_idle']
            min_d = movement.min_duration
            max_d = movement.max_duration
            start_d = str(start_idle.duration.x)
            move_d = str(movement.duration.x)
            end_d = str(end_idle.duration.x)
            print(f'OK:    Optimal solution for model for {length}cm, num {num} found: {start_d}, {move_d}, {end_d}')
            csv_row += [min_d, max_d, start_d, move_d, end_d]

        csv_result.append(csv_row)

with open(CSV_RESULT_PATH, "w") as csv_file:
    writer = csv.writer(csv_file, delimiter='\t')
    writer.writerows(csv_result)
