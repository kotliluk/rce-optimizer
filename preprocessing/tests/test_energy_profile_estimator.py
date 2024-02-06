from unittest import TestCase

from preprocessing.energy_profile_estimator import EnergyProfileEstimator
from preprocessing.robot import Robot
from utils.geometry_3d import Point3D


class TestEnergyProfileEstimator(TestCase):
    def test_default_idling_estimator(self):
        params = [
            (500, 0, 0, 448.425),
            (1750, 0, 250, 479.373),
        ]
        default_estimator = EnergyProfileEstimator()

        for x, y, z, expected_q in params:
            with self.subTest():
                # arrange
                point = Point3D(x, y, z)
                robot = Robot("r", Point3D(0, 0, 0), 300, 500)
                # act
                result = default_estimator.estimate_idling(point, robot, 0.0)
                # assert
                self.assertEqual(len(result), 1)
                self.assertAlmostEqual(result[0].q, expected_q, places=1)
