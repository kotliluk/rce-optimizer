from typing import Optional, Callable, Dict

from reactpy import component, html
from typing_extensions import TypedDict

from gui.action.action_type import ActionType
from gui.action.utils import check_action_id
from gui.atoms.input import Input


class MoveActionProps(TypedDict):
    id: str
    type: ActionType
    min_duration: str
    max_duration: str
    fixed_start: Optional[str]
    fixed_end: Optional[str]


def newMoveActionProps(robot_id: str, idle_num: int) -> MoveActionProps:
    return {
        "id": f'{robot_id}_a{str(idle_num).rjust(2, "0")}_move',
        "type": ActionType.MOVE,
        "min_duration": '1.0',
        "max_duration": '5.0',
        "fixed_start": None,
        "fixed_end": None,
    }


@component
def MoveAction(props: MoveActionProps, on_change: Callable, app_state: Dict):
    return html.div(
        html.h2('Move Action'),
        Input(
            'Id: ',
            props["id"],
            lambda value: on_change(value, 'id'),
            error=check_action_id(props["id"], app_state)
        ),
        html.p(f'Min duration (s): {props["min_duration"]}'),
        html.p(f'Max duration (s): {props["max_duration"]}'),
    )
