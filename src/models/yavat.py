from __future__ import annotations
import os, json
from typing import ClassVar
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor

from src.models.video import VideoModel, TimeWindowModel
from src.models.annotation import AnnotationGroupModel, TimelineModel

from src.version import YAVAT_VERSION, VersionModel

class YavatModel(QObject):
    yavat_path_changed  = pyqtSignal(object)
    "SIGNAL: yavat_path_changed(path: str|None)"

    VERSION_KEY: ClassVar[str] = "yavat_version"

    def __init__(self, video: VideoModel, annotations: AnnotationGroupModel, yavat_path: str|None):
        QObject.__init__(self)
        self._video             = video
        self._annotations       = annotations
        self._yavat_path        = yavat_path
        self._video.setParent(self)

    @property
    def video(self) -> VideoModel:
        return self._video

    @property
    def time_window(self) -> TimeWindowModel|None:
        return self._video.time_window if self._video is not None else None

    @property
    def annotations(self) -> AnnotationGroupModel:
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
    
    def save(self, yavat_path: str|None):
        if yavat_path is not None:
            self._set_yavat_path(yavat_path)
        assert self._yavat_path is not None
        content = {
            self.VERSION_KEY:   str(self.YAVAT_VERSION), 
            "video":            self._video.serialize(),
            "annotations":      self._annotations.serialize(),
        }
        with open(self._yavat_path, 'wt') as annotation_file:
            json.dump(content, annotation_file, indent=2)

    @classmethod
    def load(cls, path: str, default_color: QColor):
        """" load either from video file or yavat path """
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
                data = json.load(yavat_file)

            assert cls.VERSION_KEY in data, 'Not a Yavat Annotation File'
            version     = VersionModel.from_str(data.get(cls.VERSION_KEY, '0.0.0'))
            assert version.compatible(YAVAT_VERSION), f"Yavat Annotation File Version {str(version)} not compatible with Yavat Application Version {str(YAVAT_VERSION)}"
            annotations = AnnotationGroupModel.parse(**data["annotations"])

            if video_path is None:
                video_path = os.path.join(os.path.dirname(yavat_path), data['video']['video_filename'])
                assert os.path.exists(video_path), f"Video Not Found: {video_path}"

        else:
            annotations = None

        video = VideoModel(video_path)
        assert not video._error, video._error
        
        if annotations is None:
            annotations = AnnotationGroupModel(video.n_frames, "root", default_color)
        
            # build fake annotations to test the view
            tl0 = TimelineModel(video.n_frames, "First Timeline", annotations.color)
            annotations.attach(tl0)
            grp0 = AnnotationGroupModel(video.n_frames, "First Group", annotations.color)
            annotations.attach(grp0)
            tl1 = TimelineModel(video.n_frames, "Second Timeline", grp0.color)
            grp0.attach(tl1)
            tl2 = TimelineModel(video.n_frames, "Third Timeline", grp0.color)
            grp0.attach(tl2)
            tl3 = TimelineModel(video.n_frames, "Fourth Timeline", annotations.color)
            annotations.attach(tl3)
        
        return cls(video, annotations, yavat_path)
