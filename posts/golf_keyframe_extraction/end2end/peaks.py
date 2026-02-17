"""Peak detection — find backswing-top frame indices from the combined signal.

Splits the old monolithic ``_detect_peaks`` into composable parts:
``find_anchors`` → ``search_and_refine`` → ``detect_peaks`` (convenience wrapper).
"""
import numpy as np
from scipy.signal import savgol_filter, find_peaks
from .config import Config


def backswing_score(peak, smoothed, cfg):
    """Score a candidate frame for how backswing-like it is.

    A real backswing top has a *smooth approach* (club slowly rising) and a
    *sharp departure* (fast downswing).  Follow-throughs are the opposite.
    Lower scores are more backswing-like.

    The score is::

        std(diff(signal[peak - look_behind : peak]))
        - 0.5 * (signal[peak + look_ahead] - signal[peak])

    Args:
        peak: Candidate frame index.
        smoothed: Fine-smoothed combined signal.
        cfg: ``Config`` instance (uses ``look_behind``, ``look_ahead``).

    Returns:
        Float score — lower means more likely a true backswing top.
    """
    behind = smoothed[max(0, peak - cfg.look_behind):peak]
    approach_jitter = np.std(np.diff(behind)) if len(behind) > 2 else 0.0
    ahead = smoothed[peak:min(len(smoothed), peak + cfg.look_ahead)]
    departure_drop = (ahead[-1] - ahead[0]) if len(ahead) > 1 else 0.0
    return approach_jitter - 0.5 * departure_drop


def find_anchors(combined, total_video_frames, cfg):
    """Fine + coarse smooth, end-of-video mask, and anchor detection.

    Args:
        combined: 1-D combined arc signal.
        total_video_frames: Total video frame count (for end-of-video
            masking).  May be ``None`` to skip masking.
        cfg: ``Config`` instance.

    Returns:
        Tuple of ``(anchors, smoothed, coarse)`` where *anchors* is a 1-D
        int array of anchor peak indices, *smoothed* is the fine-smoothed
        signal, and *coarse* is the coarse-smoothed signal.
    """
    smoothed = savgol_filter(combined, cfg.savgol_window, cfg.savgol_poly)
    coarse = savgol_filter(combined, cfg.coarse_window, cfg.coarse_poly)
    neg = -smoothed
    if total_video_frames is not None:
        ms = int(total_video_frames * 0.95)
        if ms < len(neg):
            neg[ms:] = np.min(neg)
    anchors, _ = find_peaks(neg, prominence=cfg.peak_prominence, distance=cfg.peak_distance)
    return anchors, smoothed, coarse


def search_and_refine(anchors, smoothed, coarse, cfg):
    """Backward search, scoring, and apex refinement for each anchor.

    For each anchor, walks back up to ``search_back`` frames on the coarse
    signal to find zero-crossing candidates, scores them with
    ``backswing_score``, and refines the winner forward on the fine signal.

    Args:
        anchors: 1-D array of anchor peak indices.
        smoothed: Fine-smoothed combined signal.
        coarse: Coarse-smoothed combined signal.
        cfg: ``Config`` instance.

    Returns:
        1-D int array of refined peak frame indices.
    """
    results = []
    for anchor in anchors:
        ss = max(0, anchor - cfg.search_back)
        d = np.diff(coarse[ss:anchor + 1])
        candidates = [ss + i + 1 for i in range(len(d) - 1) if d[i] <= 0 and d[i + 1] > 0]
        if anchor not in candidates:
            candidates.append(anchor)
        best = candidates[np.argmin([backswing_score(c, smoothed, cfg) for c in candidates])]
        refine = smoothed[best:min(len(smoothed), best + cfg.refine_window + 1)]
        results.append(best + int(np.argmin(refine)))
    return np.array(results)


def detect_peaks(combined, total_video_frames, cfg):
    """Find backswing-top frame indices from the combined signal.

    Convenience wrapper that calls ``find_anchors`` then
    ``search_and_refine``.

    Args:
        combined: 1-D combined arc signal.
        total_video_frames: Total video frame count (for end-of-video
            masking).  May be ``None`` to skip masking.
        cfg: ``Config`` instance.

    Returns:
        Tuple of ``(peak_frames, smoothed)`` where *peak_frames* is a 1-D
        int array and *smoothed* is the fine-smoothed signal.
    """
    anchors, smoothed, coarse = find_anchors(combined, total_video_frames, cfg)
    if len(anchors) == 0:
        return anchors, smoothed
    peak_frames = search_and_refine(anchors, smoothed, coarse, cfg)
    return peak_frames, smoothed
