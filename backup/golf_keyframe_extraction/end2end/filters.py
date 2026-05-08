"""Composable filter pipeline — five sequential post-processing filters.

Each filter takes peaks (and context) and returns ``(peaks, log_entries)``.
``run_all`` chains them in order.
"""
import numpy as np
from .config import Config


def dedup(peaks):
    """Remove duplicate frame indices and return a sorted array.

    Args:
        peaks: 1-D array of frame indices (may contain duplicates).

    Returns:
        Tuple of ``(deduped, log)`` where *deduped* is a sorted 1-D int
        array and *log* is a list with a message if duplicates were removed.
    """
    log = []
    if len(peaks) == 0:
        return peaks, log
    before = len(peaks)
    peaks = np.array(sorted(set(peaks.tolist())))
    if len(peaks) != before:
        log.append(f"Dedup: removed {before - len(peaks)} duplicate(s)")
    return peaks, log


def trim_end(peaks, total_frames, end_of_video_pct):
    """Drop peaks in the last portion of the video.

    Args:
        peaks: 1-D array of peak frame indices.
        total_frames: Total video frame count.
        end_of_video_pct: Fraction of video at the end to suppress.

    Returns:
        Tuple of ``(filtered_peaks, log)``.
    """
    log = []
    cutoff = int(total_frames * (1.0 - end_of_video_pct))
    mask = peaks < cutoff
    if not np.all(mask):
        log.append(f"End-of-video: removed {np.sum(~mask)} peak(s) past frame {cutoff}")
        peaks = peaks[mask]
    return peaks, log


def merge_close(peaks, smoothed, min_swing_gap):
    """Merge peaks closer than *min_swing_gap*, keeping the deeper one.

    Args:
        peaks: 1-D array of peak frame indices.
        smoothed: Fine-smoothed combined signal.
        min_swing_gap: Minimum frames between peaks.

    Returns:
        Tuple of ``(merged_peaks, log)``.
    """
    log = []
    merged, removed_close = [peaks[0]], []
    for p in peaks[1:]:
        if p - merged[-1] < min_swing_gap:
            prev = merged[-1]
            if smoothed[p] < smoothed[prev]:
                removed_close.append(prev); merged[-1] = p
            else:
                removed_close.append(p)
        else:
            merged.append(p)
    if removed_close:
        log.append(f"Too-close: removed {len(removed_close)} peak(s) within {min_swing_gap} frames")
    return np.array(merged), log


def mad_outlier(peaks, smoothed, mad_thresh, mad_floor, min_peaks):
    """Remove peaks whose smoothed value is a MAD outlier.

    Args:
        peaks: 1-D array of peak frame indices.
        smoothed: Fine-smoothed combined signal.
        mad_thresh: MAD multiplier for the threshold.
        mad_floor: Minimum MAD value to prevent over-tight filtering.
        min_peaks: Skip filtering if fewer peaks than this.

    Returns:
        Tuple of ``(filtered_peaks, log)``.
    """
    log = []
    if len(peaks) < min_peaks:
        return peaks, log
    vals = smoothed[peaks]
    med = np.median(vals)
    mad = max(np.median(np.abs(vals - med)), mad_floor)
    if mad > 0:
        thresh = med + mad_thresh * mad
        om = vals > thresh
        if np.any(om):
            log.append(f"MAD: removed {np.sum(om)} peak(s) with x+y > {thresh:.0f} (med={med:.0f}, MAD={mad:.0f})")
            peaks = peaks[~om]
    return peaks, log


def followthrough(peaks, pkl_data, cfg):
    """Reject follow-through peaks using wrist-to-shoulder horizontal offset.

    Real backswings have hands behind the body (negative offset);
    follow-throughs have hands in front.  Peaks with offset more than
    ``xoff_mad_thresh`` MADs above median are removed.

    Args:
        peaks: 1-D array of peak frame indices.
        pkl_data: Full keypoint dictionary (needed for shoulder positions).
        cfg: ``Config`` instance.

    Returns:
        Tuple of ``(filtered_peaks, log)``.
    """
    log = []
    if pkl_data is None or len(peaks) < cfg.xy_outlier_min_peaks:
        return peaks, log
    offsets = np.empty(len(peaks))
    for i, p in enumerate(peaks):
        kp = np.array(pkl_data[f"frame_{p}"]["keypoints"])
        offsets[i] = (kp[cfg.left_wrist][0] + kp[cfg.right_wrist][0]) / 2 - \
                     (kp[cfg.left_shoulder][0] + kp[cfg.right_shoulder][0]) / 2
    med_off = np.median(offsets)
    mad_off = max(np.median(np.abs(offsets - med_off)), cfg.xoff_mad_floor)
    thresh_off = med_off + cfg.xoff_mad_thresh * mad_off
    om = offsets > thresh_off
    if np.any(om):
        log.append(f"Follow-through: removed {np.sum(om)} peak(s) with x_offset > {thresh_off:.0f}")
        peaks = peaks[~om]
    return peaks, log


def run_all(peaks, smoothed, total_frames, pkl_data, cfg):
    """Chain all five filters in order.

    Filter order: dedup → end-of-video trim → too-close merge →
    MAD x+y outlier → follow-through rejection.

    Args:
        peaks: 1-D array of candidate peak frame indices.
        smoothed: Fine-smoothed combined signal.
        total_frames: Total video frame count.
        pkl_data: Full keypoint dictionary (needed for follow-through
            filter).
        cfg: ``Config`` instance.

    Returns:
        Tuple of ``(filtered_peaks, log)`` where *filtered_peaks* is a 1-D
        int array and *log* is a list of human-readable strings describing
        what each filter removed.
    """
    log = []

    peaks, l = dedup(peaks)
    log.extend(l)
    if len(peaks) == 0:
        return peaks, log

    peaks, l = trim_end(peaks, total_frames, cfg.end_of_video_pct)
    log.extend(l)
    if len(peaks) == 0:
        return peaks, log

    peaks, l = merge_close(peaks, smoothed, cfg.min_swing_gap)
    log.extend(l)

    peaks, l = mad_outlier(peaks, smoothed, cfg.xy_outlier_mad_thresh,
                           cfg.xy_outlier_mad_floor, cfg.xy_outlier_min_peaks)
    log.extend(l)

    peaks, l = followthrough(peaks, pkl_data, cfg)
    log.extend(l)

    return peaks, log
