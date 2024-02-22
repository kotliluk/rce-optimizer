from reactpy import component, html


@component
def render_if(visible: bool, what):
    return what if visible else html._()
