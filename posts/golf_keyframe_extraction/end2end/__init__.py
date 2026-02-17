"""End-to-end golf swing detection pipeline.

Automatically finds the top-of-backswing and ball-contact frames in golf
videos using wrist keypoints from mmpose and Savitzky-Golay signal
processing.  No ML model, no GPU, no training data — just wrist positions
and a pair of smoothing filters.

Typical usage::

    from end2end import detect_backswings, detect_contacts, Config

    result = detect_backswings("keypoints/IMG_1171.pkl", "IMG_1171.mp4")
    contacts = detect_contacts(result)

See the ``pipeline`` module for the full pipeline and the ``config`` module
for all tunable parameters.
"""
from end2end.pipeline import detect_backswings, detect_contacts
from end2end.config import Config, DetectionResult, ContactResult

__all__ = [
    "detect_backswings",
    "detect_contacts",
    "Config",
    "DetectionResult",
    "ContactResult",
]
