from __future__ import annotations

import json
import os
from dataclasses import dataclass
from PyQt6.QtGui import QColor

@dataclass
class AppConfig:
    path: str
    font_size: int = 14
    mute: bool = False
    auto_play: bool = True
    default_color = QColor("#346beb")

    MIN_FONT_SIZE = 6
    MAX_FONT_SIZE = 30

    @classmethod
    def load(cls, path: str) -> "AppConfig":
        config = AppConfig(path=path)        
        if not os.path.exists(path):
            return config

        try:
            with open(path, "rt", encoding="utf-8") as config_file:
                data = json.load(config_file)
        except Exception:
            return config

        # load font size
        if 'font_size' in data:
            config.font_size = max(cls.MIN_FONT_SIZE, min(cls.MAX_FONT_SIZE, data['font_size']))
        # load mute status
        if 'mute' in data:
            config.mute = data['mute']
        # load auto-play
        if 'auto_play' in data:
            config.auto_play = QColor(data['auto_play'])
        # load default color
        if 'default_color' in data:
            config.default_color = QColor(data['default_color'])

        return config

    def save(self):
        folder = os.path.dirname(self.path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        content = {
            "font_size": int(self.font_size),
            "mute": self.mute,
            "auto_play": self.auto_play,
            "default_color": self.default_color.name(),
        }
        with open(self.path, "wt", encoding="utf-8") as config_file:
            json.dump(content, config_file, indent=2)

