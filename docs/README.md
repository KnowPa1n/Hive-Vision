# Overview

Hive Vision is a real-time FTC ball-detection suite (`yellow_pollen`, `red_nectar`, `blue_nectar`). The repo README is the source of truth for everything technical; this book exists to (a) help a new team pick a track and (b) give step-by-step setup instructions you can follow with the camera on the bench.

## 5-minute quick starts

Pick the track you have hardware for and be up in ~5 minutes:

* **[Limelight 3A (SSD)](quick_start.md)** — the neural track. Most capable: shape + shadow aware, runs on the Limelight's own CPU. Start here.
* **[Control Hub CV (HSV)](quick_start_cv.md)** — model-free color thresholding on any Control Hub + webcam. Cheapest, worst in shadows.
* **[Control Hub Lab](quick_start_lab.md)** — model-free chromaticity on the same webcam. The shadow-robust middle track.

## The rest of this book

* [Which detector track?](detector_tracks/) — the decision guide, with full per-track setup walkthroughs:
  * [Limelight 3A (SSD) — set it up](detector_tracks/limelight_3a_ssd/limelight_3a_setup.md)
  * [PC / ONNX Runtime (YOLO) — run it on a PC](detector_tracks/onnx_pc/onnx_run_pc.md)
  * [Control Hub (OpenCV + Lab)](detector_tracks/control_hub/) — [HSV setup](detector_tracks/control_hub/hub_hsv_setup.md) · [Lab setup](detector_tracks/control_hub/hub_lab_setup.md)
* [Calibration & coordinates](calibration.md) — how to measure `CAM_*`, and the sign conventions
* [Known limitations](known_limitations.md) — what the detectors can't do, and the fixes
* [Collecting training data](training_data.md)
* API — the `ftc_ball_chase_lib` classes (the API tab of this book)
* [Deployment checklist](deployment_checklist.md) — what ships where

Classes are always `yellow_pollen`=0, `red_nectar`=1, `blue_nectar`=2.

## In action

Same kickoff footage through each detector:

![Limelight 3A (SSD)](.gitbook/assets/ssd_mobilenetv2.gif)

![Control Hub (CV)](.gitbook/assets/control_hub_cv_example_1.gif)

![Control Hub (Lab)](.gitbook/assets/cielab_demo.gif)

The Limelight 3A model in the real world:

![Limelight 3A in action](.gitbook/assets/ssd_in_action.gif)