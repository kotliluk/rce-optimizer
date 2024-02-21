from typing import Union

from reactpy import component

from gui.action.action_type import ActionType
from gui.action.idle_action import IdleAction, IdleActionProps
from gui.action.move_action import MoveAction, MoveActionProps
from gui.action.work_action import WorkAction, WorkActionProps

ActionProps = Union[IdleActionProps, MoveActionProps, WorkActionProps]


@component
def Action(props: ActionProps):
    if props['type'] == ActionType.IDLE:
        return IdleAction(props)
    elif props['type'] == ActionType.WORK:
        return WorkAction(props)
    else:
        return MoveAction(props)
