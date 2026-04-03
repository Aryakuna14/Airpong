import cv2
import mediapipe as mp
import numpy as np
import sys  # <--- THIS WAS MISSING

# 1. Initialize MediaPipe Hand Tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# 2. Game Constants
WIDTH, HEIGHT = 1280, 720
BALL_RADIUS = 15
PADDLE_WIDTH, PADDLE_HEIGHT = 20, 120

# 3. Game State Variables
ball_pos = [WIDTH // 2, HEIGHT // 2]
ball_speed = [12, 12]
score_left = 0
score_right = 0

# Use 0 or 1 depending on your webcam
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) 

# Check if it opened correctly
if not cap.isOpened():
    print("❌ ERROR: Could not open webcam.")
    sys.exit()
else:
    print("✅ SUCCESS: Camera found! Opening game window...")

cap.set(3, WIDTH)
cap.set(4, HEIGHT)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        break

    # Flip frame for mirror effect
    frame = cv2.flip(frame, 1)
    
    # MediaPipe needs RGB, OpenCV uses BGR
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
    results = hands.process(img_rgb)

    # Default paddle positions (center)
    paddle_left_y = HEIGHT // 2 - PADDLE_HEIGHT // 2
    paddle_right_y = HEIGHT // 2 - PADDLE_HEIGHT // 2

    # 4. Hand Tracking Logic
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            x = int(hand_landmarks.landmark[8].x * WIDTH)
            y = int(hand_landmarks.landmark[8].y * HEIGHT)

            if x < WIDTH // 2:
                paddle_left_y = y - PADDLE_HEIGHT // 2
            else:
                paddle_right_y = y - PADDLE_HEIGHT // 2

            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # 5. Ball Physics
    ball_pos[0] += ball_speed[0]
    ball_pos[1] += ball_speed[1]

    if ball_pos[1] <= BALL_RADIUS or ball_pos[1] >= HEIGHT - BALL_RADIUS:
        ball_speed[1] *= -1

    # 6. Collision Detection
    if ball_pos[0] <= PADDLE_WIDTH + BALL_RADIUS:
        if paddle_left_y < ball_pos[1] < paddle_left_y + PADDLE_HEIGHT:
            ball_speed[0] *= -1
        else:
            score_right += 1
            ball_pos = [WIDTH // 2, HEIGHT // 2]

    if ball_pos[0] >= WIDTH - PADDLE_WIDTH - BALL_RADIUS:
        if paddle_right_y < ball_pos[1] < paddle_right_y + PADDLE_HEIGHT:
            ball_speed[0] *= -1
        else:
            score_left += 1
            ball_pos = [WIDTH // 2, HEIGHT // 2]

    # 7. Drawing
    cv2.rectangle(frame, (0, paddle_left_y), (PADDLE_WIDTH, paddle_left_y + PADDLE_HEIGHT), (0, 255, 0), -1)
    cv2.rectangle(frame, (WIDTH - PADDLE_WIDTH, paddle_right_y), (WIDTH, paddle_right_y + PADDLE_HEIGHT), (0, 0, 255), -1)
    cv2.circle(frame, (int(ball_pos[0]), int(ball_pos[1])), BALL_RADIUS, (255, 255, 255), -1)
    cv2.putText(frame, f"{score_left} | {score_right}", (WIDTH//2 - 50, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)

    cv2.imshow("Air Pong", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()