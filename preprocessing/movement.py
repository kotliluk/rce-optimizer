from abc import abstractmethod, ABC
from typing import List

from numpy import sqrt, abs, sin
from scipy.integrate import quad as integral

import utils.geometry_3d as g3d
from preprocessing.robot import Robot
from utils.geometry_3d import Point3D


class Movement(ABC):
    # TODO - return normalized params

    def __init__(self, start: Point3D, end: Point3D, mass: float, robot: Robot):
        self.start = start
        self.end = end
        self._mass = mass
        self.robot = robot

    @abstractmethod
    def length(self) -> float:
        """
        Computes movement length.
        """
        pass

    def height_change(self) -> float:
        """
        Computes signed height change (change of 'z' coordinate).
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
    def avg_distance_from_axe(self) -> float:
        """
        Computes average distance from axis to movement.
        Uses 2D projection, i.e. only 'x' and 'y' coordinates.
        """
        pass

    def mass(self) -> float:
        return self._mass

    def max_load(self) -> float:
        return self.robot.load_capacity

    def load_ratio(self) -> float:
        return self._mass / self.robot.load_capacity

    def robot_weight(self) -> float:
        return self.robot.weight

    def gravitational_torque(self) -> float:
        return self.avg_distance_from_axe() * self._mass

    def input_power(self) -> float:
        return self.robot.input_power

    def start_distance(self):
        projected_axis = g3d.null_z(self.axis())
        projected_start = g3d.null_z(self.start)
        return g3d.distance(projected_axis, projected_start)

    def end_distance(self):
        projected_axis = g3d.null_z(self.axis())
        projected_end = g3d.null_z(self.end)
        return g3d.distance(projected_axis, projected_end)

    def margin_distance(self):
        return (self.start_distance() + self.end_distance()) / 2

    def axis(self) -> Point3D:
        return self.robot.axis

    def get_nn_param(self, param: str) -> float:
        if param == 'movement_length':
            return self.length()
        if param == 'height_change':
            return self.height_change()
        if param == 'horizontal_angle':
            return self.horizontal_angle()
        if param == 'vertical_angle':
            return self.vertical_angle()
        if param == 'average_distance':
            return self.avg_distance_from_axe()
        if param == 'mass':
            return self.mass()
        if param == 'max_load':
            return self.max_load()
        if param == 'load_ratio':
            return self.load_ratio()
        if param == 'robot_weight':
            return self.robot_weight()
        if param == 'gravitational_pseudo_torque':
            return self.gravitational_torque()
        if param == 'input_power':
            return self.input_power()
        if param == 'start_distance':
            return self.start_distance()
        if param == 'end_distance':
            return self.end_distance()
        if param == 'margin_distance':
            return self.margin_distance()


class SimpleMovement(Movement, ABC):
    """
    Implementation of common methods of linear and joint movements.
    """
    def __init__(self, start: Point3D, end: Point3D, mass: float, robot: Robot):
        super().__init__(start, end, mass, robot)
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


class LinearMovement(SimpleMovement):
    def __init__(self, start: Point3D, end: Point3D, mass: float, robot: Robot):
        super().__init__(start, end, mass, robot)
        self._length = None
        self._avg_distance_from_axe = None

    def length(self) -> float:
        if self._length is None:
            self._length = g3d.distance(self.start, self.end)

        return self._length

    def avg_distance_from_axe(self) -> float:
        if self._avg_distance_from_axe is None:
            def parametrized_distance(t):
                """
                Distance between axis and parametrized definition of line segment.
                """
                x_part = (self.start.x + (self.end.x - self.start.x)*t - self.axis().x)**2
                y_part = (self.start.y + (self.end.y - self.start.y)*t - self.axis().y)**2
                return sqrt(x_part + y_part)

            self._avg_distance_from_axe = integral(parametrized_distance, 0, 1)[0]

        return self._avg_distance_from_axe

    def __str__(self):
        return 'Linear movement from {} to {} of robot {} with {}kg payload'.format(
            self.start, self.end, self.robot.id, self.mass()
        )

    def __repr__(self):
        return self.__str__()


class JointMovement(SimpleMovement):
    def __init__(self, start: Point3D, end: Point3D, mass: float, robot: Robot):
        super().__init__(start, end, mass, robot)
        self._length = None
        self._avg_distance_from_axe = None

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

    def avg_distance_from_axe(self) -> float:
        if self._avg_distance_from_axe is None:
            projected_axis = g3d.null_z(self.axis())
            projected_start = g3d.null_z(self.start)
            projected_end = g3d.null_z(self.end)
            self._avg_distance_from_axe = (g3d.distance(projected_axis, projected_start) +
                                           g3d.distance(projected_start, projected_end)) / 2

        return self._avg_distance_from_axe

    def __str__(self):
        return 'Joint movement from {} to {} of robot {} with {}kg payload'.format(
            self.start, self.end, self.robot.id, self.mass()
        )

    def __repr__(self):
        return self.__str__()


class CompoundMovement(Movement):
    def __init__(self, parts: List[SimpleMovement], mass: float, robot: Robot):
        assert len(parts) > 0

        super().__init__(parts[0].start, parts[-1].end, mass, robot)
        self._length = None
        self._horizontal_angle = None
        self._vertical_angle = None
        self._avg_distance_from_axe = None
        self._parts = parts

    def length(self) -> float:
        return sum(map(lambda part: part.length(), self._parts))

    def horizontal_angle(self) -> float:
        return sum(map(lambda part: part.horizontal_angle(), self._parts))

    def vertical_angle(self) -> float:
        return sum(map(lambda part: part.vertical_angle(), self._parts))

    def avg_distance_from_axe(self) -> float:
        return sum(map(lambda part: part.avg_distance_from_axe() * part.length(), self._parts)) / self.length()

    def __str__(self):
        a = 'Compound movement from {} to {} of robot {} with {}kg payload through points '.format(
            self.start, self.end, self.robot.id, self.mass()
        )
        b = ', '.join(map(lambda m: str(m.end), self._parts[:-1]))
        return a + b

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
        mass = 10.5
        load_capacity = 30.0
        robot_weight = 260.0
        input_power = 2000
        robot = Robot('r_1', axis, robot_weight, load_capacity, input_power)
        joint = JointMovement(start, end, mass, robot)
        print(joint.length())

    def compound_test():
        axis = Point3D(0, 0, 0)
        mass = 10.5
        load_capacity = 30.0
        robot_weight = 260.0
        input_power = 2000
        robot = Robot('r_1', axis, robot_weight, load_capacity, input_power)

        point_1 = Point3D(0, 1, 0)
        point_2 = Point3D(1, 1, 0)
        point_3 = Point3D(1, 0, 0)
        part_1 = JointMovement(point_1, point_2, mass, robot)
        part_2 = LinearMovement(point_2, point_3, mass, robot)
        compound_movement = CompoundMovement([part_1, part_2], mass, robot)

        print('length', compound_movement.length())
        print('height_change', compound_movement.height_change())
        print('horizontal_angle', compound_movement.horizontal_angle())
        print('vertical_angle', compound_movement.vertical_angle())
        print('avg_distance_from_axe', compound_movement.avg_distance_from_axe())
        print('mass', compound_movement.mass())
        print('load_ratio', compound_movement.load_ratio())
        print('robot_weight', compound_movement.robot_weight())
        print('gravitational_torque', compound_movement.gravitational_torque())
        print('input_power', compound_movement.input_power())
        print('axis', compound_movement.axis())

    joint_length_test()
    # compound_test()
