from .annotation import AnnotationModel, QColor

def annotation_factory(type: str, duration: int, name: str, color: str, **kwargs) -> AnnotationModel:
    color = QColor(color)

    if type == "AnnotationGroupModel":
        from .annotation_group import AnnotationGroupModel
        return AnnotationGroupModel.parse(duration, name, color, **kwargs)
    
    elif type == "TimeseriesModel":
        from .timeseries import TimeseriesModel
        return TimeseriesModel.parse(duration, name, color, **kwargs)        
    
    elif type == "TimelineModel":
        from .timeline import TimelineModel
        return TimelineModel.parse(duration, name, color, **kwargs)        
        
    raise RuntimeError(f"Unknown type: {type}")
