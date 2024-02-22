from typing import Tuple, Optional, Callable, Dict

from reactpy import component, html
from typing_extensions import TypedDict

from gui.action.action_type import ActionType
from gui.action.utils import check_action_id, before_duration_change, check_action_durations
from gui.atoms.input import Input
from gui.atoms.optional_input import OptionalInput


class IdleActionProps(TypedDict):
    id: str
    type: ActionType
    position: Tuple[str, str, str]
    min_duration: Optional[str]
    max_duration: Optional[str]
    duration: Optional[str]
    fixed_start: Optional[str]
    fixed_end: Optional[str]


def newIdleActionProps(robot_id: str, idle_num: int) -> IdleActionProps:
    return {
        "id": f'{robot_id}_a{str(idle_num).rjust(2, "0")}_idle',
        "type": ActionType.IDLE,
        "position": ('0.0', '0.0', '0.0'),
        "min_duration": None,
        "max_duration": None,
        "duration": None,
        "fixed_start": None,
        "fixed_end": None,
    }


@component
def IdleAction(props: IdleActionProps, on_change: Callable, app_state: Dict):
    return html.div(
        html.h2('Idle Action'),
        Input(
            'Id: ',
            props["id"],
            lambda value: on_change(value, 'id'),
            error=check_action_id(props["id"], app_state),
        ),
        OptionalInput(
            'Min duration (s): ',
            props["min_duration"],
            lambda value: on_change(value, 'min_duration'),
            before_change=before_duration_change,
            default_value='1.000',
            error=check_action_durations(props['min_duration'], props['max_duration']),
        ),
        html.p(f'Max duration (s): {props["max_duration"]}'),
    )
