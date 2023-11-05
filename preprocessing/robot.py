from utils.geometry_3d import Point3D


class Robot:
    def __init__(self, rId: str, axis: Point3D, weight: float, maximum_reach: float):
        """
        Creates a new robot.

        :param rId: id of the robot
        :param axis: 3D coordinates of the robot axis (in millimeters)
        :param weight: weight of the robot (in kilograms)
        :param maximum_reach: maximum reach of the robot (in millimeters)
        """
        self.id = rId
        self.axis = axis
        self.weight = weight
        self.maximum_reach = maximum_reach

    def __str__(self):
        return 'Robot {} (axis: {})'.format(self.id, self.axis)

    def __repr__(self):
        return self.__str__()
