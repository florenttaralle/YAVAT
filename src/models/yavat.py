from __future__ import annotations
import os, json, itertools as it
import numpy as np

from PyQt6.QtCore import QObject, pyqtSignal

from src.models.video import VideoModel, TimeWindowModel
from src.models.timeline import TimelineModel, EventModel
from src.models.timeseries import TimeseriesModel
from src.models.annotation_list import AnnotationListModel
from src.version import YAVAT_VERSION, VersionModel
from src.models.external.rttm import RTTMModel, RTTMType
from src.models.external.whisperx import WhisperXModel
from src.models.external.audio_rms import export_audio_rms_aligned_on_video_frames

class YavatModel(QObject):
    yavat_path_changed  = pyqtSignal(object)
    "SIGNAL: yavat_path_changed(path: str|None)"

    VERSION_KEY = 'yavat_version'

    def __init__(self, video: VideoModel, annotations: AnnotationListModel=None, 
                 yavat_path: str|None=None, parent: QObject|None=None):
        QObject.__init__(self, parent)
        self._video             = video
        self._annotations       = annotations or AnnotationListModel(video.n_frames)
        self._yavat_path        = yavat_path

        self._video.setParent(self)
        self._annotations.setParent(self)

    @property
    def video(self) -> VideoModel:
        return self._video

    @property
    def time_window(self) -> TimeWindowModel|None:
        return self._video.time_window if self._video is not None else None

    @property
    def annotations(self) -> AnnotationListModel:
        return self._annotations
    
    @property
    def yavat_path(self) -> str|None:
        return self._yavat_path
    def _set_yavat_path(self, path: str):
        if path != self._yavat_path:
            self._yavat_path = path
            self.yavat_path_changed.emit(path)
    
    @staticmethod
    def default_path(video_path: str) -> str:
        return os.path.splitext(video_path)[0] + ".yavat"
    
    @classmethod
    def load(cls, path: str):
        ext = os.path.splitext(path)[1].lower()
        if ext in {'.yavat', 'yvt'}:
            yavat_path = path
            video_path = None
        else:
            video_path = path
            yavat_path = cls.default_path(path)
            if not os.path.exists(yavat_path):
                yavat_path = None

        if yavat_path is not None:
            assert os.path.exists(yavat_path), f"Yavat File Not Found: {yavat_path}"
            with open(yavat_path, 'rt') as yavat_file:
                data    = json.load(yavat_file)

            assert cls.VERSION_KEY in data, 'Not a Yavat Annotation File'
            version     = VersionModel.from_str(data.get(cls.VERSION_KEY, '0.0.0'))
            assert version.compatible(YAVAT_VERSION), f"Yavat Annotation File Version {str(version)} not compatible with Yavat Application Version {str(YAVAT_VERSION)}"
            annotations = AnnotationListModel.parse(data['video']['duration_frames'], data['annotations'])

            if video_path is None:
                video_path = os.path.join(os.path.dirname(yavat_path), data['video']['video_filename'])
                assert os.path.exists(video_path), f"Video Not Found: {video_path}"

        else:
            annotations = None

        video = VideoModel(video_path)
        assert not video._error, video._error
        return cls(video, annotations, yavat_path)
    
    def save(self, yavat_path: str|None):
        if yavat_path is not None:
            self._set_yavat_path(yavat_path)
        assert self._yavat_path is not None
        content = {
            self.VERSION_KEY:   str(YAVAT_VERSION), 
            "video":            self._video.data(),
            "annotations":      self._annotations.data(),
        }
        with open(self._yavat_path, 'wt') as annotation_file:
            json.dump(content, annotation_file, indent=2)
    
    def load_rttm(self, rttm_path: str):
        # load rttm file content
        rttm = RTTMModel.load(rttm_path)
        # keep only the speaker entries
        rttm.entries = [entry for entry in rttm.entries if entry.entry_type == RTTMType.SPEAKER]
        assert len(rttm.entries), 'No Speaker entry found'
        # sort by speaker
        rttm.entries.sort(key=lambda entry: entry.speaker_name)
        # build a new timeline per speaker
        existing_names = {annotation.name for annotation in self._annotations}
        for speaker, entries in it.groupby(rttm.entries, key=lambda entry: entry.speaker_name):
            name = speaker if speaker not in existing_names else f"{speaker}_new"
            timeline = TimelineModel(self._video.n_frames, name)
            for entry in entries:
                first = self._video.to_frame_id(entry.start_s)
                last = self._video.to_frame_id(entry.stop_s)
                if timeline.can_add(first, last):
                    event = EventModel(first, last, label="speaking")
                    timeline.add(event)
            self._annotations.append(timeline)

    def load_whisperx(self, json_path: str):
        # load data from the json file
        assert os.path.exists(json_path), 'File not found'
        try:
            with open(json_path) as json_file:
                data = json.load(json_file)
        except Exception:
            raise RuntimeError("Invalid Json format")

        try:
            whisperx = WhisperXModel.model_validate(data)
        except Exception as what:
            print(what)
            raise RuntimeError("Invalid WhisperX format")
        
        # sort & group by speaker
        whisperx.segments.sort(key=lambda segment: segment.speaker)
        # build timeline per speaker
        existing_names = {annotation.name for annotation in self._annotations}
        for speaker, segments in it.groupby(whisperx.segments, key=lambda segment: segment.speaker):
            name = speaker if speaker not in existing_names else f"{speaker}_new"
            timeline = TimelineModel(self._video.n_frames, name)
            for segment in segments:
                first = self._video.to_frame_id(segment.start)
                last = self._video.to_frame_id(segment.end)
                if timeline.can_add(first, last):
                    event = EventModel(first, last, label=segment.text)
                    timeline.add(event)
            self._annotations.append(timeline)

    def load_audio(self):
        audio_channels = export_audio_rms_aligned_on_video_frames(
            self._video.path,
            False,
            self._video.fps,
            self._video.n_frames,
        )
        assert len(audio_channels), "No Audio Channel"
        for aid, audio_channel in enumerate(audio_channels):
            min_value = audio_channel.min()
            max_value = audio_channel.max()
            audio_channel = (audio_channel - min_value) / (max_value - min_value + 1e-12)
            xy_values = enumerate(map(float, audio_channel))
            timeseries = TimeseriesModel(self._video.n_frames, xy_values, 0, 1, f"Audio[{aid}]")
            self._annotations.append(timeseries)

    def load_audio_db(self):
        audio_channels = export_audio_rms_aligned_on_video_frames(
            self._video.path,
            True,
            self._video.fps,
            self._video.n_frames,
        )
        assert len(audio_channels), "No Audio Channel"
        for aid, audio_channel in enumerate(audio_channels):
            min_value = audio_channel.min()
            xy_values = enumerate(map(float, audio_channel))
            timeseries = TimeseriesModel(self._video.n_frames, xy_values, int(min_value), 0, f"Audio[{aid}]")
            self._annotations.append(timeseries)
