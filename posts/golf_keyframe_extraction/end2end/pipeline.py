"""Thin orchestrators — glue I/O, signal, peaks, filters, and contact.

Public API:
    detect_backswings(pkl_path, mov_path, config=None) -> DetectionResult
    detect_contacts(backswing_result, config=None) -> ContactResult
"""
import os
from .config import Config, DetectionResult, ContactResult
from . import io as _io
from . import signal as _signal
from . import peaks as _peaks
from . import filters as _filters
from . import contact as _contact


def _build_combined_signal(pkl_path, cfg):
    """Load wrist signals and build the combined arc signal.

    Args:
        pkl_path: Path to the keypoint pickle file.
        cfg: ``Config`` instance.

    Returns:
        Tuple of ``(combined, pkl_data)`` where *combined* is a 1-D float
        array and *pkl_data* is the raw keypoint dict.
    """
    x_l, x_r, y_l, y_r, c_l, c_r, data = _io.load_wrist_signals(pkl_path, cfg)
    combined = _signal.build_combined(x_l, x_r, y_l, y_r, c_l, c_r, cfg.conf_threshold)
    return combined, data


def detect_backswings(pkl_path, mov_path, config=None):
    """Detect top-of-backswing frames in a golf video.

    This is the main public entry point for backswing detection.  It runs
    the full pipeline: load keypoints → build combined signal → detect peaks
    → filter → return a ``DetectionResult``.

    Args:
        pkl_path: Path to the mmpose keypoint pickle for this video.
        mov_path: Path to the source video file (``.MOV`` or ``.mp4``).
        config: Optional ``Config`` override.  Uses defaults if ``None``.

    Returns:
        A ``DetectionResult`` containing the detected peak frames, smoothed
        signals, filter log, and metadata.

    Example:
        >>> from end2end import detect_backswings
        >>> result = detect_backswings("video/keypoints/IMG_1171.pkl",
        ...                            "video/IMG_1171.mp4")
        >>> print(f"{result.n_swings} swings detected")
        4 swings detected
        >>> result.peak_frames
        array([1527, 4166, 6433, 8337])
    """
    cfg = config or Config()
    combined, pkl_data = _build_combined_signal(pkl_path, cfg)
    fps, total_frames = _io.read_video_meta(mov_path)
    peak_frames, smoothed = _peaks.detect_peaks(combined, total_frames, cfg)
    peak_frames, flog = _filters.run_all(peak_frames, smoothed, total_frames, pkl_data, cfg)
    return DetectionResult(
        name=os.path.splitext(os.path.basename(mov_path))[0],
        peak_frames=peak_frames, smoothed=smoothed, combined=combined,
        fps=fps, total_frames=total_frames, filter_log=flog,
        pkl_data=pkl_data, pkl_path=pkl_path, mov_path=mov_path)


def detect_contacts(backswing_result, config=None):
    """Detect ball-contact frames given an existing backswing result.

    For each detected backswing, searches forward on a tightly smoothed
    signal for the maximum — the moment of impact where the hands are fully
    extended.

    Args:
        backswing_result: A ``DetectionResult`` from ``detect_backswings``.
        config: Optional ``Config`` override.  Uses defaults if ``None``.

    Returns:
        A ``ContactResult`` containing the contact frames, the upstream
        backswing result, and the contact-smoothed signal.

    Example:
        >>> from end2end import detect_backswings, detect_contacts
        >>> bs = detect_backswings("video/keypoints/IMG_1171.pkl",
        ...                        "video/IMG_1171.mp4")
        >>> ct = detect_contacts(bs)
        >>> print(f"{ct.n_contacts} contact points")
        4 contact points
    """
    cfg = config or Config()
    br = backswing_result
    cf, sm = _contact.detect_contact_points(br.peak_frames, br.combined, len(br.pkl_data), cfg)
    cf, clog = _filters.dedup(cf)
    return ContactResult(name=br.name, contact_frames=cf, backswing_result=br, smoothed=sm, filter_log=clog)
