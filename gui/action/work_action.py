from typing import Optional, Dict, Callable

from reactpy import component, html
from typing_extensions import TypedDict

from gui.action.action_type import ActionType
from gui.action.utils import check_action_id
from gui.atoms.input import Input


class WorkActionProps(TypedDict):
    id: str
    type: ActionType
    duration: str
    fixed_start: Optional[str]
    fixed_end: Optional[str]


def newWorkActionProps(robot_id: str, idle_num: int) -> WorkActionProps:
    return {
        "id": f'{robot_id}_a{str(idle_num).rjust(2, "0")}_work',
        "type": ActionType.WORK,
        "duration": '5.0',
        "fixed_start": None,
        "fixed_end": None,
    }


@component
def WorkAction(props: WorkActionProps, on_change: Callable, app_state: Dict):
    return html.div(
        html.h2('Work Action'),
        Input(
            'Id: ',
            props["id"],
            lambda value: on_change(value, 'id'),
            error=check_action_id(props["id"], app_state)
        ),
        html.p(f'Duration (s): {props["duration"]}'),
    )
