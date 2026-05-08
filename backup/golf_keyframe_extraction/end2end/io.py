"""Filesystem boundary — the only module that touches disk.

Loads mmpose keypoint pickles and reads video metadata via OpenCV.
"""
import pickle
import numpy as np
import cv2
from .config import Config


def load_wrist_signals(pkl_path, cfg):
    """Load left/right wrist coordinates and confidence scores from a pickle.

    Reads the mmpose keypoint pickle produced by the pose-estimation stage and
    extracts the x, y, and confidence arrays for both wrists.

    Args:
        pkl_path: Path to the keypoint pickle file.  Expected format is a dict
            mapping ``"frame_0"`` … ``"frame_N"`` to dicts with
            ``"keypoints"`` (17×2) and ``"keypoint_scores"`` (17,) arrays.
        cfg: ``Config`` instance (used for ``left_wrist``, ``right_wrist``
            keypoint indices).

    Returns:
        Tuple of seven arrays/objects:
        ``(x_left, x_right, y_left, y_right, conf_left, conf_right, pkl_data)``
        where each signal has shape ``(N,)`` and ``pkl_data`` is the raw dict.
    """
    with open(pkl_path, "rb") as f:
        data = pickle.load(f)
    n = len(data)
    kps = np.array([data[f"frame_{i}"]["keypoints"] for i in range(n)])
    scs = np.array([data[f"frame_{i}"]["keypoint_scores"] for i in range(n)])
    return (kps[:, cfg.left_wrist, 0], kps[:, cfg.right_wrist, 0],
            kps[:, cfg.left_wrist, 1], kps[:, cfg.right_wrist, 1],
            scs[:, cfg.left_wrist], scs[:, cfg.right_wrist], data)


def read_video_meta(mov_path):
    """Read video metadata (fps and frame count) via OpenCV.

    Args:
        mov_path: Path to the source video file (``.MOV`` or ``.mp4``).

    Returns:
        Tuple of ``(fps, total_frames)`` where *fps* is a float and
        *total_frames* is an int.
    """
    cap = cv2.VideoCapture(mov_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return fps, total_frames
