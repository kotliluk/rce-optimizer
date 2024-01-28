from abc import abstractmethod, ABC

from numpy import abs

import utils.geometry_2d as g2d
import utils.geometry_3d as g3d
from preprocessing.robot import Robot
from utils.geometry_3d import Point3D


class Movement:
    def __init__(self, start: Point3D, end: Point3D, robot: Robot, payload_weight: float = 0.0):
        self.start = start
        self.end = end
        self.robot = robot
        self.payload_weight = payload_weight
        self._side_distance = None
        self._far_distance = None

    def axis(self) -> Point3D:
        """
        Returns robot axis position (as 3D coordinates in millimeters).
        """
        return self.robot.axis

    @abstractmethod
    def length(self) -> float:
        """
        Computes movement length (in millimeters).
        """
        pass

    def height_change(self) -> float:
        """
        Computes signed height change (change of 'z' coordinate) (in millimeters).
        """
        return self.end.z - self.start.z

    @abstractmethod
    def horizontal_angle(self) -> float:
        """
        Computes overall movement horizontal (i.e. after projection to x-y plate) angular change (in radians)
        with respect to axis as a base point.
        """
        pass

    @abstractmethod
    def vertical_angle(self) -> float:
        """
        Computes overall movement vertical angular change (in radians) with respect to axis as a base point.
        """
        pass

    @abstractmethod
    def avg_distance_from_axis(self) -> float:
        """
        Computes average distance from axis to movement (in millimeters).
        Uses 2D projection, i.e. only 'x' and 'y' coordinates.
        """
        pass

    @abstractmethod
    def avg_height(self) -> float:
        """
        Computes average height of the movement (in millimeters).
        """
        pass

    def side_distance(self) -> float:
        """
        Returns distance of the start and end points of the movement after their projection on perpendicular
        to the line from robot axis to the movement center.
        """
        if self._side_distance is None:
            start_2d = self.start.to_2d()
            axis_2d = self.axis().to_2d()
            center_2d = g3d.center(self.start, self.end).to_2d()
            axis_center_line = g2d.line_through_points(axis_2d, center_2d)
            self._side_distance = 2 * axis_center_line.distance_to_point(start_2d)

        return self._side_distance

    def far_distance(self) -> float:
        """
        Returns signed (positive = movement into distance, negative = movement from afar) distance of the start
        and end points of the movement after their projection on the line from robot axis to the movement center.
        """
        if self._far_distance is None:
            start_2d = self.start.to_2d()
            axis_2d = self.axis().to_2d()
            center_2d = g3d.center(self.start, self.end).to_2d()
            axis_center_line = g2d.line_through_points(axis_2d, center_2d)
            closest_to_start = axis_center_line.closest_point(start_2d)
            center_distance = g2d.distance(axis_2d, center_2d)
            closest_to_start_distance = g2d.distance(axis_2d, closest_to_start)
            self._far_distance = 2 * (center_distance - closest_to_start_distance)

        return self._far_distance

    def gravitational_torque(self) -> float:
        """
        Return simplified average gravitational torque to the payload during the movement (in millimeters * kilograms).
        """
        return self.avg_distance_from_axis() * 1

    def start_distance(self) -> float:
        """
        Returns payload distance from robot axis at the beginning of the movement (in millimeters).
        """
        return g3d.null_z_distance(self.axis(), self.start)

    def end_distance(self) -> float:
        """
        Returns payload distance from robot axis at the end of the movement (in millimeters).
        """
        return g3d.null_z_distance(self.axis(), self.end)

    def margin_distance(self) -> float:
        """
        Returns average payload distance from robot axis at the beginning and at the end of the movement
        (in millimeters).
        """
        return (self.start_distance() + self.end_distance()) / 2


class SimpleMovement(Movement, ABC):
    """
    Linear or joint movement. Can be used as a partial movement in CompoundMovement.
    """

    def __init__(self, start: Point3D, end: Point3D, robot: Robot, payload_weight: float = 0.0):
        """
        Creates a new simple movement.

        :param start: starting 3D coordinates in millimeters
        :param end: ending 3D coordinates in millimeters
        :param robot: robot of the movement
        """
        super().__init__(start, end, robot, payload_weight)
        self._start_vertical_angle = None
        self._end_vertical_angle = None
        self._horizontal_angle = None
        self._signed_vertical_angle = None

    def start_vertical_angle(self) -> float:
        """
        Returns starting angle relative to vertical line (z-axis).
        """
        if self._start_vertical_angle is None:
            top_vector = Point3D(0, 0, 1)
            self._start_vertical_angle = g3d.angle(top_vector, self.start - self.axis())

        return self._start_vertical_angle

    def end_vertical_angle(self) -> float:
        """
        Returns ending angle relative to vertical line (z-axis).
        """
        if self._end_vertical_angle is None:
            top_vector = Point3D(0, 0, 1)
            self._end_vertical_angle = g3d.angle(top_vector, self.end - self.axis())

        return self._end_vertical_angle

    def horizontal_angle(self) -> float:
        """
        Returns absolute horizontal angular change.
        """
        if self._horizontal_angle is None:
            start_vector = g3d.null_z(self.start - self.axis())
            end_vector = g3d.null_z(self.end - self.axis())
            if start_vector.is_zero() or end_vector.is_zero():
                self._horizontal_angle = 0
            else:
                self._horizontal_angle = g3d.angle(start_vector, end_vector)

        return self._horizontal_angle

    def signed_vertical_angle(self) -> float:
        """
        Returns signed vertical angular change - positive when going down, negative when going up.
        """
        if self._signed_vertical_angle is None:
            self._signed_vertical_angle = self.end_vertical_angle() - self.start_vertical_angle()

        return self._signed_vertical_angle

    def vertical_angle(self) -> float:
        """
        Returns absolute vertical angular change.
        """
        return abs(self.signed_vertical_angle())


# TODO - use joint movement as PTP?
class PTPMovement(SimpleMovement):
    def __init__(self, start: Point3D, end: Point3D, robot: Robot, payload_weight: float = 0.0):
        """
        Creates a new PTP movement.

        :param start: starting 3D coordinates in millimeters
        :param end: ending 3D coordinates in millimeters
        :param robot: robot of the movement
        """
        super().__init__(start, end, robot, payload_weight)
        self._length = None
        self._avg_distance_from_axis = None

    def length(self) -> float:
        if self._length is None:
            self._length = g3d.distance(self.start, self.end)

        return self._length

    def avg_distance_from_axis(self) -> float:
        if self._avg_distance_from_axis is None:
            center = g3d.center(self.start, self.end)
            self._avg_distance_from_axis = g3d.null_z_distance(self.axis(), center)

        return self._avg_distance_from_axis

    def avg_height(self) -> float:
        return (self.start.z + self.end.z) / 2

    def __str__(self):
        return 'PTP movement from {} to {} of robot {}'.format(self.start, self.end, self.robot.id)

    def __repr__(self):
        return self.__str__()


# TODO - fix and test
# class JointMovement(SimpleMovement):
#     def __init__(self, start: Point3D, end: Point3D, robot: Robot, payload_weight: float = 0.0):
#         """
#         Creates a new joint movement.
#
#         :param start: starting 3D coordinates in millimeters
#         :param end: ending 3D coordinates in millimeters
#         :param robot: robot of the movement
#         """
#         super().__init__(start, end, robot, payload_weight)
#         self._length = None
#         self._avg_distance_from_axis = None
#
#     def length(self) -> float:
#         if self._length is None:
#             start_dist = g3d.distance(self.axis(), self.start)
#             end_dist = g3d.distance(self.axis(), self.end)
#             horizontal_angle = self.horizontal_angle()
#             start_angle = self.start_vertical_angle()
#             signed_vertical_angle = self.signed_vertical_angle()
#
#             def spherical_form_movement_length(t):
#                 """
#                 Movement parametrized in spherical form, i.e. t = r*sin(theta)*cos(phi), y = r*sin(theta)*sin(phi),
#                 z = r*cos(theta) (where r, theta and phi are functions of t, 0 <= t <= 1) and transformed to
#                 length relation.
#                 """
#                 r = (start_dist + (end_dist - start_dist) * t)
#                 r_t_derivative = end_dist - start_dist
#                 sin_theta = sin(start_angle + signed_vertical_angle * t)
#                 phi_t_derivative = horizontal_angle
#                 theta_t_derivative = signed_vertical_angle
#                 return sqrt(r_t_derivative**2 + sin_theta**2 * phi_t_derivative**2 + r**2 * theta_t_derivative**2)
#
#             self._length = integral(spherical_form_movement_length, 0, 1)[0]
#
#         return self._length
#
#     def avg_distance_from_axis(self) -> float:
#         if self._avg_distance_from_axis is None:
#             self._avg_distance_from_axis = (g3d.null_z_distance(self.axis(), self.start) +
#                                             g3d.null_z_distance(self.axis(), self.end)) / 2
#
#         return self._avg_distance_from_axis
#
#     def __str__(self):
#         return 'Joint movement from {} to {} of robot {}'.format(self.start, self.end, self.robot.id)
#
#     def __repr__(self):
#         return self.__str__()
