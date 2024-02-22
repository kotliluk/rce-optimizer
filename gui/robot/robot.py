from typing import List, Callable

from reactpy import component, html
from typing_extensions import TypedDict

from gui.action.action import ActionProps, Action
from gui.action.idle_action import newIdleActionProps
from gui.action.move_action import newMoveActionProps
from gui.atoms.input import Input
from gui.robot.utils import check_robot_id


class RobotProps(TypedDict):
    id: str
    actions: List[ActionProps]


def newRobotProps(robot_num: int) -> RobotProps:
    robot_id = f'r{str(robot_num).rjust(2, "0")}'

    return {
        "id": robot_id,
        "actions": [
            newIdleActionProps(robot_id, 1),
            newMoveActionProps(robot_id, 2),
            newIdleActionProps(robot_id, 3),
        ],
    }


@component
def Robot(props: RobotProps, on_change: Callable, app_state):
    return html.div(
        html.h2('Robot'),
        Input(
            'Id: ',
            props["id"],
            lambda value: on_change(value, 'id'),
            error=check_robot_id(props["id"], app_state),
        ),
        [
            Action(action, lambda value, path, _i=i: on_change(value, f'actions.{_i}.{path}'), app_state)
            for i, action in enumerate(props['actions'])
        ],
    )
