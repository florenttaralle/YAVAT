from typing import Mapping, Tuple
from .annotation_watcher import AnnotationWatcherModel, AnnotationModel

class AnnotationWatcherSingleton:
    _instances: Mapping[Tuple[object, AnnotationModel], AnnotationWatcherModel] = {}

    @classmethod
    def get_or_create(cls, watcher_class: object, annotation: AnnotationModel, *args, **kwargs) -> AnnotationWatcherModel:
        key = hash((watcher_class, annotation))
        instance = cls._instances.get(key, None)
        if instance is None:
            instance = watcher_class(annotation, *args, **kwargs)
            instance.destroyed.connect(lambda _=None: cls.onWatcherDestroyed(key))
            cls._instances[key] = instance
        return instance

    @classmethod
    def onWatcherDestroyed(cls, key):
        del cls._instances[key]
