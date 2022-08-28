from typing import Tuple, List

from preprocessing.position import Position

PositionNNOutput = float
"""
Movement neural network produces an outputs 'p' which is a coefficient of a linear approximation of position
energy consumption.
"""

PositionNNTrainingData = Tuple[Position, PositionNNOutput]


# TODO
class PositionNN:
    """
    Neural network for approximation of position energy consumption.
    """
    def __init__(self, nn: str = ''):
        self.nn = nn

    def train(self, data: List[PositionNNTrainingData]):
        self.nn = 'Trained...'

    def get_nn(self) -> str:
        return self.nn

    def set_nn(self, nn: str):
        self.nn = nn

    def estimate(self, params: Position) -> PositionNNOutput:
        return 1
