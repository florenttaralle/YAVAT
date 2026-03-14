from __future__ import annotations

import json
import os
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator
from PyQt6.QtGui import QColor


class AppConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    path: str
    font_size: int = 14
    annotation_graph_height: int = 72
    mute: bool = False
    auto_play: bool = True
    default_color: QColor = Field(default_factory=lambda: QColor(AppConfig.DEFAULT_COLOR_HEX))

    MIN_FONT_SIZE: ClassVar[int] = 6
    MAX_FONT_SIZE: ClassVar[int] = 30
    MIN_ANNOTATION_GRAPH_HEIGHT: ClassVar[int] = 0
    DEFAULT_FONT_SIZE: ClassVar[int] = 14
    DEFAULT_COLOR_HEX: ClassVar[str] = "#346beb"

    @field_validator("font_size", mode="before")
    @classmethod
    def _parse_font_size(cls, value: object) -> int:
        try:
            font_size = int(value)
        except Exception:
            font_size = cls.DEFAULT_FONT_SIZE
        return max(cls.MIN_FONT_SIZE, min(cls.MAX_FONT_SIZE, font_size))

    @field_validator("annotation_graph_height", mode="before")
    @classmethod
    def _parse_annotation_graph_height(cls, value: object) -> int:
        try:
            graph_height = int(value)
        except Exception:
            graph_height = 72
        return max(cls.MIN_ANNOTATION_GRAPH_HEIGHT, graph_height)

    @field_validator("default_color", mode="before")
    @classmethod
    def _parse_default_color(cls, value: object) -> QColor:
        if isinstance(value, QColor):
            return value if value.isValid() else QColor(cls.DEFAULT_COLOR_HEX)
        color = QColor(value) if value is not None else QColor(cls.DEFAULT_COLOR_HEX)
        if not color.isValid():
            color = QColor(cls.DEFAULT_COLOR_HEX)
        return color

    @field_serializer("default_color")
    def _serialize_default_color(self, color: QColor, _info) -> str:
        return color.name()

    @classmethod
    def load(cls, path: str) -> "AppConfig":
        default_config = cls(path=path)
        if not os.path.exists(path):
            return default_config

        try:
            with open(path, "rt", encoding="utf-8") as config_file:
                data = json.load(config_file)
        except Exception:
            return default_config

        try:
            return cls.model_validate({"path": path, **data})
        except Exception:
            return default_config

    def save(self):
        folder = os.path.dirname(self.path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        content = self.model_dump(mode="json", exclude={"path"})
        with open(self.path, "wt", encoding="utf-8") as config_file:
            json.dump(content, config_file, indent=2)
