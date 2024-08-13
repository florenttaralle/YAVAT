import os, cv2
from contextlib import ExitStack

def get_fps(video_path: str) -> float:
    if not os.path.exists(video_path):
        raise RuntimeError(f"File Not Found: {video_path}")
    with ExitStack() as on_exit:
        i_stream = cv2.VideoCapture(video_path)
        if not i_stream.isOpened():
            raise RuntimeError(f"Cannot Open Video: {video_path}")
        on_exit.callback(i_stream.release)
        return i_stream.get(cv2.CAP_PROP_FPS)
