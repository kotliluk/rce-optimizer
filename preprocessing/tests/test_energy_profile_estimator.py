from unittest import TestCase

from preprocessing.energy_profile_estimator import EnergyProfileEstimator
from preprocessing.robot import Robot
from utils.geometry_3d import Point3D


class TestEnergyProfileEstimator(TestCase):
    def test_default_estimator(self):
        params = [(0, 280), (20, 336)]
        default_estimator = EnergyProfileEstimator()

        for payload_weight, expected_q in params:
            with self.subTest():
                # arrange
                point = Point3D(300, 000, 100)
                robot = Robot("r", Point3D(0, 0, 0), 300, 500)
                # act
                result = default_estimator.estimate_idling(point, robot, payload_weight)
                # assert
                self.assertEqual(len(result), 1)
                self.assertAlmostEqual(result[0].q, expected_q)
