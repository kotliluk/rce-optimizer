from typing import Tuple, List


MovementNNParams = Tuple[float, float, float, float, float, float, float, float, float, float]
"""
Movement neural network expects 10 inputs:

- movement_length = 3D distance between start and end
- height_change = vertical distance between start and end
- horizontal_angle = horizontal angular change between of start and end (after 2D projection to x-y plate)
- vertical_angle = vertical angular change between start and end
- average_distance = average distance between a point on a trajectory and axis
- mass = mass of the payload
- load_ratio = ratio of mass and robot load capacity
- robot_weight = weight of the robot
- gravitational_pseudo_torque = approximate torque affecting vertically (average_distance * mass)
- input_power = input power of the robot
"""

MovementNNOutput = Tuple[float, float, float, float]
"""
Movement neural network produces 4 outputs 'a', 'b', 'c', 'd' which are coefs for a polynomial approximation
of movement energy consumption.
"""

MovementNNLearningData = Tuple[MovementNNParams, MovementNNOutput]


# TODO
class MovementNN:
    def __init__(self, nn: str = ''):
        self.nn = nn

    def learn(self, data: List[MovementNNLearningData]):
        self.nn = 'Learnt...'

    def get_nn(self) -> str:
        return self.nn

    def set_nn(self, nn: str):
        self.nn = nn

    def estimate(self, params: MovementNNParams) -> MovementNNOutput:
        return 6, 0, 1, 1
