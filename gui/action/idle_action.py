from typing import Tuple, Optional

from reactpy import component, html
from typing_extensions import TypedDict

from gui.action.action_type import ActionType


class IdleActionProps(TypedDict):
    id: str
    type: ActionType
    position: Tuple[float, float, float]
    min_duration: Optional[float]
    max_duration: Optional[float]
    duration: Optional[float]
    fixed_start: Optional[float]
    fixed_end: Optional[float]


def newIdleActionProps(robot_id: str, idle_num: int) -> IdleActionProps:
    return {
        "id": f"{robot_id}_a{str(idle_num).rjust(2, '0')}_idle",
        "type": ActionType.IDLE,
        "position": (0.0, 0.0, 0.0),
        "min_duration": None,
        "max_duration": None,
        "duration": None,
        "fixed_start": None,
        "fixed_end": None,
    }


@component
def IdleAction(props: IdleActionProps):
    return html.div(
        html.h2('Idle Action'),
        html.p(f'Id: {props["id"]}'),
        html.p(f'Min duration (s): {props["min_duration"]}'),
        html.p(f'Max duration (s): {props["max_duration"]}'),
    )