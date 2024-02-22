from typing import Optional, Dict


def check_robot_id(robot_id: str, app_state: Dict) -> Optional[str]:
    same_ids = 0
    for robot in app_state['robots']:
        if robot['id'] == robot_id:
            same_ids += 1

    if same_ids > 1:
        return 'Duplicated ID'

    return None
