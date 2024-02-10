import csv


def parse(in_file_path: str, out_dir: str):
    with open(in_file_path) as in_file:
        in_file_reader = csv.reader(in_file, delimiter='\t')

        for row in in_file_reader:
            length, num, min_dur, max_dur, start, end = row
            json_str = '{\n' \
                       f'  "cycle_time": {max_dur},\n' \
                       f'  "description": "Length: {length}cm, movement: {num}",\n' \
                       '  "robots": [\n' \
                       '    {\n' \
                       '      "id": "r01",\n' \
                       '      "position": { "x": 0.0, "y": 0.0, "z": 0.0 },\n' \
                       '      "weight": 400.0,\n' \
                       '      "maximum_reach": 2016.0,\n' \
                       f'      "min_activities_duration": {min_dur},\n' \
                       '      "activities": [\n' \
                       '        {\n' \
                       '          "type": "IDLE",\n' \
                       '          "id": "r01_a01_idle",\n' \
                       f'          "position": {start}\n' \
                       '        },\n' \
                       '        {\n' \
                       '          "type": "MOVEMENT",\n' \
                       '          "id": "r01_a02_move",\n' \
                       f'          "min_duration": {min_dur},\n' \
                       f'          "max_duration": {max_dur},\n' \
                       f'          "start": {start},\n' \
                       f'          "end": {end}\n' \
                       '        },\n' \
                       '        {\n' \
                       '          "type": "IDLE",\n' \
                       '          "id": "r01_a03_idle",\n' \
                       f'          "position": {end}\n' \
                       '        }\n' \
                       '      ]\n' \
                       '    }\n' \
                       '  ]\n' \
                       '}'
            out_file_path = f'{out_dir}/{length}cm_{num}.json'

            with open(out_file_path, "w") as out_file:
                out_file.write(json_str)


if __name__ == "__main__":
    in_f = "D:/Uloziste/Skola/DP/Algorithm/rce-optimizer/_inputs/time_windows_values.csv"
    out_d = "D:/Uloziste/Skola/DP/Algorithm/rce-optimizer/_inputs/time_windows"
    parse(in_f, out_d)
