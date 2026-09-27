#!/usr/bin/env python3
"""Live HSV calibration for the OpenCV ball detector.

Shows the in-range mask + detected blobs for one color at a time with drag
trackbars. Use a saved frame (or webcam) from your actual field camera and
tune H/S/V until only the ball lights up.

Usage:
    python hsv_tuner.py path/to/frame.jpg    # single saved frame
    python hsv_tuner.py --camera 0            # live webcam

Keys:
    1/2/3   pick color yellow/red/blue
    r       print current ranges (copy into BallDetectorPipeline.java)
    s       save current frame + mask preview to tune-<color>.jpg
    q       quit
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

NAMES = {1: "yellow", 2: "red", 3: "blue"}
# Start from the learned values (matches hsv_tuned.json / fit_hsv_from_yolo.py);
# red has two segments (its hue wraps through 0) -- the trackbars edit the
# primary segment (seg 0) live, seg 1 keeps its INIT values, and the mask
# shows BOTH segments so you can confirm the wrap is covered.
INIT = {
    "yellow": ([9, 90, 45], [33, 255, 238]),
    "red":    ([[0, 81, 45], [170, 81, 45]], [[15, 255, 232], [180, 255, 232]]),
    "blue":   ([102, 80, 45], [128, 255, 247]),
}
WIN = "hsv_tuner"


def nothing(_):
    pass


def segments(color_name):
    """[(lo, hi), ...] for each HSV segment of a color (red wraps -> two)."""
    lo, hi = INIT[color_name]
    if isinstance(lo[0], (list, tuple)):
        return list(zip(lo, hi))
    return [(lo, hi)]


def windows(color_name):
    cv2.destroyWindow(WIN)
    cv2.namedWindow(WIN)
    lo, hi = segments(color_name)[0]     # trackbars edit the primary segment
    for name, pos, mx in (("H lo", lo[0], 180), ("S lo", lo[1], 255),
                          ("V lo", lo[2], 255), ("H hi", hi[0], 180),
                          ("S hi", hi[1], 255), ("V hi", hi[2], 255)):
        cv2.createTrackbar(name, WIN, int(pos), mx, nothing)


def track():
    return [cv2.getTrackbarPos(f"{ch} {'lo' if i < 3 else 'hi'}", WIN)
            for i, ch in enumerate("HHHSSS")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", nargs="?", help="image file path (or use --camera)")
    ap.add_argument("--camera", type=int, help="webcam index")
    a = ap.parse_args()
    if a.source and a.camera is None:
        cap = None
        frame = cv2.imread(a.source)
    elif a.camera is not None:
        cap = cv2.VideoCapture(a.camera)
        ok, frame = cap.read()
    else:
        print("give an image path or --camera")
        sys.exit(1)

    color = 1
    windows(NAMES[color])
    segs = segments(NAMES[color])          # primary segment first; rest fixed
    while True:
        if cap is not None:
            ok, frame = cap.read()
            if not ok:
                break
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        vals = track()
        primary_lo = np.array(vals[:3])
        primary_hi = np.array(vals[3:])
        mask = np.zeros(hsv.shape[:2], np.uint8)
        for i, (slo, shi) in enumerate(segs):
            lo = primary_lo if i == 0 else np.array(slo)
            hi = primary_hi if i == 0 else np.array(shi)
            mask |= cv2.inRange(hsv, lo, hi)
        nm = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        cnts, _ = cv2.findContours(nm, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        vis = frame.copy()
        for ct in cnts:
            x, y, w, h = cv2.boundingRect(ct)
            area = cv2.contourArea(ct)
            if area < 50 or w <= 0 or h <= 0:
                continue
            if not (0.4 < area / (w * h) < 1.6):
                continue
            cv2.rectangle(vis, (x, y), (x + w, y + h), (0, 255, 255) if color == 1
                          else (0, 0, 255) if color == 2 else (255, 0, 0), 2)
        cv2.imshow("mask", nm)
        cv2.imshow(WIN, vis)
        k = cv2.waitKey(20) & 0xFF
        if k == ord('1'):
            color = 1
        elif k == ord('2'):
            color = 2
        elif k == ord('3'):
            color = 3
        if k in (ord('1'), ord('2'), ord('3')):
            windows(NAMES[color])
            segs = segments(NAMES[color])
        if k == ord('r'):
            vals = track()
            for i, (slo, shi) in enumerate(segs):
                lo = vals[:3] if i == 0 else slo
                hi = vals[3:] if i == 0 else shi
                tag = " (live)" if i == 0 else " (fixed)"
                print(f"{NAMES[color]:7s} seg{i}{tag} Lower {list(map(int, lo))}  "
                      f"Upper {list(map(int, hi))}")
        if k == ord('s'):
            cv2.imwrite(f"tune_{NAMES[color]}.jpg", np.hstack([frame, cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)]))
            print("saved tune_{}.jpg".format(NAMES[color]))
        if k in (ord('q'), 27):
            break
    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()