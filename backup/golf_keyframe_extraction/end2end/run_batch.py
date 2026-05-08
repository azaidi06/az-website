"""Batch backswing + contact detection CLI.

Discovers videos in a dataset directory, runs the full detection pipeline on
each, generates visualizations (grids, signal plots, optional clips), flags
potential problems, and optionally exports CSV summaries.

Usage::

    python -m end2end.run_batch <dataset_dir> [options]
    python -m end2end.run_batch ../saugusta --no-clips --no-pushover
    python -m end2end.run_batch ../oct25 --contact --csv --no-clips --no-pushover --skip IMG_1189
"""
import argparse, csv, os, shutil, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from end2end.config import Config
from end2end.pipeline import detect_backswings, detect_contacts
from end2end import visualize


def discover_videos(dataset_dir, skip=None):
    """Scan a dataset directory for video/keypoint pairs.

    Expects the layout::

        dataset_dir/
            VIDEO_NAME.MOV  (or .mp4)
            VIDEO_NAME/
                keypoints/
                    VIDEO_NAME.pkl

    Args:
        dataset_dir: Root directory of the dataset.
        skip: Optional list of video names to exclude.

    Returns:
        Dict mapping video name to ``{"mov": path, "pkl": path}``, sorted
        alphabetically.
    """
    skip = set(skip or [])
    videos = {}
    for entry in sorted(os.listdir(dataset_dir)):
        if entry in skip:
            continue
        pkl = os.path.join(dataset_dir, entry, "keypoints", entry + ".pkl")
        # accept .MOV or .mp4
        mov = os.path.join(dataset_dir, entry + ".MOV")
        if not os.path.isfile(mov):
            mov = os.path.join(dataset_dir, entry + ".mp4")
        if os.path.isfile(pkl) and os.path.isfile(mov):
            videos[entry] = {"mov": mov, "pkl": pkl}
    return videos


def flag_problems(result, cfg):
    """Check a detection result for potential issues.

    Runs heuristic checks on the detected peaks and flags anything
    suspicious:

    - Too few or too many swings.
    - Individual peaks whose x+y value is an outlier (MAD z-score).
    - Low wrist confidence in the neighbourhood of a peak.
    - Two successive swings closer than ``close_gap_seconds``.

    Args:
        result: ``DetectionResult`` to check.
        cfg: ``Config`` instance (threshold parameters).

    Returns:
        List of ``(swing_index_or_None, reason_string)`` tuples.  An empty
        list means no problems were found.
    """
    issues = []
    pf, smoothed, pkl_data, fps = result.peak_frames, result.smoothed, result.pkl_data, result.fps
    n = len(pf)
    if n < cfg.min_expected_swings:
        issues.append((None, f"Only {n} swing(s) (expected >= {cfg.min_expected_swings})"))
    if n > cfg.max_expected_swings:
        issues.append((None, f"{n} swings (expected <= {cfg.max_expected_swings})"))
    if n == 0:
        return issues
    vals = smoothed[pf]
    med = np.median(vals)
    mad = np.median(np.abs(vals - med)) if len(vals) > 1 else 0.0
    for i, p in enumerate(pf):
        if mad > 0 and len(vals) >= 3:
            z = abs(vals[i] - med) / mad
            if z > cfg.flag_mad_threshold:
                issues.append((i, f"x+y={vals[i]:.0f} is {z:.1f} MADs from median"))
        s, e = max(0, p - cfg.low_conf_window), min(len(pkl_data), p + cfg.low_conf_window + 1)
        confs = [(pkl_data[f"frame_{f}"]["keypoint_scores"][cfg.left_wrist] +
                  pkl_data[f"frame_{f}"]["keypoint_scores"][cfg.right_wrist]) / 2.0
                 for f in range(s, e) if f"frame_{f}" in pkl_data]
        if confs and np.mean(confs) < cfg.low_conf_threshold:
            issues.append((i, f"Low wrist conf: {np.mean(confs):.2f}"))
        if i > 0:
            gap_s = (p - pf[i-1]) / fps
            if gap_s < cfg.close_gap_seconds:
                issues.append((i, f"Only {gap_s:.1f}s since previous swing"))
    return issues


def _write_csv(path, rows, fields):
    """Write a list of row dicts to a CSV file with the given field order.

    Args:
        path: Output CSV path.
        rows: List of dicts, each representing one row.
        fields: Column names in the desired output order.
    """
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)
    print(f"  CSV: {path} ({len(rows)} rows)")


def export_csvs(all_bs, all_ct, out_dir):
    """Export detection results to three CSV files.

    Produces:

    - ``backswing_detections.csv`` — one row per detected backswing.
    - ``contact_detections.csv`` — one row per detected contact (if any).
    - ``downswing_durations.csv`` — paired backswing→contact with frame gap
      and duration in seconds.

    Args:
        all_bs: List of ``DetectionResult`` objects.
        all_ct: List of ``ContactResult`` objects (may be empty).
        out_dir: Directory to write the CSV files into.
    """
    bs_rows, ct_rows, ds_rows = [], [], []
    for br in all_bs:
        for i, bf in enumerate(br.peak_frames):
            bs_rows.append(dict(video=br.name, swing_num=i+1, backswing_frame=int(bf),
                                backswing_time_s=round(bf/br.fps,2), xy_signal=round(float(br.smoothed[bf]),1), fps=round(br.fps,2)))
    for cr in all_ct:
        br = cr.backswing_result
        for i, cf in enumerate(cr.contact_frames):
            ct_rows.append(dict(video=cr.name, swing_num=i+1, contact_frame=int(cf),
                                contact_time_s=round(cf/br.fps,2), xy_signal=round(float(cr.smoothed[cf]),1), fps=round(br.fps,2)))
        for i in range(min(len(br.peak_frames), len(cr.contact_frames))):
            bf, cf = br.peak_frames[i], cr.contact_frames[i]
            gap = int(cf - bf)
            ds_rows.append(dict(video=cr.name, swing_num=i+1, backswing_frame=int(bf), contact_frame=int(cf),
                                downswing_frames=gap, downswing_time_s=round(gap/br.fps,3), fps=round(br.fps,2)))
    _write_csv(os.path.join(out_dir, "backswing_detections.csv"), bs_rows,
               ["video","swing_num","backswing_frame","backswing_time_s","xy_signal","fps"])
    if ct_rows:
        _write_csv(os.path.join(out_dir, "contact_detections.csv"), ct_rows,
                   ["video","swing_num","contact_frame","contact_time_s","xy_signal","fps"])
    if ds_rows:
        _write_csv(os.path.join(out_dir, "downswing_durations.csv"), ds_rows,
                   ["video","swing_num","backswing_frame","contact_frame","downswing_frames","downswing_time_s","fps"])


def main():
    """Run batch detection from the command line.

    Discovers all video/keypoint pairs in the dataset directory, runs
    backswing (and optionally contact) detection on each, generates grids
    and signal plots, flags problems, and optionally exports CSVs.

    Example::

        # Backswing only, no clips or notifications
        python -m end2end.run_batch ../saugusta --no-clips --no-pushover

        # Full pipeline with contact detection and CSV export
        python -m end2end.run_batch ../oct25 --contact --csv --no-clips --no-pushover

        # Skip a problematic video
        python -m end2end.run_batch ../oct25 --skip IMG_1189 --no-pushover
    """
    ap = argparse.ArgumentParser(description="Batch backswing + contact detection")
    ap.add_argument("dataset_dir"); ap.add_argument("--out", default=None)
    ap.add_argument("--contact", action="store_true"); ap.add_argument("--csv", action="store_true")
    ap.add_argument("--no-clips", action="store_true"); ap.add_argument("--no-pushover", action="store_true")
    ap.add_argument("--skip", action="append", default=[])
    args = ap.parse_args()

    dataset_dir = os.path.abspath(args.dataset_dir)
    dataset_name = os.path.basename(dataset_dir)
    out_root = os.path.abspath(args.out or (dataset_name + "_testing"))
    os.makedirs(out_root, exist_ok=True)
    cfg = Config()

    videos = discover_videos(dataset_dir, skip=args.skip)
    print(f"Found {len(videos)} videos: {', '.join(videos.keys())}")

    if not args.no_pushover:
        try:
            from pushover import notify
        except ImportError:
            print("Warning: pushover not found, disabling notifications"); args.no_pushover = True

    all_bs, all_ct, all_problems = [], [], {}
    for name, paths in videos.items():
        vid_out = os.path.join(out_root, name)
        os.makedirs(vid_out, exist_ok=True)
        result = detect_backswings(paths["pkl"], paths["mov"], config=cfg)
        all_bs.append(result)
        filters = [m.split(":")[0] for m in result.filter_log]
        line = f"{name}: {result.n_swings} swings"

        ct = None
        if args.contact:
            ct = detect_contacts(result, config=cfg)
            all_ct.append(ct)
            line += f", {ct.n_contacts} contacts"
        if filters:
            line += f"  [filters: {', '.join(filters)}]"

        # Visualizations
        visualize.make_grid(result.peak_frames, result.pkl_data, result.mov_path, result.fps,
                            f"{name} – Top of Backswing", os.path.join(vid_out, f"{name}_backswing_grid.png"))
        visualize.make_signal_plot(result, vid_out)
        if ct:
            visualize.make_grid(ct.contact_frames, result.pkl_data, result.mov_path, result.fps,
                                f"{name} – Contact Points", os.path.join(vid_out, f"{name}_contact_grid.png"))
            visualize.make_signal_plot(result, vid_out, contact_result=ct)
        if not args.no_clips:
            visualize.extract_clips(result.peak_frames, result.mov_path, result.fps, vid_out, f"{name}_swing")
            if ct:
                visualize.extract_clips(ct.contact_frames, result.mov_path, result.fps, vid_out, f"{name}_contact")

        issues = flag_problems(result, cfg)
        if issues:
            all_problems[name] = issues
            line += " *** PROBLEMS ***"
            pdir = os.path.join(out_root, "problems")
            os.makedirs(pdir, exist_ok=True)
            for suffix in ["_backswing_grid.png", "_signal.png"]:
                src = os.path.join(vid_out, name + suffix)
                if os.path.isfile(src):
                    shutil.copy2(src, os.path.join(pdir, name + suffix))
        print(line)

    # Summary
    txt = f"\n{dataset_name}: {sum(r.n_swings for r in all_bs)} total swings across {len(all_bs)} videos"
    if all_ct:
        txt += f", {sum(c.n_contacts for c in all_ct)} contacts"
    if all_problems:
        txt += f"\nProblematic: {', '.join(all_problems.keys())}"
        pdir = os.path.join(out_root, "problems")
        os.makedirs(pdir, exist_ok=True)
        with open(os.path.join(pdir, "summary.txt"), "w") as f:
            for vname, issues in all_problems.items():
                f.write(f"{vname}:\n")
                for si, reason in issues:
                    f.write(f"  {'Swing '+str(si+1) if si is not None else 'VIDEO'}: {reason}\n")
                f.write("\n")
    print(txt)
    if not args.no_pushover:
        try:
            notify(txt, title=f"{dataset_name} detection")
        except Exception as e:
            print(f"Pushover failed: {e}")
    if args.csv:
        export_csvs(all_bs, all_ct, out_root)
    print(f"All outputs in: {out_root}")


if __name__ == "__main__":
    main()
