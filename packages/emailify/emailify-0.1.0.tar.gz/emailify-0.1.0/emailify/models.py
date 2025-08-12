from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Union

import pandas as pd
from pydantic import BaseModel, Field, model_validator


class StyleProperty(BaseModel):
    prop: str
    value: Any
    mapped: str
    unit: Optional[str] = None

    @classmethod
    def from_mapping_key(cls, key: str, mapped: str) -> "StyleProperty":
        return cls.model_validate({"key": key, "mapped": mapped})

    @model_validator(mode="before")
    @classmethod
    def _parse_from_key(cls, data: Any) -> Any:
        if isinstance(data, dict) and "key" in data and "mapped" in data:
            key = data["key"]
            parts = str(key).split("|", 2)
            if len(parts) == 2:
                prop, raw_value = parts
                unit = None
            else:
                prop, raw_value, unit = parts
            return {
                "prop": prop,
                "value": raw_value,
                "mapped": data["mapped"],
                "unit": unit,
            }
        return data

    def is_float(self, value: Any) -> bool:
        try:
            float(value)
            return True
        except ValueError:
            return False

    def render(self, value: Any) -> str:
        if self.unit and value is not None and self.is_float(value):
            return f"{self.mapped}{self.unit};"
        return f"{self.mapped};"


class Style(BaseModel):
    class Config:
        frozen = True

    text_align: Optional[
        Literal[
            "left",
            "center",
            "right",
        ]
    ] = Field(default=None)
    align: Optional[
        Literal[
            "left",
            "center",
            "right",
        ]
    ] = Field(default=None)
    padding: Optional[str] = Field(default=None)
    padding_left: Optional[str] = Field(default=None)
    padding_right: Optional[str] = Field(default=None)
    padding_top: Optional[str] = Field(default=None)
    padding_bottom: Optional[str] = Field(default=None)
    font_size: Optional[float] = Field(default=None)
    font_color: Optional[str] = Field(default=None)
    font_family: Optional[str] = Field(default=None)
    bold: Optional[bool] = Field(default=None)
    border: Optional[str] = Field(default=None)
    border_left: Optional[str] = Field(default=None)
    border_right: Optional[str] = Field(default=None)
    border_top: Optional[str] = Field(default=None)
    border_bottom: Optional[str] = Field(default=None)
    border_style: Optional[str] = Field(default=None)
    border_color: Optional[str] = Field(default=None)
    background_color: Optional[str] = Field(default=None)
    text_wrap: Optional[bool] = Field(default=None)

    def merge(self, other: "Style") -> "Style":
        self_dict = self.model_dump(exclude_none=True)
        other_dict = other.model_dump(exclude_none=True)
        self_dict.update(other_dict)
        return self.model_validate(self_dict)


class Component(BaseModel):
    style: Style = Field(default_factory=Style)

    class Config:
        arbitrary_types_allowed = True


class Text(Component):
    text: str
    width: float = Field(default=1)
    height: float = Field(default=1)


class Fill(Component):
    width: str = Field(default="100%")
    height: str = Field(default="20px")


class Image(Component):
    data: Union[Path, str, bytes, BytesIO]
    format: Literal["png", "jpeg", "jpg", "gif", "svg"] = Field(default="png")
    width: str = Field(default="auto")
    height: str = Field(default="auto")

    @model_validator(mode="before")
    @classmethod
    def _normalize_image_input(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value

        data = value.get("data")
        if isinstance(data, str):
            value["data"] = Path(data)
        elif isinstance(data, BytesIO):
            value["data"] = data.getvalue()

        if value.get("format") in (None, "") and isinstance(value.get("data"), Path):
            suffix = value["data"].suffix.lower().lstrip(".")
            if suffix in {"png", "jpeg", "jpg", "gif", "svg"}:
                value["format"] = suffix
        return value


class Table(Component):
    data: pd.DataFrame
    header_style: Dict[str, Style] = Field(default_factory=dict)
    body_style: Style = Field(default_factory=Style)
    column_style: Dict[str, Style] = Field(default_factory=dict)
    column_width: Dict[str, float] = Field(default_factory=dict)
    row_style: Dict[float, Style] = Field(default_factory=dict)
    max_col_width: Optional[float] = Field(default=None)
    header_filters: bool = Field(default=True)
    default_style: bool = Field(default=True)
    auto_width_tuning: float = Field(default=5)
    auto_width_padding: float = Field(default=5)
    merge_equal_headers: bool = Field(default=True)

    def with_stripes(
        self,
        color: str = "#D0D0D0",
        pattern: Literal["even", "odd"] = "odd",
    ) -> "Table":
        return self.model_copy(
            update=dict(
                row_style={
                    idx: (
                        self.row_style.get(idx, Style()).merge(
                            Style(background_color=color)
                        )
                        if (pattern == "odd" and idx % 2 != 0)
                        or (pattern == "even" and idx % 2 == 0)
                        else self.row_style.get(idx, Style())
                    )
                    for idx in range(self.data.shape[0])
                }
            )
        )
