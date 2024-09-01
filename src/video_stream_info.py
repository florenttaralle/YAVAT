from __future__ import annotations
import os, ffmpeg, attr


@attr.define
class VideoStreamInfo:
    width:          int
    height:         int
    fps:            float
    duration_s:     float
    
    @property
    def n_frames(self) -> int:
        return int(self.duration_s * self.fps)

    @classmethod
    def load(cls, video_path: str) -> VideoStreamInfo:
        if not os.path.exists(video_path):
            raise RuntimeError(f"File Not Found: {video_path}")

        streams         = ffmpeg.probe(video_path)["streams"]
        video_streams   = [stream for stream in streams if stream["codec_type"] == "video"]
        if len(video_streams) != 1:
            raise RuntimeError('No (or multiple) Video Streams')
        video_stream    = video_streams[0]

        return cls(
            video_stream["width"],
            video_stream["height"],
            eval(video_stream["avg_frame_rate"]),
            eval(video_stream["duration"])
        )
