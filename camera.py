"""Run TFLite inference from a USB/Pi camera and publish results to the dashboard."""
from __future__ import annotations

import argparse
import time
from collections import deque
from pathlib import Path

import cv2
import numpy as np
import requests
from ai_edge_litert.interpreter import Interpreter

DEFAULT_LABELS = ["Bad Mushroom Detected", "Bud Mushroom Detected", "Good Mushroom Detected",
                  "Intermediate Mushroom Detected", "Mature Mushroom Detected", "Medium Mushroom Detected",
                  "No Mushroom Detected"]


def as_model_input(rgb: np.ndarray, detail: dict) -> np.ndarray:
    if detail["dtype"] == np.float32:
        return (rgb.astype(np.float32) / 255.0)[None, ...]
    scale, zero = detail["quantization"]
    values = np.rint(rgb.astype(np.float32) / scale + zero)
    limits = np.iinfo(detail["dtype"])
    return np.clip(values, limits.min, limits.max).astype(detail["dtype"])[None, ...]


def as_probabilities(values: np.ndarray, detail: dict) -> np.ndarray:
    scale, zero = detail["quantization"]
    return (values.astype(np.float32) - zero) * scale if scale else values.astype(np.float32)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--server", default="http://127.0.0.1:5000")
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--interval", type=float, default=0.15)
    parser.add_argument("--threshold", type=float, default=0.60)
    args = parser.parse_args()
    interpreter = Interpreter(model_path=str(args.model), num_threads=4)
    interpreter.allocate_tensors()
    input_detail, output_detail = interpreter.get_input_details()[0], interpreter.get_output_details()[0]
    _, height, width, _ = input_detail["shape"]
    cap = cv2.VideoCapture(args.camera)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    history: deque[np.ndarray] = deque(maxlen=5)
    label, confidence, last_inference, start, frames = "Waiting for detection", 0.0, 0.0, time.monotonic(), 0
    try:
        while cap.isOpened():
            ok, frame = cap.read()
            if not ok:
                break
            now = time.monotonic()
            if now - last_inference >= args.interval:
                rgb = cv2.cvtColor(cv2.resize(frame, (width, height)), cv2.COLOR_BGR2RGB)
                interpreter.set_tensor(input_detail["index"], as_model_input(rgb, input_detail))
                interpreter.invoke()
                history.append(as_probabilities(interpreter.get_tensor(output_detail["index"])[0], output_detail))
                averaged = np.mean(history, axis=0)
                index, confidence = int(np.argmax(averaged)), float(averaged[index])
                label = DEFAULT_LABELS[index] if confidence >= args.threshold else "Uncertain Detection"
                last_inference = now
            frames += 1
            fps = frames / max(now - start, 0.001)
            cv2.putText(frame, label, (15, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 150, 0), 2)
            cv2.putText(frame, f"Confidence: {confidence * 100:.1f}% | {fps:.1f} FPS", (15, 68),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50, 50, 50), 2)
            ok, encoded = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if ok:
                requests.post(f"{args.server}/api/live", data={"label": label, "confidence": confidence * 100, "fps": fps},
                              files={"frame": ("live.jpg", encoded.tobytes(), "image/jpeg")}, timeout=1)
    finally:
        cap.release()


if __name__ == "__main__":
    main()
