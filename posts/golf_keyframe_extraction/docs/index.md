# end2end — Golf Swing Detection

Automatically find the **top-of-backswing** and **ball-contact** frames in golf
videos using wrist keypoints from mmpose and Savitzky-Golay signal processing.

No ML model, no GPU, no training data — just wrist positions and a pair of
smoothing filters.

## Pipeline

```
Raw wrist keypoints (x, y per frame)
  → Interpolate low-confidence frames
  → Combined signal: (x_L + x_R)/2 + (y_L + y_R)/2
  → Fine smooth (9 frames / 150ms) + Coarse smooth (61 frames / 1.0s)
  → find_peaks on inverted signal (anchors)
  → Backward search on coarse signal (candidate regions)
  → Backswing scoring (smooth approach + sharp departure)
  → Apex refinement (+15 frames on fine signal)
  → Five-stage filtering (dedup, end-trim, merge, MAD, follow-through)
  → Contact search (forward 10-90 frames for max)
```

## Quick Start

```python
from end2end import detect_backswings, detect_contacts

# Detect backswing tops
result = detect_backswings("keypoints/IMG_1171.pkl", "IMG_1171.mp4")
print(f"{result.n_swings} swings at frames {result.peak_frames}")

# Find contact points
contacts = detect_contacts(result)
print(f"{contacts.n_contacts} contacts at frames {contacts.contact_frames}")
```

## CLI

```bash
# Backswing only
python -m end2end.run_batch ../saugusta --no-clips --no-pushover

# Backswing + contact + CSV export
python -m end2end.run_batch ../oct25 --contact --csv --no-clips --no-pushover
```

## API Reference

- [Configuration](reference/config.md) — `Config`, `DetectionResult`, `ContactResult`
- [I/O](reference/io.md) — loading keypoint pickles and video metadata
- [Signal Processing](reference/signal.md) — interpolation and combined arc signal
- [Peak Detection](reference/peaks.md) — anchor detection, scoring, refinement
- [Filters](reference/filters.md) — five-stage post-processing pipeline
- [Contact Detection](reference/contact.md) — forward search for ball impact
- [Pipeline](reference/pipeline.md) — thin orchestrators (`detect_backswings`, `detect_contacts`)
- [Visualization](reference/visualize.md) — skeleton grids, signal plots, clips
- [Batch Processing](reference/run_batch.md) — CLI runner and CSV export
