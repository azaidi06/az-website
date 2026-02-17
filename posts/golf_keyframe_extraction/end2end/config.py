"""Configuration and result dataclasses for the detection pipeline.

Provides a single frozen ``Config`` for all tunable parameters and two mutable
result containers (``DetectionResult``, ``ContactResult``) returned by the
detection functions.
"""

from dataclasses import dataclass, field
import numpy as np


@dataclass(frozen=True)
class Config:
    """Frozen configuration for the backswing / contact detection pipeline.

    All defaults are tuned on two datasets (7 + 10 videos, 92 total swings at
    60 fps).  Frame-count parameters assume 60 fps — scale proportionally for
    other frame rates.

    Attributes:
        savgol_window: Fine Savitzky-Golay window in frames (~150 ms at 60 fps).
            Removes frame-to-frame jitter while preserving swing shape.
        savgol_poly: Polynomial order for the fine Savitzky-Golay filter.
        coarse_window: Coarse Savitzky-Golay window in frames (~1.0 s at
            60 fps).  Wide enough to flatten within-swing oscillations so
            ``find_peaks`` can locate swing *regions*.
        coarse_poly: Polynomial order for the coarse Savitzky-Golay filter.
        peak_prominence: Minimum prominence (pixels) for ``find_peaks`` on the
            inverted signal.  A swing must produce at least this much dip.
        peak_distance: Minimum distance (frames, ~8.3 s) between anchor peaks.
        look_behind: Frames behind an anchor examined when scoring backswing
            candidates (approach jitter).
        look_ahead: Frames ahead of an anchor examined when scoring backswing
            candidates (departure drop).
        search_back: Maximum frames (~10 s) to search backward from an anchor
            on the coarse signal for the true backswing candidate.
        refine_window: Forward search window (frames, ~250 ms) on the fine
            signal to correct the coarse-smoothing bias.
        min_swing_gap: Merge threshold (frames, ~10 s) — peaks closer than
            this are merged, keeping the deeper one.
        end_of_video_pct: Fraction of video at the end to suppress (camera
            noise / golfer walking away).
        xy_outlier_mad_thresh: MAD multiplier for the x+y outlier filter.
        xy_outlier_min_peaks: Minimum peak count before MAD filtering is
            applied.
        xy_outlier_mad_floor: MAD floor (pixels) to prevent an unreasonably
            tight threshold when swings are very consistent.
        xoff_mad_thresh: MAD multiplier for the follow-through rejection
            filter (wrist-to-shoulder horizontal offset).
        xoff_mad_floor: MAD floor (pixels) for the follow-through filter.
        left_wrist: COCO-17 keypoint index for the left wrist.
        right_wrist: COCO-17 keypoint index for the right wrist.
        left_shoulder: COCO-17 keypoint index for the left shoulder.
        right_shoulder: COCO-17 keypoint index for the right shoulder.
        conf_threshold: Minimum keypoint confidence; frames below this are
            linearly interpolated.
        contact_search_min: Minimum frames (~170 ms) after a backswing to
            begin searching for contact.
        contact_search_max: Maximum frames (~1.5 s) after a backswing to
            search for contact.
        contact_savgol_window: Savitzky-Golay window (frames, ~83 ms) for
            contact-point smoothing.
        contact_savgol_poly: Polynomial order for the contact smoother.
        min_expected_swings: Flag a video if fewer swings than this are found.
        max_expected_swings: Flag a video if more swings than this are found.
        low_conf_window: Half-window (frames) around a peak for confidence
            checking.
        low_conf_threshold: Mean wrist confidence below this triggers a flag.
        close_gap_seconds: Flag if two successive swings are closer than this
            (seconds).
        flag_mad_threshold: MAD z-score above which a peak's x+y value is
            flagged as suspicious.
        downswing_outlier_frames: Frame threshold used when exporting CSV to
            flag unusually long downswings.
    """

    # Smoothing
    savgol_window: int = 9
    savgol_poly: int = 3
    coarse_window: int = 61
    coarse_poly: int = 3
    # Peak detection
    peak_prominence: int = 300
    peak_distance: int = 500
    look_behind: int = 60
    look_ahead: int = 30
    search_back: int = 600
    refine_window: int = 15
    # Post-processing filters
    min_swing_gap: int = 600
    end_of_video_pct: float = 0.03
    xy_outlier_mad_thresh: float = 3.0
    xy_outlier_min_peaks: int = 3
    xy_outlier_mad_floor: int = 50
    xoff_mad_thresh: float = 3.0
    xoff_mad_floor: int = 20
    # Keypoint constants
    left_wrist: int = 9
    right_wrist: int = 10
    left_shoulder: int = 5
    right_shoulder: int = 6
    conf_threshold: float = 0.3
    # Contact detection
    contact_search_min: int = 10
    contact_search_max: int = 90
    contact_savgol_window: int = 5
    contact_savgol_poly: int = 2
    # Problem flagging
    min_expected_swings: int = 2
    max_expected_swings: int = 15
    low_conf_window: int = 5
    low_conf_threshold: float = 0.4
    close_gap_seconds: float = 8.0
    flag_mad_threshold: float = 2.0
    # CSV export
    downswing_outlier_frames: int = 40


@dataclass
class DetectionResult:
    """Container for backswing detection output from a single video.

    Attributes:
        name: Video filename stem (e.g. ``"IMG_1171"``).
        peak_frames: 1-D array of frame indices for detected backswing tops.
        smoothed: Fine-smoothed combined signal (same length as keypoint
            frames).
        combined: Raw combined signal ``(x_L + x_R)/2 + (y_L + y_R)/2``
            after low-confidence interpolation.
        fps: Video frame rate.
        total_frames: Total number of video frames.
        filter_log: Human-readable log of which filters fired and how many
            peaks they removed.
        pkl_data: Full keypoint dictionary loaded from the pickle file.
        pkl_path: Path to the keypoint pickle file.
        mov_path: Path to the source video file.
    """

    name: str
    peak_frames: np.ndarray
    smoothed: np.ndarray
    combined: np.ndarray
    fps: float
    total_frames: int
    filter_log: list = field(default_factory=list)
    pkl_data: dict = field(default=None, repr=False)
    pkl_path: str = ""
    mov_path: str = ""

    @property
    def n_swings(self):
        """Number of detected backswing peaks."""
        return len(self.peak_frames)


@dataclass
class ContactResult:
    """Container for contact-point detection output from a single video.

    Attributes:
        name: Video filename stem.
        contact_frames: 1-D array of frame indices for detected contact
            points.
        backswing_result: The upstream ``DetectionResult`` that seeded the
            contact search.
        smoothed: Tightly smoothed combined signal used for contact detection.
        filter_log: Human-readable log of any deduplication that occurred.
    """

    name: str
    contact_frames: np.ndarray
    backswing_result: DetectionResult
    smoothed: np.ndarray
    filter_log: list = field(default_factory=list)

    @property
    def n_contacts(self):
        """Number of detected contact points."""
        return len(self.contact_frames)
