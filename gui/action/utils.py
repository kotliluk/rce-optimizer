import re
from typing import Optional, Dict


def check_action_id(action_id: str, app_state: Dict) -> Optional[str]:
    same_ids = 0
    for robot in app_state['robots']:
        for action in robot['actions']:
            if action['id'] == action_id:
                same_ids += 1

    if same_ids > 1:
        return 'Duplicated ID'


DURATION_REGEX = re.compile(r'^[1-9][0-9]*{\.}[0-9]{0-5}$')


def before_duration_change(duration: Optional[str]) -> bool:
    if duration is None:
        return True

    try:
        x = float(duration)
    except ValueError:
        return False
    else:
        return x >= 0


def check_action_durations(min_duration: str, max_duration: str) -> Optional[str]:
    # TODO - combine with before...
    if min_duration is not None and max_duration is not None and min_duration >= max_duration:
        return 'Min duration must be less than max duration'
