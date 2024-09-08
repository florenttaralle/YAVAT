from __future__ import annotations
import attr, json
from typing import List
from src.models.annotation_list import AnnotationListModel, AnnotationModel
from .timeline import TimelineProfileModel, TimelineModel
from .timeseries import TimeseriesProfileModel, TimeseriesModel

@attr.define
class ProfileModel:
    timelines:      List[TimelineProfileModel] = attr.field(factory=list)
    timeseries:     List[TimeseriesProfileModel] = attr.field(factory=list)
    path:           str|None = None


    def data(self):
        return {
            'timelines':    [timeline.data() for timeline in self.timelines],
            'timeseries':   [timeseries.data() for timeseries in self.timeseries],
        }
    
    @classmethod
    def parse(cls, data) -> ProfileModel:
        timelines = list(map(TimelineProfileModel.parse, data.get('timelines', [])))
        timeseries = list(map(TimeseriesProfileModel.parse, data.get('timeseries', [])))
        return cls(timelines, timeseries)

    @classmethod
    def from_annotations(cls, annotations: AnnotationListModel) -> ProfileModel:
        timelines = [
            TimelineProfileModel.from_timeline(annotation)
            for annotation in annotations
            if isinstance(annotation, TimelineModel)
        ]
        timeseries = [
            TimeseriesProfileModel.from_timeseries(annotation)
            for annotation in annotations
            if isinstance(annotation, TimeseriesModel)
        ]
        return cls(timelines, timeseries)
    
    @classmethod
    def load(cls, path: str) -> ProfileModel:
        with open(path, 'rt') as json_file:
            data = json.load(json_file)
        timelines   = [TimelineProfileModel.parse(tl_data) for tl_data in data.get('timelines', [])]
        timeseries  = [TimeseriesProfileModel.parse(ts_data) for ts_data in data.get('timeseries', [])]
        return cls(timelines, timeseries, path)
    
    def save(self, path: str) -> ProfileModel:
        with open(path, 'wt') as json_file:
            json.dump(self.data(), json_file, indent=2)
        self.path = path
        return self

    def update_annotations(self, annotations: AnnotationListModel, create: bool) -> AnnotationListModel:
        # update existing timelines or create missing timelines
        for tl_profile in self.timelines:
            used = False
            for annotation in annotations:
                used |= tl_profile.apply(annotation)

            if not used and create:
                # create missing timelines
                timeline = TimelineModel(annotations.duration, tl_profile.name, tl_profile.color, colors=tl_profile.colors)
                annotations.append(timeline)    

        # update existing timeseries
        for ts_profile in self.timeseries:
            for annotation in annotations:
                ts_profile.apply(annotation)

        return annotations

    def update_annotation(self, annotation: AnnotationModel) -> AnnotationModel:
        if isinstance(annotation, TimelineModel):
            for tl_profile in self.timelines:
                tl_profile.apply(annotation)
        elif isinstance(annotation, TimeseriesModel):
            for ts_profile in self.timeseries:
                ts_profile.apply(annotation)
        return annotation
    