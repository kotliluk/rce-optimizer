from abc import abstractmethod, ABC

from numpy import sqrt, abs, sin
from scipy.integrate import quad as integral

import utils.geometry_3d as g3d
from preprocessing.robot import Robot
from utils.geometry_3d import Point3D


class Movement:
    def __init__(self, start: Point3D, end: Point3D, robot: Robot):
        self.robot = robot
        self.start = start
        self.end = end

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

    def gravitational_torque(self) -> float:
        """
        Return simplified average gravitational torque to the payload during the movement (in millimeters * kilograms).
        """
        return self.avg_distance_from_axis() * 1

    def start_distance(self):
        """
        Returns payload distance from robot axis at the beginning of the movement (in millimeters).
        """
        projected_axis = g3d.null_z(self.axis())
        projected_start = g3d.null_z(self.start)
        return g3d.distance(projected_axis, projected_start)

    def end_distance(self):
        """
        Returns payload distance from robot axis at the end of the movement (in millimeters).
        """
        projected_axis = g3d.null_z(self.axis())
        projected_end = g3d.null_z(self.end)
        return g3d.distance(projected_axis, projected_end)

    def margin_distance(self):
        """
        Returns average payload distance from robot axis at the beginning and at the end of the movement
        (in millimeters).
        """
        return (self.start_distance() + self.end_distance()) / 2


class SimpleMovement(Movement, ABC):
    """
    Linear or joint movement. Can be used as a partial movement in CompoundMovement.
    """

    def __init__(self, start: Point3D, end: Point3D, robot: Robot):
        """
        Creates a new simple movement.

        :param start: starting 3D coordinates in millimeters
        :param end: ending 3D coordinates in millimeters
        :param robot: robot of the movement
        """
        super().__init__(start, end, robot)
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


class JointMovement(SimpleMovement):
    def __init__(self, start: Point3D, end: Point3D, robot: Robot):
        """
        Creates a new joint movement.

        :param start: starting 3D coordinates in millimeters
        :param end: ending 3D coordinates in millimeters
        :param robot: robot of the movement
        """
        super().__init__(start, end, robot)
        self._length = None
        self._avg_distance_from_axis = None

    def length(self) -> float:
        if self._length is None:
            start_dist = g3d.distance(self.axis(), self.start)
            end_dist = g3d.distance(self.axis(), self.end)
            horizontal_angle = self.horizontal_angle()
            start_angle = self.start_vertical_angle()
            signed_vertical_angle = self.signed_vertical_angle()

            def spherical_form_movement_length(t):
                """
                Movement parametrized in spherical form, i.e. t = r*sin(theta)*cos(phi), y = r*sin(theta)*sin(phi),
                z = r*cos(theta) (where r, theta and phi are functions of t, 0 <= t <= 1) and transformed to
                length relation.
                """
                r = (start_dist + (end_dist - start_dist) * t)
                r_t_derivative = end_dist - start_dist
                sin_theta = sin(start_angle + signed_vertical_angle * t)
                phi_t_derivative = horizontal_angle
                theta_t_derivative = signed_vertical_angle
                return sqrt(r_t_derivative**2 + sin_theta**2 * phi_t_derivative**2 + r**2 * theta_t_derivative**2)

            self._length = integral(spherical_form_movement_length, 0, 1)[0]

        return self._length

    def avg_distance_from_axis(self) -> float:
        if self._avg_distance_from_axis is None:
            projected_axis = g3d.null_z(self.axis())
            projected_start = g3d.null_z(self.start)
            projected_end = g3d.null_z(self.end)
            self._avg_distance_from_axis = (g3d.distance(projected_axis, projected_start) +
                                           g3d.distance(projected_start, projected_end)) / 2

        return self._avg_distance_from_axis

    def __str__(self):
        return 'Joint movement from {} to {} of robot {}'.format(self.start, self.end, self.robot.id)

    def __repr__(self):
        return self.__str__()


if __name__ == '__main__':
    def joint_length_test():
        sqrt2inv = 1 / sqrt(2)
        axis = Point3D(0, 0, 0)
        # start = Point3D(0, -sqrt2inv, -sqrt2inv)
        # end = Point3D(0, sqrt2inv, sqrt2inv)
        # start = Point3D(-sqrt2inv, 0, -sqrt2inv)
        # end = Point3D(sqrt2inv, 0, sqrt2inv)
        # start = Point3D(-sqrt2inv, -sqrt2inv, 0)
        # end = Point3D(sqrt2inv, sqrt2inv, 0)
        # start = Point3D(0, 0, 1)
        # end = Point3D(0, 0, -1)
        start = Point3D(0, sqrt2inv, sqrt2inv)
        end = Point3D(0, -sqrt2inv, sqrt2inv)
        # start = Point3D(1, 0, 0)
        # end = Point3D(-1, 0, 0)
        robot = Robot('r_1', axis)
        joint = JointMovement(start, end, robot)
        print(joint.length())

    joint_length_test()
