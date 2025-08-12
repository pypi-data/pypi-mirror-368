from mjml import mjml2html

from emailify.models import Component, Fill, Image, Table, Text
from emailify.renderers.core import _render
from emailify.renderers.fill import render_fill
from emailify.renderers.image import render_image
from emailify.renderers.table import render_table
from emailify.renderers.text import render_text

RENDER_MAP = {
    Table: render_table,
    Text: render_text,
    Fill: render_fill,
    Image: render_image,
}


def render(
    *components: Component,
) -> str:
    parts: list[str] = []
    for component in components:
        parts.append(RENDER_MAP[type(component)](component))

    body_str = _render(
        "index",
        content="".join(parts),
    )
    return mjml2html(body_str)
