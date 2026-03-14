#! /usr/bin/env python3
import argparse as ap
import os

from PyQt6.QtWidgets import QApplication

from src.models.app_config import AppConfig
from src.views.yavat import YavatView

parser = ap.ArgumentParser()
parser.add_argument('path', nargs='?', default=None)
args = parser.parse_args()

config_path = os.path.join(os.path.expanduser("~"), ".config", "yavat", "config.json")
config = AppConfig.load(config_path)

app = QApplication([])
window = YavatView(config, args.path)
window.show()
app.exec()
