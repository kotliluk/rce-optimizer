from typing import Optional

from reactpy import component, html
from typing_extensions import TypedDict

from gui.action.action_type import ActionType


class MoveActionProps(TypedDict):
    id: str
    type: ActionType
    min_duration: float
    max_duration: float
    fixed_start: Optional[float]
    fixed_end: Optional[float]


def newMoveActionProps(robot_id: str, idle_num: int) -> MoveActionProps:
    return {
        "id": f"{robot_id}_a{str(idle_num).rjust(2, '0')}_idle",
        "type": ActionType.MOVE,
        "min_duration": 1.0,
        "max_duration": 5.0,
        "fixed_start": None,
        "fixed_end": None,
    }


@component
def MoveAction(props: MoveActionProps):
    return html.div(
        html.h2('Move Action'),
        html.p(f'Id: {props["id"]}'),
        html.p(f'Min duration (s): {props["min_duration"]}'),
        html.p(f'Max duration (s): {props["max_duration"]}'),
    )