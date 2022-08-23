from typing import Tuple, List

from nn.movement_energy_nn import MovementNNParams

MovementDurationNNOutput = Tuple[float, float]
"""
Movement duration neural network produces 2 outputs 'min', 'max' which are approximate minimal and maximal durations
of a movement.
"""

MovementDurationNNLearningData = Tuple[MovementNNParams, MovementDurationNNOutput]


# TODO
class MovementDurationNN:
    """
    Neural network for approximation of minimal and maximal duration of a movement.
    """
    def __init__(self, nn: str = ''):
        self.nn = nn

    def learn(self, data: List[MovementDurationNNLearningData]):
        self.nn = 'Learnt...'

    def get_nn(self) -> str:
        return self.nn

    def set_nn(self, nn: str):
        self.nn = nn

    def estimate(self, params: MovementNNParams) -> MovementDurationNNOutput:
        return 1, 10
