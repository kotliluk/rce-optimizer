from typing import List

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


@component
def App():
    app_state, set_app_state = hooks.use_state(newAppState())

    return html.div(
        html.h1("RCE Optimizer"),
        [Robot(robot) for robot in app_state['robots']]
    )
