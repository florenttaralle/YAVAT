from PyQt6.QtWidgets import QFileDialog, QMessageBox
from src.models.video_file import VideoFile
from src.models.timeline_list import TimelineListModel
import os, json


class SaveAndLoad:
    def __init__(self, video_file: VideoFile, timeline_list: TimelineListModel):
        self._video_file        = video_file
        self._timeline_list     = timeline_list
        self._base_folder       = os.path.dirname(video_file.path)
        self._annotations_path: str|None = None


    def pick_and_load(self):
        filename,  _ = QFileDialog.getOpenFileName(None, "Load YAVAT annotations", 
                                            self._base_folder, 
                                            "YAVAT Annotations (*.json, *.yavat)")
        if filename == '': return
        self.load_file(filename)


    def pick_and_save(self):
        default_path = self._annotations_path if self._annotations_path \
            else os.path.splitext(self._video_file.path)[0] + ".yavat"
        filename, _ = QFileDialog.getSaveFileName(None, "Save AYAT annotations",
                                                default_path,
                                                "YAVAT Annotations (*.json, *.yavat)")
        if filename == '': return
        self.save_file(filename)


    def load_file(self, path: str):
        self._annotations_path = path
        with open(path, 'rt') as json_file:
            data = json.load(json_file)
        
        crt_header = self._video_file.data()
        header = dict(**crt_header) # make a copy
        header.update(data['video'])
        if header != crt_header:
            QMessageBox.warning(None, "Invalid Annotation File", 
                                "Annotation file is incompatible with this video file.", 
                                QMessageBox.StandardButton.Ok)
            return
        self._timeline_list.clear()
        for timeline_data in data['timelines']:
            timeline = self._timeline_list.add(timeline_data["name"])
            for event_data in timeline_data['events']:
                timeline.add(**event_data)


    def save_file(self, path: str):
        self._annotations_path = path
        data = {
            "video":        self._video_file.data(),
            "timelines":    self._timeline_list.data()
        }
        with open(path, 'wt') as json_file:
            json.dump(data, json_file, indent=2)
