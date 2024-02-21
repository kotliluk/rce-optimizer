from typing import List

from reactpy import component, html
from typing_extensions import TypedDict

from gui.action.action import ActionProps, Action
from gui.action.idle_action import newIdleActionProps
from gui.action.move_action import newMoveActionProps


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
def Robot(props: RobotProps):
    return html.div(
        html.h2('Robot'),
        html.p(f'Id: {props["id"]}'),
        [Action(action) for action in props['actions']]
    )
