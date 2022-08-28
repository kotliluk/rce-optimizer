from typing import Tuple, List

from preprocessing.movement import Movement

MovementDurationNNOutput = Tuple[float, float]
"""
Movement duration neural network produces 2 outputs 'min', 'max' which are approximate minimal and maximal durations
of a movement.
"""

MovementDurationNNTrainingData = Tuple[Movement, MovementDurationNNOutput]


# TODO
class MovementDurationNN:
    """
    Neural network for approximation of minimal and maximal duration of a movement.
    """
    def __init__(self, nn: str = ''):
        self.nn = nn

    def train(self, data: List[MovementDurationNNTrainingData]):
        self.nn = 'Trained...'

    def get_nn(self) -> str:
        return self.nn

    def set_nn(self, nn: str):
        self.nn = nn

    def estimate(self, movement: Movement) -> MovementDurationNNOutput:
        return 1, 10
