from utils.geometry_3d import Point3D


class Robot:
    def __init__(self, rId: str, axis: Point3D, weight: float, load_capacity: float, input_power: float):
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
