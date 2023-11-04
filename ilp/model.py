from typing import Dict, List, Tuple, Optional

import gurobipy as g
import matplotlib.pyplot as plt

from ilp.activity import Activity, MovementActivity, WorkActivity, IdleActivity
from preprocessing.energy_profile import compute_movement_energy_profile, compute_idle_energy_profile
from preprocessing.robot import Robot
from utils.bad_input_file_error import BadInputFileError
from utils.json import point3d_from_json, joint_movement_from_json

TimeOffset = Tuple[Activity, Activity, Optional[float], Optional[float]]
Collision = Tuple[Activity, Activity, g.Var]


class Model:
    """
    ILP model for energy consumption optimization wrapping Gurobi model.

    It uses (3*A + 1) real variables, C binary variables, less then (8*A + 2*T + 2*C) linear constraints,
    where A is total number of activities (including added idling activities in between each pair of input activities),
    C is number of collision pairs, T is number of relative time restrictions,
    i.e. number of variables and constraints is linear with respect to problem size.
    """
    def __init__(self):
        self.model = g.Model()
        self.cycle_time: float = 0
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
        return {
            'cycle_time': self.cycle_time,
            'robots': [
                {
                    'id': robot,
                    'activities': [
                        activity.solution_json_dict() for activity in self.robot_to_activities[robot]
                    ]
                }
                for robot in self.robot_to_activities.keys()
            ],
            'energy': sum(map(
                lambda robot_activities: sum(map(lambda activity: activity.energy.x, robot_activities)),
                self.robot_to_activities.values(),
            )),
        }

    def create_gantt_chart(self, gantt_filename: str, size: Tuple[float, float] = (10, 5)):
        """
        Creates a Gantt's chart of the solution and saves it in the given file.
        """
        activities = list(self.activities.values())

        fig, ax = plt.subplots(figsize=size)
        ax.invert_yaxis()

        ax.barh(
            list(map(lambda a: a.id, activities)),
            list(map(lambda a: a.duration.x, activities)),
            left=list(map(lambda a: a.start_time.x, activities)),
            color='b',
        )

        plt.savefig(gantt_filename)

    def _process_robot(self, robot_json: Dict):
        robot = Robot(
            robot_json['id'],
            point3d_from_json(robot_json['position']),
        )

        min_activities_duration = robot_json['min_activities_duration']

        activities: List[Activity] = list(map(
            lambda activity_json: self._process_activity(activity_json, robot, min_activities_duration),
            robot_json['activities'],
        ))

        # add time constraints
        self._add_constr(
            activities[0].start_time == 0
        )
        self._add_constr(
            activities[-1].start_time + activities[-1].duration == self.cycle_time
        )
        for i in range(len(activities) - 1):
            j = i + 1
            self._add_constr(
                activities[i].start_time + activities[i].duration == activities[j].start_time
            )

        # saves robot activities
        self.robot_to_activities[robot.id] = activities
        self.activities.update({a.id: a for a in activities})

    def _process_activity(self, activity_json: Dict, robot: Robot, min_activities_duration: float) -> Activity:
        activity_type = activity_json['type']
        if activity_type == 'WORK':
            return self._process_work_activity(activity_json)
        elif activity_type == 'MOVEMENT':
            return self._process_movement_activity(activity_json, robot)
        elif activity_type == 'IDLE':
            return self._process_idle_activity(activity_json, min_activities_duration)
        else:
            raise BadInputFileError('Activity type must be "MOVEMENT", "WORK" or "IDLE", not {}'.format(activity_type))

    def _process_work_activity(self, activity_json: Dict) -> WorkActivity:
        # add activity params
        work_activity = WorkActivity(
            activity_json['id'],
            activity_json['duration'],
            activity_json.get('fixed_start_time'),
            activity_json.get('fixed_end_time'),
        )

        # add activity variables
        self._add_activity_vars(work_activity)

        # add fixed duration
        self._add_constr(
            work_activity.duration == work_activity.fixed_duration,
        )

        # if fixed start time is specified, sets it
        if work_activity.fixed_start_time is not None:
            self._add_constr(
                work_activity.start_time == work_activity.fixed_start_time,
            )

        # if fixed end time is specified, sets it
        if work_activity.fixed_end_time is not None:
            self._add_constr(
                work_activity.start_time + work_activity.duration == work_activity.fixed_end_time,
            )

        # work activity does not affect the optimization
        self._add_constr(
            work_activity.energy == 0
        )

        return work_activity

    def _process_movement_activity(self, activity_json: Dict, robot: Robot) -> MovementActivity:
        # add activity params
        movement_activity = MovementActivity(
            activity_json['id'],
            activity_json['min_duration'],
            activity_json['max_duration'],
            activity_json.get('fixed_start_time'),
            activity_json.get('fixed_end_time'),
        )

        # add activity variables
        self._add_activity_vars(movement_activity)

        # every movement activity has constrained minimal and maximal duration (with given or estimated values)
        self._add_constr(
            movement_activity.min_duration <= movement_activity.duration,
        )
        self._add_constr(
            movement_activity.duration <= movement_activity.max_duration,
        )

        # if fixed start time is specified, sets it
        if movement_activity.fixed_start_time is not None:
            self._add_constr(
                movement_activity.start_time == movement_activity.fixed_start_time,
            )

        # if fixed end time is specified, sets it
        if movement_activity.fixed_end_time is not None:
            self._add_constr(
                movement_activity.start_time + movement_activity.duration == movement_activity.fixed_end_time,
            )

        # computes activity energy consumption
        movement = joint_movement_from_json(activity_json, robot)
        movement_activity.energy_profile_lines = compute_movement_energy_profile(movement)
        for line in movement_activity.energy_profile_lines:
            self._add_constr(
                movement_activity.energy >= line.q * movement_activity.duration + line.c
            )

        return movement_activity

    def _process_idle_activity(self, activity_json: Dict, min_activities_duration: float) -> IdleActivity:
        idle_activity = IdleActivity(activity_json['id'])

        # add activity variables
        self._add_activity_vars(idle_activity)

        # constraints the idling duration
        self._add_constr(
            0 <= idle_activity.duration,
        )
        self._add_constr(
            idle_activity.duration <= self.cycle_time - min_activities_duration,
        )

        # computes activity energy consumption
        point = point3d_from_json(activity_json['position'])
        idle_activity.energy_profile_lines = compute_idle_energy_profile(point)
        for line in idle_activity.energy_profile_lines:
            self._add_constr(
                idle_activity.energy >= line.q * idle_activity.duration + line.c
            )

        return idle_activity

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
        Adds constraints for the given collision.
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
