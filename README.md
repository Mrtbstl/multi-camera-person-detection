> **IMPORTANT NOTE:** Although the initial plan included GStreamer, it was excluded after repeated compatibility issues on macOS. Instead, we implemented a fully working Flask-based MJPEG stream server, which still delivers the required functionality.

# Multi-Camera Real-Time Face Detection Platform
This project implements a real-time video analytics and streaming system that detects faces from two simultaneous camera inputs and displays annotated video feeds along with detection metrics through a web interface and REST API.

---

## 🎯 Features

- 🔴 Real-time face detection with bounding boxes using OpenCV
- 📷 Multi-camera support (e.g., iPhone + MacBook webcam)
- 🌐 Web interface to display both streams side by side
- 📊 REST API endpoint to monitor face detection counts per camera
- ⚡ Flicker-free visualization by analyzing every single frame
- 💻 Clean HTML/CSS layout with automatic face count updates via JavaScript

---

## 🧱 Technologies Used

- Python 3
- Flask (REST API + web server)
- OpenCV (Haar cascades for face detection)
- HTML5 + CSS + JavaScript (front-end)

---

## 🚀 Installation

> Recommended: Use a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## ▶️ Running the App

```bash
python app.py
```

- Visit: `http://localhost:5050`
- Live video feeds will appear for both cameras
- Face counts will update every second under each stream
- REST API available at: `http://localhost:5050/status`

Example JSON response:
```json
{
  "status": "Running",
  "faces_detected_1": 2,
  "faces_detected_2": 1
}
```

---

## 🧠 Notes

- Although GStreamer was initially considered, it was excluded due to multiple compatibility and runtime issues encountered on macOS during testing.
- Video encoding and face annotation are handled directly with OpenCV.
- Face detection is performed using OpenCV’s `haarcascade_frontalface_default.xml`.

---

## 📂 Project Structure

```
.
├── app.py               # Main Flask app and video processing logic
├── requirements.txt     # Dependencies
└── venv/                # (Optional) Virtual environment directory
```
