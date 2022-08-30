import utils.geometry_3d as g3d
from preprocessing.robot import Robot
from preprocessing.robot_activity import RobotActivity
from utils.geometry_3d import Point3D


class Position(RobotActivity):
    def __init__(self, position: Point3D, mass: float, robot: Robot):
        """
        Creates a new position.

        :param position: 3D coordinates in millimeters
        :param mass: payload mass at the position in kilograms
        :param robot: robot of the position
        """
        super().__init__(mass, robot)
        self.position = position
        self._distance_from_axis = None

    def distance_from_axis(self) -> float:
        """
        Computes distance from axis to movement (in millimeters).
        Uses 2D projection, i.e. only 'x' and 'y' coordinates.
        """
        if self._distance_from_axis is None:
            projected_axis = g3d.null_z(self.axis())
            projected_position = g3d.null_z(self.position)
            self._distance_from_axis = g3d.distance(projected_axis, projected_position)

        return self._distance_from_axis

    def gravitational_torque(self) -> float:
        """
        Return simplified gravitational torque to the payload at the position (in millimeters * kilograms).
        """
        return self.distance_from_axis() * self._mass

    def get_nn_param(self, param: str) -> float:
        """
        Returns given parameter value. Raises UnsupportedParameterError if the parameter is not supported.
        """
        if param == 'distance_from_axis':
            return self.distance_from_axis()
        if param == 'gravitational_pseudo_torque':
            return self.gravitational_torque()
        return super().get_nn_param(param)
