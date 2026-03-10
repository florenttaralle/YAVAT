import os

import av
import numpy as np


def export_audio_rms_aligned_on_video_frames(video_path: str, db_scale: bool, video_fps: float|None=None, n_frames: int|None=None) -> list[np.ndarray]:
    assert os.path.exists(video_path), 'Video File Not Found'
    container = av.open(video_path)

    # get video fps
    if video_fps is None:
        assert len(container.streams.video), "No Video Stream"
        video_stream = container.streams.video[0]
        video_fps = float(video_stream.average_rate)

    per_audio_stream_rms = [
        extract_audio_rms(container, audio_stream, video_fps, n_frames)
        for audio_stream in container.streams.audio
    ]
 
    if db_scale:
        per_audio_stream_rms = [20 * np.log10(rms + 1e-12) for rms in per_audio_stream_rms]
 
    return per_audio_stream_rms


def extract_audio_rms(container, audio_stream, video_fps: float, n_frames: int|None=None) -> np.ndarray:
    sample_rate = float(audio_stream.rate)
    sumsq_by_frame = np.array([], dtype=np.float64)
    count_by_frame = np.array([], dtype=np.int64)
    t0_s = None

    for frame in container.decode(audio_stream):
        if frame.pts is None:
            continue

        samples = frame.to_ndarray()

        # Collapse multi-channel audio to mono before RMS.
        if samples.ndim > 1:
            samples = samples.mean(axis=0)
        samples = samples.astype(np.float64, copy=False)
        if samples.size == 0:
            continue

        frame_start_s = float(frame.pts * frame.time_base)
        if t0_s is None:
            t0_s = frame_start_s
        frame_start_s -= t0_s
        sample_times_s = frame_start_s + (np.arange(samples.size, dtype=np.float64) / sample_rate)
        # Keep the same rounding rule used by VideoModel.to_frame_id.
        frame_ids = np.rint(sample_times_s * video_fps).astype(np.int64)
        valid = frame_ids >= 0
        if n_frames is not None:
            valid &= (frame_ids < n_frames)
        if not np.any(valid):
            continue
        frame_ids = frame_ids[valid]
        sample_values = samples[valid]

        sumsq = np.bincount(frame_ids, weights=sample_values * sample_values)
        count = np.bincount(frame_ids)
        target_size = max(sumsq_by_frame.size, sumsq.size)
        if target_size > sumsq_by_frame.size:
            sumsq_by_frame = np.pad(sumsq_by_frame, (0, target_size - sumsq_by_frame.size))
            count_by_frame = np.pad(count_by_frame, (0, target_size - count_by_frame.size))
        sumsq_by_frame[:sumsq.size] += sumsq
        count_by_frame[:count.size] += count

    if sumsq_by_frame.size == 0:
        return np.array([], dtype=np.float32)

    rms = np.zeros_like(sumsq_by_frame, dtype=np.float64)
    valid = count_by_frame > 0
    rms[valid] = np.sqrt(sumsq_by_frame[valid] / count_by_frame[valid])
    return rms.astype(np.float32)
