from typing import Callable, Optional, Dict

from reactpy import component, html

from gui.atoms.render_if import render_if


def handle_change(event: Dict, on_change: Callable, before_change: Callable):
    print(event)
    if before_change(event['target']['value']):
        on_change(event['target']['value'])
    else:
        event['defaultPrevented'] = True


@component
def OptionalInput(
    label: str,
    value: Optional[str],
    on_change: Callable[[str], None],
    before_change: Callable[[str], bool] = None,
    default_value: str = '',
    unset_text: str = ' - ',
    button_text_set: str = 'Set',
    button_text_unset: str = 'Unset',
    placeholder: str = '',
    error: str = None,
):
    if before_change is None:
        before_change = lambda _: True

    return html.div(
        html.label(
            label,
        ),
        render_if(value is not None, html.input(
            {
                "value": value,
                "on_change": lambda e: handle_change(e, on_change, before_change),
                "placeholder": placeholder,
                "style": {
                    "border-color": 'black' if error is None else 'red',
                },
            },
        )),
        render_if(value is None, html.span(unset_text)),
        html.button(
            {
                "on_click": lambda e: on_change(None if value is not None else default_value),
            },
            button_text_set if value is None else button_text_unset,
        ),
        render_if(error is not None, html.span(error)),
    )
