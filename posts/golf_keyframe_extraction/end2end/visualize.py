"""Visualization helpers — skeleton grids, signal plots, and clip extraction.

All output is file-based (PNG images, MP4 clips).  Matplotlib uses the
``"Agg"`` backend so no display is required.
"""
import os
import numpy as np
import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.style.use("dark_background")

#: COCO-17 skeleton connectivity as ``(joint_a, joint_b)`` pairs.
COCO_SKELETON = [
    (0,1),(0,2),(1,3),(2,4),(5,6),(5,7),(7,9),(6,8),(8,10),
    (5,11),(6,12),(11,12),(11,13),(13,15),(12,14),(14,16)]

#: BGR colour for each limb — head/face grey, torso green, left arm yellow,
#: right arm cyan, left leg red, right leg blue.
LIMB_COLORS = {
    (0,1):(200,200,200),(0,2):(200,200,200),(1,3):(200,200,200),(2,4):(200,200,200),
    (5,6):(0,200,0),(5,7):(255,255,0),(7,9):(255,255,0),
    (6,8):(0,255,255),(8,10):(0,255,255),
    (5,11):(0,200,0),(6,12):(0,200,0),(11,12):(0,200,0),
    (11,13):(255,100,100),(13,15):(255,100,100),
    (12,14):(100,100,255),(14,16):(100,100,255)}
_LW, _RW = 9, 10


def draw_skeleton(frame, keypoints, scores):
    """Draw a COCO-17 skeleton overlay on a video frame.

    Joints with confidence > 0.1 are drawn; wrist keypoints are highlighted
    with large magenta circles and labelled "L" / "R".

    Args:
        frame: BGR image array (H×W×3).
        keypoints: Keypoint array of shape ``(17, 2)`` — ``(x, y)`` per joint.
        scores: Confidence array of shape ``(17,)``.

    Returns:
        A copy of *frame* with the skeleton drawn on it.
    """
    img = frame.copy()
    kp = np.array(keypoints, dtype=np.int32)
    for (a, b) in COCO_SKELETON:
        if scores[a] > 0.1 and scores[b] > 0.1:
            cv2.line(img, tuple(kp[a]), tuple(kp[b]), LIMB_COLORS.get((a,b),(200,200,200)), 2, cv2.LINE_AA)
    for i, (pt, sc) in enumerate(zip(kp, scores)):
        if sc > 0.1:
            c, r = ((255,0,255), 12) if i in (_LW, _RW) else ((0,255,0), 4)
            cv2.circle(img, tuple(pt), r, c, -1, cv2.LINE_AA)
    for idx, label in [(_LW, "L"), (_RW, "R")]:
        if scores[idx] > 0.1:
            cv2.putText(img, label, (kp[idx][0]+15, kp[idx][1]-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,0,255), 2, cv2.LINE_AA)
    return img


def make_grid(frames, pkl_data, mov_path, fps, title, out_path):
    """Render a grid of skeleton-overlaid video frames and save as PNG.

    Arranges frames in a 4-column grid.  Each cell shows the video frame at
    the given index with the COCO-17 skeleton drawn on top.

    Args:
        frames: 1-D array of frame indices to render.
        pkl_data: Keypoint dictionary (``frame_N`` → keypoints/scores).
        mov_path: Path to the source video file.
        fps: Video frame rate (used in per-cell time labels).
        title: Figure suptitle.
        out_path: Destination PNG path.

    Returns:
        *out_path* on success, or ``None`` if *frames* is empty.
    """
    if len(frames) == 0:
        return None
    cap = cv2.VideoCapture(mov_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    ncols = 4
    nrows = max(1, int(np.ceil(len(frames) / ncols)))
    fig, axes = plt.subplots(nrows, ncols, figsize=(5*ncols, 8*nrows))
    if nrows == 1:
        axes = np.array(axes).reshape(1, -1)
    axes = axes.flatten()
    for i, pf in enumerate(frames):
        cap.set(cv2.CAP_PROP_POS_FRAMES, min(pf, total-1))
        ret, frame = cap.read()
        if not ret:
            axes[i].set_title(f"Frame {pf} (read failed)"); axes[i].axis("off"); continue
        fd = pkl_data[f"frame_{pf}"]
        axes[i].imshow(cv2.cvtColor(draw_skeleton(frame, fd["keypoints"], fd["keypoint_scores"]), cv2.COLOR_BGR2RGB))
        axes[i].set_title(f"Frame {pf}  ({pf/fps:.1f}s)", fontsize=11, fontweight="bold")
        axes[i].axis("off")
    for j in range(len(frames), len(axes)):
        axes[j].axis("off")
    fig.suptitle(title, fontsize=16, fontweight="bold")
    fig.tight_layout(rect=[0,0,1,0.97])
    fig.savefig(out_path, dpi=90, bbox_inches="tight")
    plt.close(fig); cap.release()
    return out_path


def make_signal_plot(result, out_dir, contact_result=None):
    """Plot the combined signal with detected landmarks and save as PNG.

    Shows the raw and smoothed combined signal with backswing tops marked as
    red triangles.  If *contact_result* is provided, contact points are added
    as green triangles with arrows connecting each backswing–contact pair.

    Args:
        result: ``DetectionResult`` for the video.
        out_dir: Directory to save the output PNG.
        contact_result: Optional ``ContactResult``.  When provided the plot
            uses its smoother and includes contact markers.

    Returns:
        Path to the saved PNG file.
    """
    br = contact_result.backswing_result if contact_result else result
    t = np.arange(len(br.combined)) / br.fps
    sm = contact_result.smoothed if contact_result else result.smoothed
    fig, ax = plt.subplots(figsize=(16, 5))
    ax.plot(t, br.combined, color="lightgray", linewidth=0.5, label="Raw (x+y)")
    ax.plot(t, sm, color="steelblue", linewidth=1.2, label="Smoothed")
    ax.invert_yaxis()
    pf = br.peak_frames
    if len(pf) > 0:
        ax.plot(pf/br.fps, sm[pf], "rv", markersize=10, label="Backswing top")
        for p in pf:
            ax.axvline(p/br.fps, color="red", alpha=0.3, linewidth=0.8)
            ax.annotate(str(p), (p/br.fps, sm[p]), textcoords="offset points", xytext=(5,-15), fontsize=8, color="red")
    if contact_result is not None and len(contact_result.contact_frames) > 0:
        cf = contact_result.contact_frames
        ax.plot(cf/br.fps, sm[cf], "g^", markersize=10, label="Contact")
        for c in cf:
            ax.axvline(c/br.fps, color="lime", alpha=0.2, linewidth=0.8)
            ax.annotate(str(c), (c/br.fps, sm[c]), textcoords="offset points", xytext=(5,10), fontsize=8, color="lime")
        bs = contact_result.backswing_result.peak_frames
        for i in range(min(len(bs), len(cf))):
            ax.annotate("", xy=(cf[i]/br.fps, sm[cf[i]]), xytext=(bs[i]/br.fps, sm[bs[i]]),
                        arrowprops=dict(arrowstyle="->", color="yellow", alpha=0.4, lw=1.5))
    ax.set_xlabel("Time (s)"); ax.set_ylabel("Arc position x+y (inverted)")
    ax.set_title(f"{br.name} – Backswing" + (" & Contact" if contact_result else ""))
    ax.legend(loc="lower right"); fig.tight_layout()
    suffix = "_contact_signal.png" if contact_result else "_signal.png"
    out_path = os.path.join(out_dir, br.name + suffix)
    fig.savefig(out_path, dpi=120); plt.close(fig)
    return out_path


def extract_clips(frames, mov_path, fps, out_dir, prefix):
    """Extract short MP4 clips centred on each detected frame.

    Each clip spans ±0.5 s around the target frame and is written with the
    ``mp4v`` codec at the original frame rate.

    Args:
        frames: 1-D array of centre-frame indices.
        mov_path: Path to the source video file.
        fps: Video frame rate.
        out_dir: Directory to write clips into.
        prefix: Filename prefix — clips are named
            ``{prefix}_01.mp4``, ``{prefix}_02.mp4``, etc.

    Returns:
        List of paths to the written MP4 files, or an empty list if
        *frames* is empty.
    """
    if len(frames) == 0:
        return []
    cap = cv2.VideoCapture(mov_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    half_sec = int(round(fps * 0.5))
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    paths = []
    for i, pf in enumerate(frames):
        clamped = min(pf, total-1)
        start, end = max(0, clamped-half_sec), min(total, clamped+half_sec+1)
        out_path = os.path.join(out_dir, f"{prefix}_{i+1:02d}.mp4")
        writer = cv2.VideoWriter(out_path, fourcc, fps, (w, h))
        cap.set(cv2.CAP_PROP_POS_FRAMES, start)
        for _ in range(end - start):
            ret, frame = cap.read()
            if not ret:
                break
            writer.write(frame)
        writer.release()
        paths.append(out_path)
    cap.release()
    return paths
