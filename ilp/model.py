from typing import Dict, List, Tuple, Optional

import gurobipy as g
import matplotlib.pyplot as plt

from ilp.activity import StaticActivity, Activity, DynamicActivity
from nn.movement_duration_nn import MovementDurationNN
from nn.movement_energy_nn import MovementEnergyNN
from nn.position_nn import PositionNN
from preprocessing.movement import LinearMovement, JointMovement, CompoundMovement
from preprocessing.robot import Robot
from utils.bad_input_file_error import BadInputFileError
from utils.json import point3d_from_json, simple_movement_from_partial_json

TimeOffset = Tuple[Activity, Activity, Optional[float], Optional[float]]
Collision = Tuple[Activity, Activity, g.Var]


class Model:
    """
    ILP model for energy consumption optimization wrapping Gurobi model.

    It uses (3*A + 1) real variables, C binary variables, less then (8*A + 2*T) linear constraints,
    and 2*C quadratic constraints, where A is total number of activities, C is number of collision pairs,
    T is number of relative time restrictions, i.e. number of variables and constraints is linear with
    respect to problem size.
    """
    def __init__(
        self,
        position_nn: PositionNN,
        movement_energy_nn: MovementEnergyNN,
        movement_duration_nn: MovementDurationNN,
    ):
        self.position_nn = position_nn
        self.movement_energy_nn = movement_energy_nn
        self.movement_duration_nn = movement_duration_nn
        self.model = g.Model()
        self.cycle_time = 0
        self.robot_to_activities: Dict[str, List[Activity]] = dict()
        self.activities: Dict[str, Activity] = dict()
        self.time_offsets: List[TimeOffset] = []
        self.collisions: List[Collision] = []

    def load_from_json(self, cell_json: Dict):
        """
        Loads data from given JSON dictionary. If the JSON does not contain required data, throws BadInputFileError.
        """
        self.cycle_time = cell_json['cycle_time']

        for robot in cell_json.get('robots', []):
            self._process_robot(robot)

        for time_offset in cell_json.get('time_offsets', []):
            self._process_time_offset(time_offset)

        for collision in cell_json.get('collisions', []):
            self._process_collision(collision)

        # the goal is to minimize sum of activity energies
        self.model.setObjective(
            g.quicksum(list(map(lambda a: a.energy, self.activities.values()))),
            g.GRB.MINIMIZE,
        )

    def optimize(self):
        """
        Optimizes the model. The model needs to be loaded first using load_from_json function.
        """
        self.model.optimize()

    def solution_json_dict(self):
        """
        Creates a dictionary with an optimization solution ready to be saved in a JSON file.
        """
        # TODO - save result energy
        return {
            'cycle_time': self.cycle_time,
            'robots': [
                {
                    'id': robot,
                    'activities': [
                        activity.solution_json_dict(self.cycle_time)
                        for activity in self.robot_to_activities[robot]
                    ]
                }
                for robot in self.robot_to_activities.keys()
            ]
        }

    def create_gantt_chart(self, gantt_filename: str, size: Tuple[float, float] = (10, 5)):
        """
        Creates a Gantt's chart of the solution and saves it in the given file.
        """
        activities = list(self.activities.values())

        fig, ax = plt.subplots(figsize=size)
        ax.invert_yaxis()

        # add first parts of activities
        ax.barh(
            list(map(lambda a: a.id, activities)),
            list(map(lambda a: a.first_part_duration(self.cycle_time), activities)),
            left=list(map(lambda _: 0, activities)),
            color='b',
        )
        # add second parts of activities
        ax.barh(
            list(map(lambda a: a.id, activities)),
            list(map(lambda a: a.second_part_duration(self.cycle_time), activities)),
            left=list(map(lambda a: a.cycle_start_time(self.cycle_time), activities)),
            color='b',
        )

        plt.savefig(gantt_filename)

    def _process_robot(self, robot_json: Dict):
        robot = Robot(
            robot_json['id'],
            point3d_from_json(robot_json['position']),
            robot_json['weight'],
            robot_json['load_capacity'],
            robot_json['input_power'],
        )

        activities: List[Activity] = list(map(
            lambda activity_json: self._process_activity(activity_json, robot),
            robot_json['activities'],
        ))

        # add time constraints
        self._add_constr(
            g.quicksum(list(map(lambda a: a.duration, activities))) == self.cycle_time
        )
        for i in range(len(activities) - 1):
            j = i + 1
            self._add_constr(
                activities[i].start_time + activities[i].duration == activities[j].start_time
            )

        # saves robot activities
        self.robot_to_activities[robot.id] = activities
        self.activities.update({a.id: a for a in activities})

    def _process_activity(self, activity_json: Dict, robot: Robot) -> Activity:
        activity_type = activity_json['type']
        if activity_type == 'static':
            return self._process_static_activity(activity_json, robot)
        elif activity_type == 'dynamic':
            return self._process_dynamic_activity(activity_json, robot)
        else:
            raise BadInputFileError('Activity type must be "static" or "dynamic", not {}'.format(activity_type))

    def _process_static_activity(self, activity_json: Dict, robot: Robot) -> StaticActivity:
        # add activity params
        static_activity = StaticActivity(activity_json['id'])
        static_activity.min_duration = activity_json.get('min_duration')
        static_activity.compute_energy_coef(
            point3d_from_json(activity_json['position']),
            activity_json['payload_weight'],
            robot,
            self.position_nn,
        )

        # add activity variables
        self._add_activity_vars(static_activity)

        # if minimal duration is specified, constraints the duration
        if static_activity.min_duration is not None:
            self._add_constr(
                static_activity.min_duration <= static_activity.duration,
            )

        # computes activity energy consumption
        self._add_constr(
            static_activity.energy == static_activity.energy_coef * static_activity.duration
        )

        return static_activity

    def _process_dynamic_activity(self, activity_json: Dict, robot: Robot) -> DynamicActivity:
        # add activity params
        dynamic_activity = DynamicActivity(activity_json['id'])

        given_min = activity_json.get('min_duration')
        given_max = activity_json.get('max_duration')
        movement_type = activity_json['movement_type']
        payload_weight = activity_json['payload_weight']

        if movement_type == 'linear':
            dynamic_activity.set_movement(
                LinearMovement(
                    point3d_from_json(activity_json['start']),
                    point3d_from_json(activity_json['end']),
                    payload_weight,
                    robot,
                )
            )
            dynamic_activity.compute_min_max_duration(given_min, given_max, self.movement_duration_nn)
            dynamic_activity.compute_energy_profile(self.movement_energy_nn)

        elif movement_type == 'joint':
            dynamic_activity.set_movement(
                JointMovement(
                    point3d_from_json(activity_json['start']),
                    point3d_from_json(activity_json['end']),
                    payload_weight,
                    robot,
                )
            )
            dynamic_activity.compute_min_max_duration(given_min, given_max, self.movement_duration_nn)
            dynamic_activity.compute_energy_profile(self.movement_energy_nn)

        elif movement_type == 'compound':
            partial_movements = list(map(
                lambda json: simple_movement_from_partial_json(json, payload_weight, robot),
                activity_json['partial_movements'],
            ))
            dynamic_activity.set_movement(
                CompoundMovement(
                    partial_movements,
                    payload_weight,
                    robot,
                )
            )
            dynamic_activity.compute_min_max_duration(given_min, given_max, self.movement_duration_nn)
            dynamic_activity.compute_energy_profile(self.movement_energy_nn)

        else:
            raise BadInputFileError(
                'Movement type must be "linear", "joint" or "compound", not {}'.format(movement_type)
            )

        # add activity variables
        self._add_activity_vars(dynamic_activity)

        # every dynamic activity has constrained minimal and maximal duration (with given or estimated values)
        self._add_constr(
            dynamic_activity.min_duration <= dynamic_activity.duration,
        )
        self._add_constr(
            dynamic_activity.duration <= dynamic_activity.max_duration,
        )

        # computes activity energy consumption
        for line in dynamic_activity.energy_profile_lines:
            self._add_constr(
                dynamic_activity.energy >= line.q * dynamic_activity.duration + line.c
            )

        return dynamic_activity

    def _process_time_offset(self, time_offset_json: Dict):
        a_id = time_offset_json['a_id']
        b_id = time_offset_json['b_id']
        min_offset = time_offset_json.get('min_offset')
        max_offset = time_offset_json.get('max_offset')
        a = self.activities[a_id]
        b = self.activities[b_id]
        # adds offset constraint
        if min_offset is not None:
            self._add_constr(
                a.start_time + min_offset <= b.start_time
            )
        if max_offset is not None:
            self._add_constr(
                a.start_time + max_offset >= b.start_time
            )
        # saves offset info
        self.time_offsets.append((a, b, min_offset, max_offset))

    def _process_collision(self, collision_json: Dict):
        """
        If a bug with collisions ever appears (there will be a collision in the Gantt's chart) it might be because of
        cycle-time shift of start_times in model. It can be solved by adding "cycle_start_time" and "is_shifted"
        variables for each activity used in collisions:
          - 0 <= cycle_start_time <= cycle_time
          - cycle_start_time == start_time - cycle_time * is_shifted   => possibly more quadratic constraints
        """
        a_id = collision_json['a_id']
        b_id = collision_json['b_id']
        a = self.activities[a_id]
        b = self.activities[b_id]
        x = self._add_var(vtype=g.GRB.BINARY, name='x_{}_{}'.format(a_id, b_id))
        # adds collision resolution constraints
        self._add_constr(
            a.start_time + a.duration <= b.start_time + (1 - x) * self.cycle_time
        )
        self._add_constr(
            b.start_time + b.duration <= a.start_time + x * self.cycle_time
        )
        # saves collision info
        self.collisions.append((a, b, x))

    def _add_activity_vars(self, activity: Activity):
        activity.start_time = self._add_var(name='start_time_{}'.format(activity.id))
        activity.duration = self._add_var(name='duration_{}'.format(activity.id))
        activity.energy = self._add_var(name='energy_{}'.format(activity.id))
        self._add_constr(
            activity.start_time <= 2 * self.cycle_time
        )

    def _add_constr(self, constr):
        self.model.addConstr(constr)

    def _add_var(self, lb=0, vtype=g.GRB.CONTINUOUS, name='') -> g.Var:
        return self.model.addVar(lb=lb, vtype=vtype, name=name)
