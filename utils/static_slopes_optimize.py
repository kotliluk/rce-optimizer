import csv
from typing import List

from gurobipy import GRB

from ilp.activity import MovementActivity, IdleActivity
from ilp.model import Model
from utils.json import read_json_from_file, save_to_json_file

INPUT_DIR = 'D:/Uloziste/Skola/DP/Algorithm/rce-optimizer/_inputs/static_slopes'
CSV_RESULT_PATH = 'D:/Uloziste/Skola/DP/Algorithm/rce-optimizer/_inputs/static_slopes_results.csv'

csv_result: List[List[str]] = [[
    'length', 'point A', 'point B', 'point C', 'B slope',
    'A-B line 1', 'A-B line 2', 'A-B line 3', 'A-B line 1', 'A-B line 2', 'A-B line 3',
]]

for length in [40]:
    for points in [('b', 'c', 'b'), ('g', 'b', 'c'), ('i', 'k', 'j'), ('k', 'i', 'j')]:
        point_a, point_b, point_c = points
        csv_row = [str(length), point_a, point_b, point_c]
        input_filename = f'{INPUT_DIR}/{point_a}_{point_b}_{point_c}_{length}cm.json'
        output_filename = f'{INPUT_DIR}/{point_a}_{point_b}_{point_c}_{length}cm_result.json'
        gantt_chart_filename = f'{INPUT_DIR}/{point_a}_{point_b}_{point_c}_{length}cm_chart.png'

        model = Model()

        json = read_json_from_file(input_filename)
        model.load_from_json(json)
        model.optimize()

        if model.status() != GRB.OPTIMAL:
            print(f'ERROR: Model for {point_a}_{point_b}_{point_c}, {length}cm has status: {model.status()}')
            csv_row += [f'Not optimal solution found, status: {model.status()}', '', '', '', '', '', '', '']
        else:
            solution = model.solution_json_dict()
            save_to_json_file(output_filename, solution)
            model.create_gantt_chart(gantt_chart_filename, (10, 5))
            b_position: IdleActivity = model.activities[f'r01_a03_idle_{point_b}']
            ab_movement: MovementActivity = model.activities[f'r01_a02_move_{point_a}{point_b}']
            bc_movement: MovementActivity = model.activities[f'r01_a04_move_{point_b}{point_c}']
            b_slope = b_position.energy_profile_lines[0].q
            ab_lines = ab_movement.energy_profile_lines
            bc_lines = bc_movement.energy_profile_lines
            print(f'OK:    Optimal solution for model for {point_a}_{point_b}_{point_c}, {length}cm found')
            csv_row += [f'y = {b_slope}x',
                        str(ab_lines[0]), str(ab_lines[1]), str(ab_lines[2]),
                        str(bc_lines[0]), str(bc_lines[1]), str(bc_lines[2]),
                        ]

        csv_result.append(csv_row)

with open(CSV_RESULT_PATH, "w") as csv_file:
    writer = csv.writer(csv_file, delimiter='\t')
    writer.writerows(csv_result)
