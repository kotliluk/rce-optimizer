from typing import Callable

from reactpy import component, html

from gui.atoms.render_if import render_if


@component
def Input(
    label: str,
    value: str,
    on_change: Callable[[str], None],
    before_change: Callable[[str], bool] = None,
    placeholder: str = '',
    error: str = None,
):
    if before_change is None:
        before_change = lambda _: True

    return html.div(
        html.label(
            label,
        ),
        html.input(
            {
                "value": value,
                "on_change": lambda e: on_change(e['target']['value']) if before_change(e['target']['value']) else None,
                "placeholder": placeholder,
                "style": {
                    "border-color": 'black' if error is None else 'red',
                },
            },
        ),
        render_if(error is not None, html.span(error)),
    )
