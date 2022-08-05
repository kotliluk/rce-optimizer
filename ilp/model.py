import gurobipy as g
from typing import Dict, List, Tuple

from ilp.activity import StaticActivity, Activity, DynamicActivity
from nn.position_nn import PositionNN
from nn.movement_nn import MovementNN
from preprocessing.robot import Robot
from utils.bad_input_file_error import BadInputFileError
from utils.json import point3d_from_json, simple_movement_from_partial_json


TimeOffset = Tuple[Activity, Activity, float]
Collision = Tuple[Activity, Activity, g.Var]


class Model:
    """
    ILP model for energy consumption optimization wrapping Gurobi model.
    """
    def __init__(self, position_nn: PositionNN, movement_nn: MovementNN):
        self.position_nn = position_nn
        self.movement_nn = movement_nn
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

        self._add_constr(
            g.quicksum(list(map(lambda a: a.duration, self.activities.values()))) <= self.cycle_time
        )

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
        return {
            'input_cycle_time': self.cycle_time,
            'result_cycle_time': self.result_cycle_time(),
            'robots': [
                {
                    'id': robot,
                    'activities': [activity.solution_json_dict() for activity in self.robot_to_activities[robot]]
                }
                for robot in self.robot_to_activities.keys()
            ]
        }

    def result_cycle_time(self) -> float:
        """
        Returns cycle time computed in an optimization.
        """
        return sum(map(lambda a: a.duration.x, self.activities.values()))

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
        # TODO - initial is always first?
        activities[0].is_initial = True
        self._add_constr(
            activities[0].start_time == 0
        )

        # add time constraints
        for i in range(len(activities) - 1):
            j = i + 1
            if activities[j].is_initial:
                self._add_constr(
                    activities[i].start_time + activities[i].duration <= activities[j].start_time + self.cycle_time
                )
            else:
                self._add_constr(
                    activities[i].start_time + activities[i].duration <= activities[j].start_time
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
        dynamic_activity.min_duration = activity_json.get('min_duration')
        dynamic_activity.max_duration = activity_json.get('max_duration')

        movement_type = activity_json['movement_type']
        payload_weight = activity_json['payload_weight']
        if movement_type == 'linear':
            dynamic_activity.compute_linear_energy_profile(
                point3d_from_json(activity_json['start']),
                point3d_from_json(activity_json['end']),
                payload_weight,
                robot,
                self.movement_nn,
            )
        elif movement_type == 'joint':
            dynamic_activity.compute_joint_energy_profile(
                point3d_from_json(activity_json['start']),
                point3d_from_json(activity_json['end']),
                payload_weight,
                robot,
                self.movement_nn,
            )
        elif movement_type == 'compound':
            partial_movements = list(map(
                lambda partial_movement_json: simple_movement_from_partial_json(
                    partial_movement_json,
                    payload_weight,
                    robot,
                ),
                activity_json['partial_movements'],
            ))
            dynamic_activity.compute_compound_energy_profile(
                partial_movements,
                payload_weight,
                robot,
                self.movement_nn,
            )
        else:
            raise BadInputFileError(
                'Movement type must be "linear", "joint" or "compound", not {}'.format(movement_type)
            )

        # add activity variables
        self._add_activity_vars(dynamic_activity)

        # if minimal duration is specified, constraints the duration
        if dynamic_activity.min_duration is not None:
            self._add_constr(
                dynamic_activity.min_duration <= dynamic_activity.duration,
            )

        # if maximal duration is specified, constraints the duration
        if dynamic_activity.max_duration is not None:
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
        offset = time_offset_json['offset']
        a = self.activities[a_id]
        b = self.activities[b_id]
        # adds offset constraint
        self._add_constr(
            a.start_time + offset <= b.start_time
        )
        # saves offset info
        self.time_offsets.append((a, b, offset))

    def _process_collision(self, collision_json: Dict):
        a_id = collision_json['a_id']
        b_id = collision_json['b_id']
        a = self.activities[a_id]
        b = self.activities[b_id]
        x = self.model.addVar(vtype=g.GRB.BINARY, name='x_{}_{}'.format(a_id, b_id))
        # adds collision resolution constraints
        self._add_constr(
            a.start_time + a.duration <= b.start_time + (1 - x) * self.cycle_time
        )
        self._add_constr(
            b.start_time + b.duration <= a.start_time + x * self.cycle_time
        )
        # saves collision info
        self.collisions.append((a, b, x))

    def _add_constr(self, constr):
        self.model.addConstr(constr)

    def _add_activity_vars(self, activity: Activity):
        activity.start_time = self.model.addVar(
            lb=0, vtype=g.GRB.CONTINUOUS, name='start_time_{}'.format(activity.id)
        )
        activity.duration = self.model.addVar(
            lb=0, vtype=g.GRB.CONTINUOUS, name='duration_{}'.format(activity.id)
        )
        activity.energy = self.model.addVar(
            lb=0, vtype=g.GRB.CONTINUOUS, name='energy_{}'.format(activity.id)
        )
