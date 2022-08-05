from typing import Tuple, List


PositionNNParams = Tuple[float, float, float, float, float, float]
"""
Position neural network expects 6 inputs:

- distance_from_axe = 2D distance between position and axis
- mass = mass of the payload
- load_ratio = ratio of mass and robot load capacity
- robot_weight = weight of the robot
- gravitational_pseudo_torque = approximate torque affecting vertically (distance_from_axe * mass)
- input_power = input power of the robot
"""

PositionNNOutput = float
"""
Movement neural network produces an  outputs 'p' which is a coefs of a linear approximation of position
energy consumption.
"""

PositionNNLearningData = Tuple[PositionNNParams, PositionNNOutput]


# TODO
class PositionNN:
    def __init__(self, nn: str = ''):
        self.nn = nn

    def learn(self, data: List[PositionNNLearningData]):
        self.nn = 'Learnt...'

    def get_nn(self) -> str:
        return self.nn

    def set_nn(self, nn: str):
        self.nn = nn

    def estimate(self, params: PositionNNParams) -> PositionNNOutput:
        return 1
