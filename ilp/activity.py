from typing import Optional, List

import gurobipy as g

from nn.movement_duration_nn import MovementDurationNN
from nn.movement_energy_nn import MovementEnergyNN
from nn.position_nn import PositionNN
from preprocessing.movement import Movement
from preprocessing.piecewise_linearization import piecewise_linearize
from preprocessing.position import Position
from preprocessing.robot import Robot
from utils.geometry_2d import Line2D
from utils.geometry_3d import Point3D


class Activity:
    """
    Base class for activity representation in ILP model.
    It stores activity id, variables and initial-flag.
    """
    def __init__(self, id_: str):
        self.id = id_
        # vars
        self.start_time: Optional[g.Var] = None
        self.duration: Optional[g.Var] = None
        self.energy: Optional[g.Var] = None

    def cycle_start_time(self, cycle_time: float) -> float:
        return self.start_time.x % cycle_time

    def cycle_end_time(self, cycle_time: float) -> float:
        result = (self.start_time.x + self.duration.x) % cycle_time
        return result if result > 0 else cycle_time

    def solution_json_dict(self, cycle_time: float):
        """
        Saves activity id and variables in a dictionary ready to be saved in a JSON file.
        """
        return {
            'id': self.id,
            'start_time': round(self.cycle_start_time(cycle_time), 3),
            'duration': round(self.duration.x, 3),
            'end_time': round(self.cycle_end_time(cycle_time), 3),
            'energy': round(self.energy.x, 6),
        }

    def is_split(self, cycle_time: float) -> bool:
        """
        Returns whether the activity is split, i.e. it starts in one cycle and ends in the next one.
        """
        return self.cycle_end_time(cycle_time) < self.cycle_start_time(cycle_time)

    def first_part_duration(self, cycle_time: float) -> float:
        """
        Returns duration of the first part (shifted to start in Gantt chart) of activity if the activity is split,
        0 otherwise.
        """
        if self.is_split(cycle_time):
            return self.cycle_end_time(cycle_time)
        return 0

    def second_part_duration(self, cycle_time: float) -> float:
        """
        Returns duration of the second part (in Gantt chart) of activity if the activity is split,
        total duration otherwise.
        """
        if self.is_split(cycle_time):
            return cycle_time - self.cycle_start_time(cycle_time)
        return self.duration.x

    def __str__(self):
        return 'activity "{}", VARS: s={}, d={}, e={}'.format(
            self.id,
            round(self.start_time.x, 3),
            round(self.duration.x, 3),
            round(self.energy.x, 3),
        )

    def __repr__(self):
        return self.__str__()


class StaticActivity(Activity):
    """
    Class for static activity representation in ILP model.
    Adds storing of static activity ILP parameters: minimal duration and energy coefficient.
    """
    def __init__(self, id_: str):
        super().__init__(id_)
        # params
        self.min_duration: Optional[float] = None
        self.energy_coef: Optional[float] = None

    def compute_energy_coef(self, point: Point3D, payload_weight: float, robot: Robot, nn: PositionNN):
        """
        Computes static activity energy coefficient using given input parameters and neural network.
        """
        position = Position(point, payload_weight, robot)
        self.energy_coef = nn.estimate(position)

    def __str__(self):
        super_str = super().__str__()
        return 'static {}, PARAMS: d_min={}, e_c={}'.format(super_str, self.min_duration, self.energy_coef)

    def __repr__(self):
        return self.__str__()


class DynamicActivity(Activity):
    """
    Class for dynamic activity representation in ILP model.
    Adds storing of dynamic activity ILP parameters: movement type, minimal duration, maximal duration
    and piecewise-linearized energy consumption function.
    """
    def __init__(self, id_: str):
        super().__init__(id_)
        # params
        self.movement_type = 'unknown type'
        self.movement: Optional[Movement] = None
        self.min_duration: Optional[float] = None
        self.max_duration: Optional[float] = None
        self.energy_profile_lines: List[Line2D] = []

    def set_movement(self, movement):
        self.movement = movement

    def compute_min_max_duration(
        self,
        given_min: Optional[float],
        given_max: Optional[float],
        duration_nn: MovementDurationNN,
    ):
        estimates_min, estimated_max = 0, 0
        if given_min is None or given_max is None:
            estimates_min, estimated_max = duration_nn.estimate(self.movement)

        self.min_duration = given_min if given_min is not None else estimates_min
        self.max_duration = given_max if given_max is not None else estimated_max

    def compute_energy_profile(self, energy_nn: MovementEnergyNN):
        non_linear_coefs = energy_nn.estimate(self.movement)
        self.energy_profile_lines = piecewise_linearize(non_linear_coefs, self.min_duration, self.max_duration)

    def __str__(self):
        super_str = super().__str__()
        return '{} dynamic {}, PARAMS: d_min={}, d_max={}, lines={}'.format(
            self.movement_type, super_str, self.min_duration, self.max_duration, self.energy_profile_lines
        )

    def __repr__(self):
        return self.__str__()
