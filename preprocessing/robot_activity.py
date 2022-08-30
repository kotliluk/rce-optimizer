from preprocessing.robot import Robot
from utils.geometry_3d import Point3D
from utils.unsupported_parameter_error import UnsupportedParameterError


class RobotActivity:
    def __init__(self, mass: float, robot: Robot):
        """
        Creates a new robot activity with a payload.

        :param mass: payload mass during the activity in kilograms
        :param robot: robot of the activity
        """
        self._mass = mass
        self.robot = robot

    def mass(self) -> float:
        """
        Returns payload mass (in kilograms).
        """
        return self._mass

    def max_load(self) -> float:
        """
        Returns robots maximum possible payload mass (in kilograms).
        """
        return self.robot.load_capacity

    def load_ratio(self) -> float:
        """
        Returns ratio of actual payload mass and maximum possible robot load.
        """
        return self._mass / self.robot.load_capacity

    def robot_weight(self) -> float:
        """
        Returns robot weight (in kilograms).
        """
        return self.robot.weight

    def input_power(self) -> float:
        """
        Returns robot input power.
        """
        return self.robot.input_power

    def axis(self) -> Point3D:
        """
        Returns robot axis position (as 3D coordinates in millimeters).
        """
        return self.robot.axis

    def get_nn_param(self, param: str) -> float:
        """
        Returns given parameter value. Raises UnsupportedParameterError if the parameter is not supported.
        """
        if param == 'mass':
            return self.mass()
        if param == 'max_load':
            return self.max_load()
        if param == 'load_ratio':
            return self.load_ratio()
        if param == 'robot_weight':
            return self.robot_weight()
        if param == 'input_power':
            return self.input_power()
        raise UnsupportedParameterError('Parameter {} is not supported by Movement class'.format(param))
