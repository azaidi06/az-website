"""Pure signal transforms — numpy in, numpy out, no side effects.

Interpolates low-confidence keypoint frames and builds the combined
arc signal used by the rest of the pipeline.
"""
import numpy as np


def interp_low_conf(signal, conf, threshold):
    """Replace low-confidence frames with linearly interpolated values.

    mmpose occasionally drops confidence on individual frames, producing
    spikes in the wrist trajectory.  This replaces those frames using
    ``numpy.interp`` from the nearest high-confidence neighbors.

    Args:
        signal: 1-D array of coordinate values (e.g. wrist x).
        conf: 1-D confidence scores, same length as *signal*.
        threshold: Frames with confidence below this are interpolated.

    Returns:
        A copy of *signal* with low-confidence values replaced.  If fewer than
        2 good frames exist, returns an unmodified copy.
    """
    bad = conf < threshold
    if not np.any(bad):
        return signal.copy()
    good = ~bad
    if np.sum(good) < 2:
        return signal.copy()
    out = signal.copy()
    out[np.where(bad)[0]] = np.interp(np.where(bad)[0], np.where(good)[0], signal[good])
    return out


def build_combined(x_l, x_r, y_l, y_r, c_l, c_r, conf_threshold):
    """Build the single-channel arc signal from wrist arrays.

    Interpolates low-confidence frames on all four coordinate channels,
    then computes ``(x_L + x_R) / 2 + (y_L + y_R) / 2``.  At the top of
    the backswing both x and y are low (hands high and behind); at contact
    they are high (hands extended forward).

    Args:
        x_l: 1-D array of left-wrist x coordinates.
        x_r: 1-D array of right-wrist x coordinates.
        y_l: 1-D array of left-wrist y coordinates.
        y_r: 1-D array of right-wrist y coordinates.
        c_l: 1-D array of left-wrist confidence scores.
        c_r: 1-D array of right-wrist confidence scores.
        conf_threshold: Confidence threshold for interpolation.

    Returns:
        1-D float array — the combined arc signal.
    """
    x_l = interp_low_conf(x_l, c_l, conf_threshold)
    x_r = interp_low_conf(x_r, c_r, conf_threshold)
    y_l = interp_low_conf(y_l, c_l, conf_threshold)
    y_r = interp_low_conf(y_r, c_r, conf_threshold)
    return (x_l + x_r) / 2.0 + (y_l + y_r) / 2.0
