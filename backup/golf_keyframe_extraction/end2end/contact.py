"""Contact-point detection — forward search from backswing tops.

Finds the ball-impact frame by searching for the maximum of a tightly
smoothed signal in a window after each backswing.
"""
import numpy as np
from scipy.signal import savgol_filter
from .config import Config


def detect_contact_points(bs_frames, combined, n_pkl, cfg):
    """Find contact-point frame indices by forward search from backswings.

    For each backswing frame, searches forward ``contact_search_min`` to
    ``contact_search_max`` frames on a tightly smoothed signal for the
    maximum — the moment where the hands are fully extended (club meeting
    ball).

    Args:
        bs_frames: 1-D array of backswing-top frame indices.
        combined: Raw combined arc signal.
        n_pkl: Number of keypoint frames in the pickle.
        cfg: ``Config`` instance.

    Returns:
        Tuple of ``(contact_frames, smoothed)`` where *contact_frames* is a
        1-D int array and *smoothed* is the contact-smoothed signal.
    """
    smoothed = savgol_filter(combined, cfg.contact_savgol_window, cfg.contact_savgol_poly)
    contacts = []
    for bf in bs_frames:
        s, e = bf + cfg.contact_search_min, min(bf + cfg.contact_search_max, n_pkl - 1)
        if s >= n_pkl:
            continue
        seg = smoothed[s:e + 1]
        if len(seg) > 0:
            contacts.append(s + np.argmax(seg))
    return np.array(contacts), smoothed
