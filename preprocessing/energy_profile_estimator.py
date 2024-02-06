from typing import List, Dict

from numpy import sqrt

from preprocessing.energy_profile_parameters import DIR_TYPES, DEFAULT_PARAMETERS_MANUAL, merge_parameters, \
    EnergyProfileParameters
from preprocessing.movement import Movement
from preprocessing.robot import Robot
from utils.geometry_2d import Line2D, Point2D, line_through_points
from utils.geometry_3d import Point3D, null_z_distance


def _get_dir_type_ratios(movement: Movement) -> Dict:
    length = movement.length()

    type_ratios = {
        'side': movement.side_distance() / length,
        'into_dist': max(movement.far_distance(), 0) / length,
        'from_afar': max(-movement.far_distance(), 0) / length,
        'up': max(movement.height_change(), 0) / length,
        'down': max(-movement.height_change(), 0) / length,
    }

    return type_ratios


def _estimate_movement_energy_for_duration(params: Dict[str, float], movement: Movement, dir_ratios: Dict) -> float:
    base_factor = params['base']

    type_factor = sqrt(
        sum(map(
            lambda d: (dir_ratios[d] * params[f'type_factor__{d}']) ** 2,
            DIR_TYPES,
        ))
    )

    def l_c(d, c):
        return params[f'length_coef__{d}__{c}']

    length = movement.length()
    length_factor = sqrt(
        sum(map(
            lambda d: (dir_ratios[d] * (l_c(d, 'A') * length * length + l_c(d, 'B') * length + l_c(d, 'C'))) ** 2,
            DIR_TYPES,
        ))
    )

    def a_d_c(d, c):
        return params[f'avg_dist_coef__{d}__{c}']

    a_d = movement.avg_distance_from_axis()
    avg_dist_factor = sqrt(
        sum(map(
            lambda d: (dir_ratios[d] * (a_d_c(d, 'A') * a_d * a_d + a_d_c(d, 'B') * a_d + a_d_c(d, 'C'))) ** 2,
            DIR_TYPES,
        ))
    )

    def a_h_c(d, c):
        return params[f'avg_height_coef__{d}__{c}']

    a_h = movement.avg_height()
    avg_height_factor = sqrt(
        sum(map(
            lambda d: (dir_ratios[d] * (a_h_c(d, 'A') * a_h * a_h + a_h_c(d, 'B') * a_h + a_h_c(d, 'C'))) ** 2,
            DIR_TYPES,
        ))
    )

    return base_factor * type_factor * length_factor * avg_dist_factor * avg_height_factor


class EnergyProfileEstimator:
    """
    Estimator of energy profiles for movements and idling. Stores params which can be modified.
    Uses custom parameters if given, otherwise uses default parameters.
    """
    def __init__(self, custom_params: Dict = None, default_params: EnergyProfileParameters = None):
        if default_params is None:
            default_params = DEFAULT_PARAMETERS_MANUAL

        self.parameters = merge_parameters(custom_params, default_params)

    def estimate_movement(self, movement: Movement, min_dur: float, max_dur: float) -> List[Line2D]:
        """
        Computes piece-wise linearization of the given movement with the given minimal and maximal duration.
        """
        dir_ratios = _get_dir_type_ratios(movement)

        min_dur = min_dur
        min_dur_energy = _estimate_movement_energy_for_duration(
            self.parameters['movement']['min_duration'], movement, dir_ratios,
        )
        
        opt_dur_ratio = _estimate_movement_energy_for_duration(
            self.parameters['movement']['opt_duration'], movement, dir_ratios,
        )
        opt_dur = min_dur * opt_dur_ratio
        opt_dur_energy = 0

        max_dur = max_dur
        max_dur_energy = _estimate_movement_energy_for_duration(
            self.parameters['movement']['max_duration'], movement, dir_ratios,
        )

        left_opt_dur_shift = self.parameters['movement']['opt_duration']['left_dur_shift']
        min_left_opt_dur_ratio = self.parameters['movement']['opt_duration']['min_left_dur_ratio']
        left_opt_dur = max(left_opt_dur_shift * opt_dur, min_left_opt_dur_ratio * min_dur)
        right_opt_dur_shift = self.parameters['movement']['opt_duration']['right_dur_shift']
        min_right_opt_dur_ratio = self.parameters['movement']['opt_duration']['min_right_dur_ratio']
        right_opt_dur = max(right_opt_dur_shift * opt_dur, min_right_opt_dur_ratio * min_dur)

        min_point = Point2D(min_dur, min_dur_energy)
        opt_left_point = Point2D(left_opt_dur, opt_dur_energy)
        opt_right_point = Point2D(right_opt_dur, opt_dur_energy)
        max_point = Point2D(max_dur, max_dur_energy)

        return [
            line_through_points(min_point, opt_left_point),
            Line2D(0.0, 0.0),  # line through opt_left and opt_right points (both have 0.0 y value)
            line_through_points(opt_right_point, max_point),
        ]

    def estimate_idling(self, point: Point3D, robot: Robot, payload_weight: float) -> List[Line2D]:
        """
        Computes piece-wise linearization of idling in the given point.
        """
        # robot_weight_coef = self.parameters['common']['robot_weight_coef']
        # payload_weight_coef = self.parameters['common']['payload_weight_coef']
        # relative_weight = robot.weight * robot_weight_coef + payload_weight * payload_weight_coef
        d = null_z_distance(robot.axis, point)
        h = point.z
        base = self.parameters['idling']['base']
        dist_a = self.parameters['idling']['dist_coef__A']
        dist_b = self.parameters['idling']['dist_coef__B']
        dist_c = self.parameters['idling']['dist_coef__C']
        height_a = self.parameters['idling']['height_coef__A']
        height_b = self.parameters['idling']['height_coef__B']
        height_c = self.parameters['idling']['height_coef__C']
        q = base * (dist_a * d * d + dist_b * d + dist_c) * (height_a * h * h + height_b * h + height_c)
        return [Line2D(q, 0.0)]
