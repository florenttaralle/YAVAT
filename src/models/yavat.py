from __future__ import annotations
import os, json
from typing import ClassVar
from hashlib import sha256

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor

from src.models.video import VideoModel, TimeWindowModel
from src.models.annotation import AnnotationGroupModel, annotation_factory

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
    
    @staticmethod
    def _compute_json_hash(json_content: str) -> str:
        return sha256(json_content.encode("utf-8")).hexdigest()        
    
    def serialize(self) -> tuple[str, str]:
        content = {
            self.VERSION_KEY:   str(YAVAT_VERSION), 
            "video":            self._video.serialize(),
            "annotations":      self._annotations.serialize(),
        }
        json_content = json.dumps(content, indent=2)
        json_hash = self._compute_json_hash(json_content)
        return json_content, json_hash

    def save(self, yavat_path: str|None) -> str:
        # update yavat path if one provided
        if yavat_path is not None:
            self._set_yavat_path(yavat_path)
        # ensure there is a path defined
        assert self._yavat_path is not None
        # serialize and compute hash
        json_content, json_hash = self.serialize()
        # save serialized content
        with open(self._yavat_path, 'wt') as annotation_file:
            annotation_file.write(json_content)
        return json_hash
    
    @classmethod
    def load(cls, path: str, default_color: QColor) -> tuple[YavatModel, str|None]:
        """" load either from video file or yavat path """
        ext = os.path.splitext(path)[1].lower()
        if ext in {'.yavat', '.yvt'}:
            yavat_path = path
            video_path = None
        else:
            video_path = path
            yavat_path = cls.default_path(path)
            if not os.path.exists(yavat_path):
                yavat_path = None

        if yavat_path is not None:
            assert os.path.exists(yavat_path), f"Yavat File Not Found: {yavat_path}"
            with open(yavat_path, 'rt', encoding='utf-8') as yavat_file:
                json_content = yavat_file.read()
                json_hash = cls._compute_json_hash(json_content)
                data = json.loads(json_content)

            assert cls.VERSION_KEY in data, 'Not a Yavat Annotation File'
            version     = VersionModel.from_str(data.get(cls.VERSION_KEY, '0.0.0'))
            assert version.compatible(YAVAT_VERSION), f"Yavat Annotation File Version {str(version)} not compatible with Yavat Application Version {str(YAVAT_VERSION)}"
            annotations = annotation_factory(**data["annotations"])

            if video_path is None:
                video_path = os.path.join(os.path.dirname(yavat_path), data['video']['video_filename'])
                assert os.path.exists(video_path), f"Video Not Found: {video_path}"

        else:
            annotations = None
            json_hash = None

        video = VideoModel(video_path)
        assert not video._error, video._error
        
        if annotations is None:
            annotations = AnnotationGroupModel(video.n_frames, "root", default_color)
        
            # # build fake annotations to test the view
            # tl0 = TimelineModel(video.n_frames, "First Timeline", annotations.color)
            # annotations.attach(tl0)
            # grp0 = AnnotationGroupModel(video.n_frames, "First Group", annotations.color)
            # annotations.attach(grp0)
            # tl1 = TimelineModel(video.n_frames, "Second Timeline", grp0.color)
            # grp0.attach(tl1)
            # tl2 = TimelineModel(video.n_frames, "Third Timeline", grp0.color)
            # grp0.attach(tl2)
            # tl3 = TimelineModel(video.n_frames, "Fourth Timeline", annotations.color)
            # annotations.attach(tl3)
        
        model = cls(video, annotations, yavat_path)
        
        return model, json_hash
