from PyQt6.QtWidgets import QWidget, QSizePolicy

class Spacer(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

