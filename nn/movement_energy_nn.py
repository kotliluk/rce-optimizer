from typing import Tuple, List

from preprocessing.movement import Movement

MovementEnergyNNOutput = Tuple[float, float, float, float]
"""
Movement neural network produces 4 outputs 'a', 'b', 'c', 'd' which are coefs for a polynomial approximation
of movement energy consumption.
"""

MovementEnergyNNTrainingData = Tuple[Movement, MovementEnergyNNOutput]


# TODO
class MovementEnergyNN:
    """
    Neural network for polynomial approximation of movement energy consumption.
    """
    def __init__(self, nn: str = ''):
        self.nn = nn

    def train(self, data: List[MovementEnergyNNTrainingData]):
        self.nn = 'Trained...'

    def get_nn(self) -> str:
        return self.nn

    def set_nn(self, nn: str):
        self.nn = nn

    def estimate(self, movement: Movement) -> MovementEnergyNNOutput:
        return 6, 0, 1, 1
