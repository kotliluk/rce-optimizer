from typing import List

from preprocessing.movement import Movement
from preprocessing.robot import Robot
from utils.geometry_2d import Line2D
from utils.geometry_3d import Point3D, null_z_distance


class EnergyProfileEstimator:
    """
    Estimator of energy profiles for movements and idling.
    Stores parameters which can be modified.
    """
    def __init__(
        self,
        c_robot_weight_coef: float = (1/100)*(1/3),
        c_payload_weight_coef: float = (1/100),
        i_closest: float = 250.0,
        i_furthest: float = 300.0,
    ):
        # common parameters
        self.c_robot_weight_coef = c_robot_weight_coef
        self.c_payload_weight_coef = c_payload_weight_coef
        # idling parameters
        self.i_closest = i_closest
        self.i_furthest = i_furthest

    def estimate_movement(self, movement: Movement) -> List[Line2D]:
        """
        Computes piece-wise linearization of the given movement.
        """
        # TODO
        return []

    def estimate_idling(self, point: Point3D, robot: Robot, payload_weight: float) -> List[Line2D]:
        """
        Computes piece-wise linearization of idling in the given point.

        Used parameters:
        - c_robot_weight_coef (default 1/300)
        - c_payload_weight_coef (default 1/100)
        - i_closest (default 250)
        - i_furthest (default 300)
        """

        '''
        Idea:
        In experiments, the static consumption close to the robot axis was 275 W and far was 298 W.
        We simplify it to consumption of "i_closest" W in axis and "i_furthest" W in maximum reach.
        We compute relative weight (using robot and payload weight and their coefficients parameters). 
        '''
        relative_weight = robot.weight * self.c_robot_weight_coef + payload_weight * self.c_payload_weight_coef
        relative_distance = null_z_distance(robot.axis, point) / robot.maximum_reach
        q = relative_weight * (self.i_closest + relative_distance * (self.i_furthest - self.i_closest))
        return [Line2D(q, 0.0)]
