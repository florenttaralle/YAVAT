from PyQt6.QtCore import QObject

from .app_config import AppConfig
from .yavat import YavatModel
from .annotation import AnnotationModel
from .watched_item import WatchedItemModel
from .time_window import TimeWindowModel

class ApplicationStateModel(QObject):
    def __init__(self, config: AppConfig):
        self.config = config
        self.watched_yavat = WatchedItemModel[YavatModel]()
        self.watched_active_annotation = WatchedItemModel[AnnotationModel]()
        self.watched_time_window = WatchedItemModel[TimeWindowModel]()

    @property
    def yavat(self) -> YavatModel|None:
        return self.watched_yavat.get()
    def set_yavat(self, yavat: YavatModel|None):
        return self.watched_yavat.set(yavat)
    
    @property
    def active_annotation(self) -> AnnotationModel|None:
        return self.watched_active_annotation.get()
    def set_active_annotation(self, active_annotation: AnnotationModel|None):
        return self.watched_active_annotation.set(active_annotation)
    
    @property
    def time_window(self) -> TimeWindowModel|None:
        return self.watched_time_window.get()
    def set_time_window(self, time_window: TimeWindowModel|None):
        return self.watched_time_window.set(time_window)
