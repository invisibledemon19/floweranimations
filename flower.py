import cv2
import mediapipe as mp
import math
import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Initialize MediaPipe Hands
base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.7,
    min_tracking_confidence=0.7
)
detector = vision.HandLandmarker.create_from_options(options)
last_timestamp_ms = 0

# Start capturing video from the webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Webcam index 0 not available. Trying index 1...")
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("Webcam index 1 not available. Trying index 2...")
        cap = cv2.VideoCapture(2)
        if not cap.isOpened():
            print("Error: Could not open any webcam (tried indexes 0, 1, 2).")
            print("Make sure your camera is connected and not in use by another app.")

def get_hand_openness(hand_landmarks):
    """Calculates a normalized score [0.0, 1.0] indicating how open the hand is.
    0.0 represents a tight fist, 1.0 represents a fully open hand."""
    wrist = hand_landmarks[0]
    mcp = hand_landmarks[9] # Middle finger MCP
    
    # Scale reference (distance from wrist to middle finger MCP)
    scale = math.hypot(mcp.x - wrist.x, mcp.y - wrist.y)
    if scale < 0.001:
        scale = 0.001
        
    # We calculate distance from wrist to all 5 fingertips
    tips = [4, 8, 12, 16, 20]
    dists = []
    for tip_idx in tips:
        tip = hand_landmarks[tip_idx]
        d = math.hypot(tip.x - wrist.x, tip.y - wrist.y)
        dists.append(d / scale)
        
    avg_dist = sum(dists) / len(dists)
    
    # Closed fist avg_dist is around 1.1-1.3, open hand is 2.0-2.5
    # We map [1.2, 2.2] to [0.0, 1.0]
    openness = (avg_dist - 1.2) / 1.0
    openness = max(0.0, min(1.0, openness))
    return openness

def draw_stem(img, base_x, target_x, target_y, img_height, is_left_curve=True):
    """Draws a green curved stem from a base at the bottom of the screen to a target coordinate,
    along with a leaf."""
    # Control point for curvature (curve left or right)
    mid_y = (target_y + img_height) // 2
    curve_direction = -30 if is_left_curve else 30
    mid_x = (base_x + target_x) // 2 + curve_direction
    
    # Generate points along quadratic Bezier curve
    points = []
    for i in range(21):
        t = i / 20.0
        x = int((1-t)**2 * base_x + 2*(1-t)*t * mid_x + t**2 * target_x)
        y = int((1-t)**2 * img_height + 2*(1-t)*t * mid_y + t**2 * target_y)
        points.append((x, y))
        
    # Draw stem lines
    for i in range(len(points) - 1):
        cv2.line(img, points[i], points[i+1], (34, 139, 34), 4) # Forest Green
        
    # Draw a leaf at t = 0.5
    t_leaf = 0.5
    lx = int((1-t_leaf)**2 * base_x + 2*(1-t_leaf)*t_leaf * mid_x + t_leaf**2 * target_x)
    ly = int((1-t_leaf)**2 * img_height + 2*(1-t_leaf)*t_leaf * mid_y + t_leaf**2 * target_y)
    leaf_angle = -45 if is_left_curve else 45
    cv2.ellipse(img, (lx, ly), (15, 8), leaf_angle, 0, 360, (34, 139, 34), -1)
    cv2.ellipse(img, (lx, ly), (15, 8), leaf_angle, 0, 360, (0, 100, 0), 1)

def draw_flower(img, center_x, center_y, openness, flower_type=0):
    """Draws a procedurally animated flower using OpenCV that blooms as openness increases.
    flower_type=0 draws an orange/yellow flower, flower_type=1 draws a pink/purple flower."""
    if openness < 0.15:
        # Draw a closed flower bud
        bud_color = (147, 20, 255) if flower_type == 0 else (203, 192, 255) # Magenta-pink vs light pink/purple
        border_color = (100, 0, 150) if flower_type == 0 else (150, 50, 100)
        cv2.ellipse(img, (center_x, center_y), (10, 15), 0, 0, 360, bud_color, -1)
        cv2.ellipse(img, (center_x, center_y), (10, 15), 0, 0, 360, border_color, 2)
        # Sepals at base
        cv2.circle(img, (center_x - 5, center_y + 12), 4, (34, 139, 34), -1)
        cv2.circle(img, (center_x + 5, center_y + 12), 4, (34, 139, 34), -1)
        return
        
    # Scale bloom with openness
    bloom = (openness - 0.15) / 0.85
    core_radius = int(8 + (bloom * 12))
    petal_radius = int(10 + (bloom * 25))
    petal_distance = int(12 + (bloom * 38))
    
    # Color scheme selection
    if flower_type == 0:
        # Orange/Yellow
        color1 = (0, 120, 255) # dark orange edge
        color2 = (0, 180, 255) # lighter orange
        color3 = (0, 220, 255) # yellow center
        outline_color = (0, 60, 180)
        core_color = (0, 255, 255)
        core_outline = (0, 180, 180)
    else:
        # Pink/Purple
        color1 = (180, 0, 180) # dark purple edge
        color2 = (220, 50, 220) # magenta middle
        color3 = (255, 120, 255) # light pink center
        outline_color = (120, 0, 120)
        core_color = (255, 255, 150) # light yellow core
        core_outline = (180, 180, 100)

    # Draw 6 petals
    for i in range(6):
        angle = i * (math.pi / 3)
        petal_x = int(center_x + math.cos(angle) * petal_distance)
        petal_y = int(center_y + math.sin(angle) * petal_distance)
        
        # nested circles for gradient effect
        cv2.circle(img, (petal_x, petal_y), petal_radius, color1, -1)
        cv2.circle(img, (petal_x, petal_y), int(petal_radius * 0.8), color2, -1)
        cv2.circle(img, (petal_x, petal_y), int(petal_radius * 0.5), color3, -1)
        cv2.circle(img, (petal_x, petal_y), petal_radius, outline_color, 2)
        
    # Draw Center of the flower
    cv2.circle(img, (center_x, center_y), core_radius, core_color, -1)
    cv2.circle(img, (center_x, center_y), core_radius, core_outline, 2)

while True:
    success, img = cap.read()
    if not success:
        print("Warning: Failed to grab frame from webcam. Exiting...")
        break

    # Flip the image horizontally for a selfie-view display
    img = cv2.flip(img, 1)
    h, w, _ = img.shape

    # Convert the BGR image to RGB for MediaPipe
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Create MediaPipe Image object
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
    
    # Calculate timestamp in ms
    timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))
    if timestamp_ms <= last_timestamp_ms:
        timestamp_ms = last_timestamp_ms + 1
    last_timestamp_ms = timestamp_ms

    results = detector.detect_for_video(mp_image, timestamp_ms)

    if results.hand_landmarks:
        for hand_landmarks in results.hand_landmarks:
            # Get palm center (middle finger MCP) to anchor stem bases
            palm_center = hand_landmarks[9]
            cx = int(palm_center.x * w)

            # Get coordinates for Thumb Tip (Landmark 4) and Pinky Tip (Landmark 20)
            thumb_tip = hand_landmarks[4]
            pinky_tip = hand_landmarks[20]

            t_x, t_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
            p_x, p_y = int(pinky_tip.x * w), int(pinky_tip.y * h)

            # Draw fingertip dots for active tracking feedback
            for tip_idx in [4, 8, 12, 16, 20]:
                tip = hand_landmarks[tip_idx]
                tx, ty = int(tip.x * w), int(tip.y * h)
                cv2.circle(img, (tx, ty), 5, (255, 0, 255), -1)

            # Calculate overall hand openness
            openness = get_hand_openness(hand_landmarks)

            # Draw Stem 1 to Thumb Tip (base shifted left)
            draw_stem(img, cx - 40, t_x, t_y, h, is_left_curve=True)
            # Draw Stem 2 to Pinky Tip (base shifted right)
            draw_stem(img, cx + 40, p_x, p_y, h, is_left_curve=False)

            # Draw Flower 1 (Orange/Yellow) at Thumb Tip
            draw_flower(img, t_x, t_y, openness, flower_type=0)
            # Draw Flower 2 (Pink/Purple) at Pinky Tip
            draw_flower(img, p_x, p_y, openness, flower_type=1)
            
            # Display the bloom text near the palm center
            cv2.putText(img, f'Bloom: {int(openness * 100)}%', (cx + 20, int(palm_center.y * h) - 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # Show the final image
    cv2.imshow("Interactive Python Flower", img)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
detector.close()
cv2.destroyAllWindows()