from typing import Optional

from reactpy import component, html
from typing_extensions import TypedDict

from gui.action.action_type import ActionType


class WorkActionProps(TypedDict):
    id: str
    type: ActionType
    duration: float
    fixed_start: Optional[float]
    fixed_end: Optional[float]


def newWorkActionProps(robot_id: str, idle_num: int) -> WorkActionProps:
    return {
        "id": f"{robot_id}_a{str(idle_num).rjust(2, '0')}_idle",
        "type": ActionType.WORK,
        "duration": 5.0,
        "fixed_start": None,
        "fixed_end": None,
    }


@component
def WorkAction(props: WorkActionProps):
    return html.div(
        html.h2('Work Action'),
        html.p(f'Id: {props["id"]}'),
        html.p(f'Duration (s): {props["duration"]}'),
    )
