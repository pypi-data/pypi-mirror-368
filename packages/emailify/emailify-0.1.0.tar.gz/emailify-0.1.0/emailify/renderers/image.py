from base64 import b64encode

from emailify.models import Image
from emailify.renderers.core import _render
from emailify.renderers.style import merge_styles, render_extra_props, render_style
from emailify.styles.image_default import IMAGE_STYLE


def _as_data_uri(content: bytes, mime: str) -> str:
    return f"data:{mime};base64,{b64encode(content).decode('ascii')}"


def render_image(image: Image) -> str:
    src = str(image.data)
    if isinstance(image.data, (bytes, bytearray)):
        mime = "image/svg+xml" if image.format == "svg" else f"image/{image.format}"
        src = _as_data_uri(image.data, mime)

    cur_style = merge_styles(IMAGE_STYLE, image.style)
    return _render(
        "image",
        image=image,
        src=src,
        style=render_style(cur_style),
        extra_props=render_extra_props(
            "image", cur_style, {"width": image.width, "height": image.height}
        ),
    )
