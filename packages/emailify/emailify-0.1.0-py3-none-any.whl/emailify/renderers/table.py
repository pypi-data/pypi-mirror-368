import re
from typing import Dict, List, Tuple

from PIL import ImageFont

from emailify.models import Table
from emailify.renderers.core import _render
from emailify.renderers.style import merge_styles, render_style
from emailify.styles.table_default import COL_STYLE, HEADER_STYLE

DEFAULT_FONT_FAMILY = "Arial"
DEFAULT_FONT_SIZE = 11


def _get_text_size(text: str, font_size: int | None, font_family: str | None) -> float:
    size = font_size or DEFAULT_FONT_SIZE
    family = (font_family or DEFAULT_FONT_FAMILY).lower()
    try:
        font = ImageFont.truetype(f"{family}.ttf", size)
    except Exception:
        font = ImageFont.load_default()
    return float(font.getlength(str(text)))


def _get_style_font_family(*styles) -> str | None:
    current = None
    for s in filter(None, styles):
        current = getattr(s, "font_family", None) or current
    return current


def _get_style_font_size(*styles) -> int | None:
    current = None
    for s in filter(None, styles):
        current = getattr(s, "font_size", None) or current
    return current


def _compute_header_merge_spans(
    columns: List[str],
) -> Tuple[Dict[int, int], Dict[int, List[int]]]:
    indices_by_header: Dict[str, List[int]] = {}
    for idx, header in enumerate(columns):
        if header not in indices_by_header:
            indices_by_header[header] = [idx]
        else:
            if indices_by_header[header][-1] == idx - 1:
                indices_by_header[header].append(idx)
            else:
                indices_by_header[header] = [idx]

    span_by_start: Dict[int, int] = {}
    contiguous_only: Dict[int, List[int]] = {}
    for header, indices in list(indices_by_header.items()):
        if len(indices) >= 2:
            start = indices[0]
            span = len(indices)
            span_by_start[start] = span
            contiguous_only[start] = indices
    return span_by_start, contiguous_only


def render_table(table: Table) -> str:
    row_styles: Dict[int, str] = {}
    header_styles: Dict[str, str] = {}
    col_styles: Dict[str, str] = {}
    col_widths: Dict[str, int] = {}
    header_spans_by_start: Dict[int, int] = {}
    skip_header_indices: set[int] = set()
    header_wraps: Dict[str, bool] = {}
    body_nowrap_cols: set[str] = set()

    for header in table.data.columns:
        header_styles[header] = render_style(
            merge_styles(
                HEADER_STYLE,
                table.header_style.get(header),
            )
        )

    for col in table.data.columns:
        col_styles[col] = render_style(
            merge_styles(
                COL_STYLE,
                table.column_style.get(col),
            )
        )

    if table.merge_equal_headers:
        spans_by_start, groups = _compute_header_merge_spans(list(table.data.columns))
        header_spans_by_start = spans_by_start
        for _, indices in groups.items():
            skip_header_indices.update(indices[1:])

    if table.data is not None and table.data.shape[1] > 0:
        max_cap = table.max_col_width if table.max_col_width is not None else 10**9
        for col_idx, col_name in enumerate(table.data.columns):
            set_width = table.column_width.get(col_name)
            if set_width is not None:
                col_widths[col_name] = int(set_width)
                continue
            series = table.data.iloc[:, col_idx]
            cur_skip = col_idx in skip_header_indices
            header_font_size = _get_style_font_size(
                HEADER_STYLE,
                table.style,
                table.header_style.get(col_name),
            )
            header_font_family = _get_style_font_family(
                HEADER_STYLE,
                table.style,
                table.header_style.get(col_name),
            )
            header_px = _get_text_size(col_name, header_font_size, header_font_family)
            header_longest_word_px = 0.0
            for word in filter(None, re.split(r"[\s/()_-]+", str(col_name))):
                header_longest_word_px = max(
                    header_longest_word_px,
                    _get_text_size(word, header_font_size, header_font_family),
                )

            col_font_size = _get_style_font_size(
                COL_STYLE,
                table.style,
                table.body_style,
                table.column_style.get(col_name),
            )
            col_font_family = _get_style_font_family(
                COL_STYLE,
                table.style,
                table.body_style,
                table.column_style.get(col_name),
            )
            try:
                body_max_px = float(
                    series.astype(str)
                    .map(lambda it: _get_text_size(it, col_font_size, col_font_family))
                    .max()
                )
            except Exception:
                body_max_px = 0.0
            small_body_threshold = 90.0
            wrap_factor = 1.6
            should_wrap_header = (
                header_px > max(body_max_px, 40.0) * wrap_factor
                and body_max_px <= small_body_threshold
            ) and not cur_skip
            header_wraps[col_name] = should_wrap_header

            base_px = max(body_max_px, 10.0) + (table.auto_width_padding or 0)
            if should_wrap_header:
                base_px = max(
                    base_px, header_longest_word_px + (table.auto_width_padding or 0)
                )
            else:
                base_px = max(base_px, header_px + (table.auto_width_padding or 0))

            est_px = int(min(base_px, max_cap))
            est_px = min(est_px, max_cap)
            col_widths[col_name] = int(est_px)

            sample = series.astype(str).head(400)
            digit_count = int(sum(ch.isdigit() for s in sample for ch in s))
            alnum_count = int(sum(ch.isalnum() for s in sample for ch in s))
            if alnum_count > 0 and digit_count / alnum_count >= 0.5:
                body_nowrap_cols.add(col_name)

    body_style = render_style(
        merge_styles(
            table.body_style,
        )
    )

    for idx in range(table.data.shape[0]):
        row_styles[idx] = render_style(merge_styles(table.row_style.get(idx)))

    headers_render: List[Dict[str, object]] = []
    for idx, header in enumerate(table.data.columns):
        if idx in skip_header_indices:
            continue
        span = header_spans_by_start.get(idx, 1)
        span_width = 0
        for j in range(idx, idx + span):
            name = table.data.columns[j]
            span_width += col_widths.get(name, 0)
        headers_render.append(
            {
                "text": header,
                "span": span,
                "width": span_width,
                "wrap": header_wraps.get(header, False),
            }
        )

    return _render(
        "table",
        table=table,
        header_styles=header_styles,
        col_styles=col_styles,
        row_styles=row_styles,
        body_style=body_style,
        col_widths=col_widths,
        headers_render=headers_render,
        body_nowrap_cols=body_nowrap_cols,
    )
