from utils.geometry_3d import Point3D


class Robot:
    def __init__(self, rId: str, axis: Point3D):
        """
        Creates a new robot.

        :param rId: id of the robot
        :param axis: 3D coordinates of the robot axis (in millimeters)
        """
        self.id = rId
        self.axis = axis

    def __str__(self):
        return 'Robot {} (axis: {})'.format(self.id, self.axis)

    def __repr__(self):
        return self.__str__()
