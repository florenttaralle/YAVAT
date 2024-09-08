from __future__ import annotations
import attr, json
from typing import List
from src.models.annotation_list import AnnotationListModel, AnnotationModel
from .timeline import TimelineTemplateModel, TimelineModel
from .timeseries import TimeseriesTemplateModel, TimeseriesModel

@attr.define
class TemplateModel:
    timelines:      List[TimelineTemplateModel] = attr.field(factory=list)
    timeseries:     List[TimeseriesTemplateModel] = attr.field(factory=list)
    path:           str|None = None


    def data(self):
        return {
            'timelines':    [timeline.data() for timeline in self.timelines],
            'timeseries':   [timeseries.data() for timeseries in self.timeseries],
        }
    
    @classmethod
    def parse(cls, data) -> TemplateModel:
        timelines = list(map(TimelineTemplateModel.parse, data.get('timelines', [])))
        timeseries = list(map(TimeseriesTemplateModel.parse, data.get('timeseries', [])))
        return cls(timelines, timeseries)

    @classmethod
    def from_annotations(cls, annotations: AnnotationListModel) -> TemplateModel:
        timelines = [
            TimelineTemplateModel.from_timeline(annotation)
            for annotation in annotations
            if isinstance(annotation, TimelineModel)
        ]
        timeseries = [
            TimeseriesTemplateModel.from_timeseries(annotation)
            for annotation in annotations
            if isinstance(annotation, TimeseriesModel)
        ]
        return cls(timelines, timeseries)
    
    @classmethod
    def load(cls, path: str) -> TemplateModel:
        with open(path, 'rt') as json_file:
            data = json.load(json_file)
        timelines   = [TimelineTemplateModel.parse(tl_data) for tl_data in data.get('timelines', [])]
        timeseries  = [TimeseriesTemplateModel.parse(ts_data) for ts_data in data.get('timeseries', [])]
        return cls(timelines, timeseries, path)
    
    def save(self, path: str) -> TemplateModel:
        with open(path, 'wt') as json_file:
            json.dump(self.data(), json_file, indent=2)
        self.path = path
        return self

    def update_annotations(self, annotations: AnnotationListModel, create: bool) -> AnnotationListModel:
        # update existing timelines or create missing timelines
        for tl_template in self.timelines:
            used = False
            for annotation in annotations:
                used |= tl_template.apply(annotation)

            if not used and create:
                # create missing timelines
                timeline = TimelineModel(annotations.duration, tl_template.name, tl_template.color, colors=tl_template.colors)
                annotations.append(timeline)    

        # update existing timeseries
        for ts_template in self.timeseries:
            for annotation in annotations:
                ts_template.apply(annotation)

        return annotations

    def update_annotation(self, annotation: AnnotationModel) -> AnnotationModel:
        if isinstance(annotation, TimelineModel):
            for tl_template in self.timelines:
                tl_template.apply(annotation)
        elif isinstance(annotation, TimeseriesModel):
            for ts_template in self.timeseries:
                ts_template.apply(annotation)
        return annotation
    