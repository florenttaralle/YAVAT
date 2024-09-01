#! /usr/bin/env python3
import argparse as ap
from PyQt6.QtWidgets import QApplication
# ##############################################################
from src.views.yavat import YavatView
# ##############################################################

parser = ap.ArgumentParser()
parser.add_argument('path', nargs='?', default=None)
args = parser.parse_args()

app = QApplication([])
window = YavatView(args.path)
window.show()
app.exec()

