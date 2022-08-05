from utils.geometry_3d import Point3D
import utils.geometry_3d as g3d
from preprocessing.robot import Robot
from nn.position_nn import PositionNNParams


class Position:
    def __init__(self, position: Point3D, mass: float, robot: Robot):
        self.position = position
        self._mass = mass
        self.robot = robot
        self._distance_from_axe = None

    def distance_from_axe(self) -> float:
        if self._distance_from_axe is None:
            projected_axis = g3d.null_z(self.axis())
            projected_position = g3d.null_z(self.position)
            self._distance_from_axe = g3d.distance(projected_axis, projected_position)

        return self._distance_from_axe

    def mass(self) -> float:
        return self._mass

    def load_ratio(self) -> float:
        return self._mass / self.robot.load_capacity

    def robot_weight(self) -> float:
        return self.robot.weight

    def gravitational_torque(self) -> float:
        return self.distance_from_axe() * self._mass

    def input_power(self) -> float:
        return self.robot.input_power

    def axis(self) -> Point3D:
        return self.robot.axis

    def to_nn_params(self) -> PositionNNParams:
        return (
            self.distance_from_axe(),
            self.mass(),
            self.load_ratio(),
            self.robot_weight(),
            self.gravitational_torque(),
            self.input_power()
        )
