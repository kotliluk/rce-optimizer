import re
from typing import List, Callable

from reactpy import component, html, hooks
from typing_extensions import TypedDict

from gui.robot.robot import Robot, RobotProps, newRobotProps


class AppState(TypedDict):
    robots: List[RobotProps]


def newAppState() -> AppState:
    return {
        "robots": [
            newRobotProps(1),
        ]
    }


INT_REGEX = re.compile(r'^[0-9]+')


def _handle_change(value, path: str, state: AppState, set_state: Callable[[AppState], None]):
    changed_state = state.copy()
    nested_state = changed_state
    steps = path.split('.')
    for s in steps[:-1]:
        if INT_REGEX.match(s):
            s = int(s)
        nested_state = nested_state[s]
    nested_state[steps[-1]] = value
    set_state(changed_state)


@component
def App():
    app_state, set_app_state = hooks.use_state(newAppState())

    handle_change = hooks.use_callback(
        lambda value, path: _handle_change(value, path, app_state, set_app_state),
        dependencies=[app_state, set_app_state],
    )

    return html.div(
        html.h1("RCE Optimizer"),
        [
            Robot(robot, lambda value, path, _i=i: handle_change(value, f'robots.{_i}.{path}'), app_state)
            for i, robot in enumerate(app_state['robots'])
        ],
    )
