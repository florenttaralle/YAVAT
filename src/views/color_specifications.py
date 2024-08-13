import attr
from PyQt5.QtGui import QColor

@attr.define
class EventColorSpecification:
    border:                 QColor = QColor("#000000")
    object_default:         QColor = QColor("#0000A6")
    object_hovering:        QColor = QColor("#0000e0")  
    object_moving:          QColor = QColor("#0505ff")

@attr.define
class RangeEventColorSpecification(EventColorSpecification):
    handle_left_default:    QColor = QColor("#A60000")
    handle_left_hovering:   QColor = QColor("#e00000")
    handle_left_moving:     QColor = QColor("#ff0505")

    handle_right_default:   QColor = QColor("#00A600")
    handle_right_hovering:  QColor = QColor("#00e000")
    handle_right_moving:    QColor = QColor("#05ff05")

    def __attrs_post_init__(self):
        if self.handle_right_default is None:
            self.handle_right_default = self.handle_left_default
        if self.handle_right_hovering is None:
            self.handle_right_hovering = self.handle_left_hovering
        if self.handle_right_moving is None:
            self.handle_right_moving = self.handle_left_moving
