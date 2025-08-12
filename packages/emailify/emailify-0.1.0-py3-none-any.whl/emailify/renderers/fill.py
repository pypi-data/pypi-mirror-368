from emailify.models import Fill
from emailify.renderers.core import _render
from emailify.renderers.style import render_extra_props, render_style


def render_fill(fill: Fill) -> str:
    return _render(
        "fill",
        fill=fill,
        style=render_style(fill.style),
        extra_props=render_extra_props("fill", fill.style),
    )
