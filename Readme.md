# Agrowtein AI Vision

Live mushroom-quality monitoring with a webcam, a TensorFlow Lite model, and a browser dashboard.

The system reads frames from a webcam, classifies each frame, and sends the latest frame, label, confidence, and FPS to the local dashboard.

## What it detects

The included model returns one of these classes:

- Bad Mushroom Detected
- Bud Mushroom Detected
- Good Mushroom Detected
- Intermediate Mushroom Detected
- Mature Mushroom Detected
- Medium Mushroom Detected
- No Mushroom Detected

Predictions below the configured confidence threshold are shown as `Uncertain Detection`.

## Main files

| File | Purpose |
| --- | --- |
| `server.py` | Starts the dashboard and receives live results from the camera process. |
| `camera.py` | Reads a webcam, runs the `.tflite` model, and publishes the live frame/result. |
| `index.html` | Live Agrowtein dashboard. |
| `style.css` / `script.js` | Dashboard design and real-time UI logic. |
| `mushroom_classifier.tflite` | Model used by the live camera application. |
| `classify.py` | Legacy single-image upload API; not needed for live dashboard use. |

## Windows setup

### 1. Requirements

- Windows 10 or 11
- Python 3.11, 64-bit
- A built-in or USB webcam

Check Python:

```powershell
python --version
```

### 2. Create a virtual environment

Open PowerShell in the project folder:

```powershell
cd C:\Users\ASUS\Documents\Agrowtein\mashroom_cnn
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this once in that window, then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### 3. Install packages

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements-windows.txt
```

## Run the live dashboard

Use **two PowerShell windows**. Keep both windows open while the system runs.

### Terminal 1 — dashboard server

```powershell
cd C:\Users\ASUS\Documents\Agrowtein\mashroom_cnn
.\.venv\Scripts\Activate.ps1
python server.py
```

Open the dashboard in a browser:

```text
http://127.0.0.1:5000
```

### Terminal 2 — webcam and AI model

```powershell
cd C:\Users\ASUS\Documents\Agrowtein\mashroom_cnn
.\.venv\Scripts\Activate.ps1
python camera.py --camera 0 --model mushroom_classifier.tflite --server http://127.0.0.1:5000
```

The dashboard updates automatically. Click **Start Analysis** to show the live feed in the UI.

## Select a different webcam

Camera `0` is usually the built-in laptop webcam. For an external USB webcam, stop `camera.py` with `Ctrl+C`, then try:

```powershell
python camera.py --camera 1 --model mushroom_classifier.tflite --server http://127.0.0.1:5000
```

If needed, try `--camera 2`. Close Chrome tabs, Teams, Zoom, or the Windows Camera app if they are using the webcam.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `No module named ai_edge_litert` | Activate `.venv`, then run `python -m pip install -r requirements-windows.txt`. |
| `--model MODEL` required | Include `--model mushroom_classifier.tflite` in the `camera.py` command. |
| Dashboard shows no frame | Confirm `server.py` is running first, then start `camera.py` in the second terminal. |
| Dashboard is unstyled | Restart `server.py`, then press `Ctrl+F5` in the browser. |
| Camera cannot open | Close other apps using it and change `--camera 0` to `--camera 1` or `--camera 2`. |
| Camera text looks reversed | Refresh after updating to the latest `style.css`; the dashboard does not mirror Pi/USB frames. |

## Raspberry Pi note

The same `server.py` and `camera.py` workflow works on a 64-bit Raspberry Pi OS installation. Install system packages first:

```bash
sudo apt update
sudo apt install -y python3-venv python3-opencv python3-flask python3-requests
```

Then create a virtual environment with `python3 -m venv --system-site-packages .venv`, activate it, and install `ai-edge-litert` with pip. For an official CSI Pi Camera Module, `camera.py` may need a Picamera2 input instead of the OpenCV webcam input.

## Important limitation

This is an image **classifier**. It labels the whole camera frame; it does not draw boxes around or count individual mushrooms. Individual-object counting requires a separately trained object-detection model.
