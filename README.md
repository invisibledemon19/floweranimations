# Marvalanimations - Interactive Hand-Gesture Flower Animator

An interactive, real-time computer vision application that generates and grows beautiful, procedural flowers directly from your hands using your webcam!

This project tracks your hand landmarks to grow twin-stemmed flowers (an Orange/Yellow flower on the thumb tip and a Pink/Purple flower on the pinky tip) from the bottom of the screen. The flowers dynamically bloom from closed buds into fully opened blossoms as you spread your fingers wide.

---

## 🌸 Key Features

1. **Twin-Flower Control from One Hand**:
   - **Flower 1 (Thumb Tip)**: Blooms with a warm Orange & Yellow gradient.
   - **Flower 2 (Pinky Tip)**: Blooms with a cool Pink & Purple gradient.
2. **Bezier-Curved Stem Growth**:
   - Two forest-green stems grow dynamically from the bottom of the screen (anchored to your palm center) to your fingertips.
   - Includes organic leaves that angle outwards dynamically.
3. **Dynamic Blooming Physics**:
   - Hand openness is calculated in real-time by analyzing the distance of all 5 fingertips relative to your wrist (making it invariant to hand rotation and distance from the camera).
   - A closed fist shows a **closed bud** with green sepals.
   - Spreading your hand open triggers a smooth, procedural blooming animation.
4. **Resilient Hardware Setup**:
   - Automatically probes webcam indexes (`0`, `1`, `2`) to find an available camera feed.
5. **Modern API Stack**:
   - Fully migrated to the modern **MediaPipe Tasks API** for high-performance CPU tracking, compatible with Python 3.14+ on Windows.

---

## 🛠️ Prerequisites & Installation

### 1. Clone the repository
Make sure you are in the project folder:
```bash
cd Marvalanimations
```

### 2. Set up a Virtual Environment
Create and activate a virtual environment to manage dependencies:
```powershell
# Create environment
python -m venv .venv

# Activate environment (Windows PowerShell)
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
Install the required dependencies:
```bash
pip install opencv-python mediapipe numpy
```

---

## 🚀 Running the App

Run the main Python script in your active terminal session:
```powershell
python flower.py
```

### How to Interact:
1. Put your hand in front of the camera.
2. **Make a closed fist** ✊: The stems grow from the bottom, ending in two closed buds on your thumb and pinky tips.
3. **Slowly open your hand** 🖐️: Watch the buds dynamically grow, split, and bloom into gorgeous multi-layered flowers.
4. **Move your hand** left, right, up, or down: The stems will bend and curve organically as they follow your hand.
5. **Quit**: Press **'q'** on your keyboard while focusing on the video window to safely exit and release the webcam.