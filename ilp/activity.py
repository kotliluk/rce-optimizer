from typing import Optional, List

import gurobipy as g

from utils.geometry_2d import Line2D


class Activity:
    """
    Base class for activity representation in ILP model.
    It stores activity id, type and variables.
    """
    def __init__(self, activity_id: str, activity_type: str):
        self.id = activity_id
        self.type = activity_type
        self.prev: Optional[Activity] = None
        self.next: Optional[Activity] = None
        # vars
        self.start_time: Optional[g.Var] = None
        self.duration: Optional[g.Var] = None
        self.energy: Optional[g.Var] = None

    def is_first(self):
        """
        Returns whether the activity is the first one of its robot.
        """
        return self.prev is None

    def is_last(self):
        """
        Returns whether the activity is the last one of its robot.
        """
        return self.next is None

    def end_time(self):
        """
        Returns end time of the activity.
        """
        return self.start_time.x + self.duration.x

    def solution_json_dict(self):
        """
        Saves activity id and variables in a dictionary ready to be saved in a JSON file.
        """
        return {
            'id': self.id,
            'type': self.type,
            'start_time': round(self.start_time.x, 3),
            'duration': round(self.duration.x, 3),
            'end_time': round(self.end_time(), 3),
            'energy': round(self.energy.x, 6),
        }

    def gantt_chart_color(self):
        return 'b'

    def __str__(self):
        return 'activity "{}", VARS: s={}, d={}, e={}'.format(
            self.id,
            round(self.start_time.x, 3),
            round(self.duration.x, 3),
            round(self.energy.x, 3),
        )

    def __repr__(self):
        return self.__str__()


class IdleActivity(Activity):
    """
    Class for idle representation in ILP model.
    Adds storing of idle activity ILP parameters: piecewise-linearized energy consumption profile.
    """
    def __init__(self, activity_id: str):
        super().__init__(activity_id, 'IDLE')
        # params
        self.energy_profile_lines: List[Line2D] = []

    def set_energy_profile(self, energy_profile_lines: List[Line2D]):
        self.energy_profile_lines = energy_profile_lines

    def solution_json_dict(self):
        d = super().solution_json_dict()
        d['energy_profile'] = [{'q': line.q, 'c': line.c} for line in self.energy_profile_lines]
        return d

    def gantt_chart_color(self):
        return 'g'

    def __str__(self):
        super_str = super().__str__()
        return 'Idle {}, PARAMS: lines={}'.format(super_str, self.energy_profile_lines)

    def __repr__(self):
        return self.__str__()


class MovementActivity(Activity):
    """
    Class for movement representation in ILP model.
    Adds storing of dynamic activity ILP parameters: minimal and maximal duration,
    optional fixed start and end times and piecewise-linearized energy consumption profile.
    """
    def __init__(
        self,
        activity_id: str,
        min_duration: float,
        max_duration: float,
        fixed_start_time: Optional[float],
        fixed_end_time: Optional[float],
    ):
        super().__init__(activity_id, 'MOVEMENT')
        # params
        self.min_duration: float = min_duration
        self.max_duration: float = max_duration
        self.fixed_start_time: Optional[float] = fixed_start_time
        self.fixed_end_time: Optional[float] = fixed_end_time
        self.energy_profile_lines: List[Line2D] = []

    def set_energy_profile(self, energy_profile_lines: List[Line2D]):
        self.energy_profile_lines = energy_profile_lines

    def solution_json_dict(self):
        d = super().solution_json_dict()
        d['energy_profile'] = [{'q': line.q, 'c': line.c} for line in self.energy_profile_lines]
        return d

    def gantt_chart_color(self):
        return 'b'

    def __str__(self):
        super_str = super().__str__()
        return 'Movement {}, PARAMS: d_min={}, d_max={}, s_fixed={}, e_fixed={}, lines={}'.format(
            super_str,
            self.min_duration, self.max_duration,
            self.fixed_start_time, self.fixed_end_time,
            self.energy_profile_lines,
        )

    def __repr__(self):
        return self.__str__()


class WorkActivity(Activity):
    """
    Class for work (or other fixed) activity representation in ILP model.
    Adds storing of work activity ILP parameters: fixed duration and optional fixed start and end times.
    """
    def __init__(
        self,
        activity_id: str,
        fixed_duration: float,
        fixed_start_time: Optional[float],
        fixed_end_time: Optional[float],
    ):
        super().__init__(activity_id, 'WORK')
        # params
        self.fixed_duration: float = fixed_duration
        self.fixed_start_time: Optional[float] = fixed_start_time
        self.fixed_end_time: Optional[float] = fixed_end_time

    def gantt_chart_color(self):
        return 'r'

    def __str__(self):
        super_str = super().__str__()
        return 'Work {}, PARAMS: d_fixed={}, s_fixed={}, e_fixed={}'.format(
            super_str, self.fixed_duration, self.fixed_start_time, self.fixed_end_time,
        )

    def __repr__(self):
        return self.__str__()
