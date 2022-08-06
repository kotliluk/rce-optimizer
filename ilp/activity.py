from typing import Optional, List

import gurobipy as g

from nn.movement_duration_nn import MovementDurationNN
from nn.movement_energy_nn import MovementEnergyNN
from nn.position_nn import PositionNN
from preprocessing.movement import LinearMovement, JointMovement, SimpleMovement, CompoundMovement, Movement
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
        # params
        self.is_initial = False
        # vars
        self.start_time: Optional[g.Var] = None
        self.duration: Optional[g.Var] = None
        self.energy: Optional[g.Var] = None

    def solution_json_dict(self):
        """
        Saves activity id and variables in a dictionary ready to be saved in a JSON file.
        """
        return {
            'id': self.id,
            'start_time': self.start_time.x,
            'duration': self.duration.x,
            'energy': self.energy.x,
        }

    def __str__(self):
        return 'activity "{}"{}, VARS: s={}, d={}, e={}'.format(
            self.id,
            ' (initial)' if self.is_initial else '',
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
        self.energy_coef = nn.estimate(position.to_nn_params())

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
        self.min_duration: Optional[float] = None
        self.max_duration: Optional[float] = None
        self.energy_profile_lines: List[Line2D] = []

    def compute_linear_energy_profile(
        self,
        start: Point3D,
        end: Point3D,
        payload_weight: float,
        robot: Robot,
        energy_nn: MovementEnergyNN,
        duration_nn: MovementDurationNN,
    ):
        """
        Computes linear dynamic activity piecewise-linearized energy consumption function using given input parameters
        and neural network.
        """
        self.movement_type = 'linear'
        movement = LinearMovement(start, end, payload_weight, robot)
        self._compute_energy_profile(movement, energy_nn, duration_nn)

    def compute_joint_energy_profile(
        self,
        start: Point3D,
        end: Point3D,
        payload_weight: float,
        robot: Robot,
        energy_nn: MovementEnergyNN,
        duration_nn: MovementDurationNN,
    ):
        """
        Computes joint dynamic activity piecewise-linearized energy consumption function using given input parameters
        and neural network.
        """
        self.movement_type = 'joint'
        movement = JointMovement(start, end, payload_weight, robot)
        self._compute_energy_profile(movement, energy_nn, duration_nn)

    def compute_compound_energy_profile(
        self,
        partial_movements: List[SimpleMovement],
        payload_weight: float,
        robot: Robot,
        energy_nn: MovementEnergyNN,
        duration_nn: MovementDurationNN,
    ):
        """
        Computes compound dynamic activity piecewise-linearized energy consumption function using given input parameters
        and neural network.
        """
        self.movement_type = 'compound'
        movement = CompoundMovement(partial_movements, payload_weight, robot)
        self._compute_energy_profile(movement, energy_nn, duration_nn)

    def _compute_energy_profile(self, movement: Movement, energy_nn: MovementEnergyNN, duration_nn: MovementDurationNN):
        nn_params = movement.to_nn_params()
        non_linear_coefs = energy_nn.estimate(nn_params)

        approximate_duration = 1, 10
        if self.min_duration is None or self.min_duration is None:
            approximate_duration = duration_nn.estimate(nn_params)

        min_duration = self.min_duration if self.min_duration is not None else approximate_duration[0]
        max_duration = self.max_duration if self.max_duration is not None else approximate_duration[1]
        self.energy_profile_lines = piecewise_linearize(non_linear_coefs, min_duration, max_duration)

    def __str__(self):
        super_str = super().__str__()
        return '{} dynamic {}, PARAMS: d_min={}, d_max={}, lines={}'.format(
            self.movement_type, super_str, self.min_duration, self.max_duration, self.energy_profile_lines
        )

    def __repr__(self):
        return self.__str__()
