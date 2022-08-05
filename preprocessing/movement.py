from abc import abstractmethod, ABC
from scipy.integrate import quad as integral
from numpy import sqrt, cos
from typing import List

from utils.geometry_3d import Point3D
import utils.geometry_3d as g3d
from preprocessing.robot import Robot
from nn.movement_nn import MovementNNParams


class Movement(ABC):
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

    def load_ratio(self) -> float:
        return self._mass / self.robot.load_capacity

    def robot_weight(self) -> float:
        return self.robot.weight

    def gravitational_torque(self) -> float:
        return self.avg_distance_from_axe() * self._mass

    def input_power(self) -> float:
        return self.robot.input_power

    def axis(self) -> Point3D:
        return self.robot.axis

    def to_nn_params(self) -> MovementNNParams:
        return (
            self.length(),
            self.height_change(),
            self.horizontal_angle(),
            self.vertical_angle(),
            self.avg_distance_from_axe(),
            self.mass(),
            self.load_ratio(),
            self.robot_weight(),
            self.gravitational_torque(),
            self.input_power()
        )


class SimpleMovement(Movement, ABC):
    """
    Implementation of common methods of linear and joint movements.
    """
    def __init__(self, start: Point3D, end: Point3D, mass: float, robot: Robot):
        super().__init__(start, end, mass, robot)
        self._horizontal_angle = None
        self._vertical_angle = None

    def horizontal_angle(self) -> float:
        if self._horizontal_angle is None:
            start_vector = g3d.null_z(self.start - self.axis())
            end_vector = g3d.null_z(self.end - self.axis())
            if start_vector.is_zero() or end_vector.is_zero():
                self._horizontal_angle = 0
            else:
                self._horizontal_angle = g3d.angle(start_vector, end_vector)

        return self._horizontal_angle

    def vertical_angle(self) -> float:
        if self._vertical_angle is None:
            start_vector = self.start - self.axis()
            end_vector = self.end - self.axis()
            start_magnitude = start_vector.magnitude()
            end_magnitude = end_vector.magnitude()
            projected_start = Point3D(sqrt(start_magnitude**2 - start_vector.z**2), 0, start_vector.z)
            projected_end = Point3D(sqrt(end_magnitude**2 - end_vector.z**2), 0, end_vector.z)
            self._vertical_angle = g3d.angle(projected_start, projected_end)

        return self._vertical_angle


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
            vertical_angle = self.vertical_angle()

            # TODO - does not work for:
            # sqrt2inv = 1 / sqrt(2)
            # start = Point3D(0, -sqrt2inv, -sqrt2inv)
            # end = Point3D(0, sqrt2inv, sqrt2inv)
            # or for
            # start = Point3D(-sqrt2inv, 0, -sqrt2inv)
            # end = Point3D(sqrt2inv, 0, sqrt2inv)
            # returns 3.3295836107826746 instead of 3.141592653589793
            # it works for
            # start = Point3D(-sqrt2inv, -sqrt2inv, 0)
            # end = Point3D(sqrt2inv, sqrt2inv, 0)

            def spherical_form_movement_length(t):
                """
                Movement parametrized in spherical form, i.e. x = r*sin(theta)*cos(phi), y = r*sin(theta)*sin(phi),
                z = r*cos(phi) (where r, theta and phi are functions of t, 0 <= t <= 1) and transformed to length relation.
                """
                r = (start_dist + (end_dist - start_dist) * t)
                r_t_derivative = end_dist - start_dist
                cos_theta = cos(horizontal_angle * t)
                phi_t_derivative = vertical_angle
                theta_t_derivative = horizontal_angle
                return sqrt(r_t_derivative**2 + r**2 * cos_theta**2 * phi_t_derivative**2 + r**2 * theta_t_derivative**2)

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
        # start = Point3D(1, 0, 0)
        # end = Point3D(-2, 0, 0)
        # start = Point3D(0, 1, 0)
        # end = Point3D(0, -1, 0)
        start = Point3D(0, 0, -1)
        end = Point3D(0, 0, 1)
        mass = 10.5
        load_capacity = 30.0
        robot_weight = 260.0
        input_power = 2000
        robot = Robot('r_1', axis, robot_weight, load_capacity, input_power)
        joint = JointMovement(start, end, mass, robot)
        print(joint.horizontal_angle())
        print(joint.vertical_angle())
        print(joint.length())
        # linear = LinearMovement(start, end, mass, robot)
        # print(linear.horizontal_angle())
        # print(linear.vertical_angle())
        # print(linear.length())

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

    # joint_length_test()
    compound_test()
