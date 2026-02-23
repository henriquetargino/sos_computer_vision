# ✋🚨 Signal for Help Detector (Computer Vision)

> A Computer Vision-based security system capable of identifying the universal "Signal for Help" in real-time and triggering API alerts.

## 🎯 About the Project

This project applies **Data Science** concepts to a real-world problem: personal safety.

Unlike traditional approaches that rely on computationally heavy Deep Learning models, this system uses **Euclidean Geometry** and **Linear Algebra** to analyze hand biomechanics in real-time using only a CPU. It successfully differentiates random movements from intentional distress signals through a **Finite State Machine (FSM)**.

---

## 🛠️ Technical Features

* **Hand Tracking:** Uses MediaPipe to extract 21 hand landmarks in real-time.
* **Geometric Logic:** Calculates vector distances between the thumb and the base of the pinky to validate hand positioning independently of depth or fixed pixels.
* **Temporal State Machine:** Alerts are not triggered by a static frame. The system validates the movement **sequence** (Armed -> 2s Window -> Closed Fist).
* **Asynchronous Processing (Threading):** HTTP requests (Webhooks) run on a separate thread to prevent *Blocking I/O*, ensuring the video feed remains smooth at 30 FPS.
* **Visual Feedback (UI):** Reactive interface with dynamic bounding boxes, state feedback (Green/Orange/Red), and screen flashes for visual confirmation.

---

## 🧠 How it Works (The Logic)

The algorithm follows a strict decision pipeline to avoid false positives:

1. **Input:** Video capture via OpenCV (BGR -> RGB conversion).
2. **Vectorization:** Extraction of joint `(x, y)` coordinates.
3. **Stage 1 (Arming):**
* Verifies if 4 fingers are raised.
* Calculates the **Euclidean Distance** (`math.hypot`) between the thumb tip and pinky base. If the distance is short (thumb tucked in), the system enters the **ALERT** state (Orange).


4. **Stage 2 (Triggering):**
* A 2-second temporal window opens.
* If the user closes their fist (all fingers down) within this timeframe, the intent is confirmed.


5. **Output:**
* The system fires a POST Request to a Webhook (e.g., n8n).
* The UI flashes red to confirm a successful distress signal.



---

## 💻 Tech Stack

* **Python 3.10** (Conda Virtual Environment for MediaPipe compatibility)
* **OpenCV (`cv2`)**: Image manipulation and UI rendering.
* **MediaPipe**: Landmark extraction.
* **NumPy & Math**: Vector calculations and geometry.
* **Requests**: API integration.
* **Threading**: Concurrency management.

---

## 🚀 How to Run

### Prerequisites

Ensure you have Python installed (Python 3.10 recommended).

1. **Clone the repository:**

```bash
git clone https://github.com/henriquetargino/sos_computer_vision.git
cd sos_computer_vision

```

2. **Install dependencies:**

```bash
pip install opencv-python mediapipe numpy requests

```

3. **Configure the Webhook (Optional):**
In the `main.py` file, edit the `webhook_socorro` function and add your URL:

```python
url = "your_webhook_link_here"

```

4. **Execute:**

```bash
python main.py

```

---

## 📈 Learnings & Challenges

Several engineering challenges were overcome during development:

* **Color Channels:** Handling OpenCV's BGR matrices vs. AI models' RGB requirements.
* **Concurrency:** Implementing Threading was crucial. Without it, the video feed would freeze while Python waited for the HTTP server's response.
* **Safety UX:** Designing visual feedback (Focus Boxes and Flashes) to assure the user that the system understood the command.

---

## 📞 Contact

**Henrique Targino** - Data Scientist
[LinkedIn](https://www.linkedin.com/in/henriquetargino) | [Portfolio](https://henriquetargino.github.io/Portfolio)

---
