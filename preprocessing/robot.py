from utils.geometry_3d import Point3D


class Robot:
    def __init__(self, rId: str, axis: Point3D, weight: float, load_capacity: float, input_power: float):
        """
        Creates a new robot.

        :param rId: id of the robot
        :param axis: 3D coordinates of the robot axis (in millimeters)
        :param weight: robot weight (in kilograms)
        :param load_capacity: maximum load capacity of the robot (in kilograms)
        :param input_power: input power of the robot (in Watts)
        """
        self.id = rId
        self.axis = axis
        self.weight = weight
        self.load_capacity = load_capacity
        self.input_power = input_power

    def __str__(self):
        return 'Robot {} (axis: {}, weight: {}, capacity: {}, input power: {})'.format(
            self.id, self.axis, self.weight, self.load_capacity, self.input_power
        )

    def __repr__(self):
        return self.__str__()
