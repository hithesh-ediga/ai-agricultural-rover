"""
AI Agricultural Rover - Crop Disease Detection Node
Uses OpenCV colour masking to estimate leaf discoloration (brown/yellow lesions)
from a webcam, an ESP32-CAM stream, or a single image.

Examples:
    python detect_disease.py                                   # default webcam
    python detect_disease.py --source http://192.168.1.50:81/stream   # ESP32-CAM
    python detect_disease.py --source leaf.jpg                 # single image
"""

import argparse
import sys

import cv2
import numpy as np

# HSV ranges (OpenCV hue is 0-179)
HEALTHY_GREEN = (np.array([35, 50, 50]), np.array([85, 255, 255]))
DISEASE_BROWN_YELLOW = (np.array([10, 100, 20]), np.array([30, 255, 200]))

DEFAULT_ALERT_THRESHOLD = 15.0  # % of leaf pixels


def analyze_leaf_health(image_frame):
    """
    Return the percentage of leaf pixels that look diseased (brown/yellow)
    relative to all leaf pixels (healthy green + diseased).
    """
    hsv = cv2.cvtColor(image_frame, cv2.COLOR_BGR2HSV)

    healthy_mask = cv2.inRange(hsv, *HEALTHY_GREEN)
    disease_mask = cv2.inRange(hsv, *DISEASE_BROWN_YELLOW)

    healthy_pixels = cv2.countNonZero(healthy_mask)
    disease_pixels = cv2.countNonZero(disease_mask)
    total_pixels = healthy_pixels + disease_pixels

    if total_pixels == 0:
        return 0.0
    return disease_pixels / total_pixels * 100


def annotate(frame, infection_rate, threshold):
    if infection_rate > threshold:
        text, color = f"WARNING: Disease Detected! ({infection_rate:.1f}%)", (0, 0, 255)
    else:
        text, color = f"Healthy ({infection_rate:.1f}% affected)", (0, 200, 0)
    cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)


def run_image(path, threshold, show):
    frame = cv2.imread(path)
    if frame is None:
        sys.exit(f"Error: could not read image '{path}'")

    infection_rate = analyze_leaf_health(frame)
    status = "DISEASE DETECTED" if infection_rate > threshold else "healthy"
    print(f"{path}: {infection_rate:.1f}% affected -> {status}")

    if show:
        annotate(frame, infection_rate, threshold)
        cv2.imshow("Crop Monitor", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def run_stream(source, threshold):
    cap = cv2.VideoCapture(int(source) if source.isdigit() else source)
    if not cap.isOpened():
        sys.exit(f"Error: could not open camera/stream '{source}'")

    print("Vision node running. Press 'q' in the video window to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Stream ended or frame could not be read.")
            break

        annotate(frame, analyze_leaf_health(frame), threshold)
        cv2.imshow("Crop Monitor Stream", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description="Crop disease detection (OpenCV colour masking)")
    parser.add_argument("--source", default="0",
                        help="camera index (e.g. 0), stream URL (ESP32-CAM), or image file path")
    parser.add_argument("--threshold", type=float, default=DEFAULT_ALERT_THRESHOLD,
                        help="alert when affected leaf area exceeds this percent (default: 15)")
    parser.add_argument("--no-window", action="store_true",
                        help="image mode only: print the result without opening a window")
    args = parser.parse_args()

    if args.source.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
        run_image(args.source, args.threshold, show=not args.no_window)
    else:
        run_stream(args.source, args.threshold)


if __name__ == "__main__":
    main()
