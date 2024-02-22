from typing import Union, Callable, Dict

from reactpy import component

from gui.action.action_type import ActionType
from gui.action.idle_action import IdleAction, IdleActionProps
from gui.action.move_action import MoveAction, MoveActionProps
from gui.action.work_action import WorkAction, WorkActionProps

ActionProps = Union[IdleActionProps, MoveActionProps, WorkActionProps]


@component
def Action(props: ActionProps, on_change: Callable, app_state: Dict):
    if props['type'] == ActionType.IDLE:
        return IdleAction(props, on_change, app_state)
    elif props['type'] == ActionType.WORK:
        return WorkAction(props, on_change, app_state)
    else:
        return MoveAction(props, on_change, app_state)
