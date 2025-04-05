import cv2
import numpy as np
import mediapipe as mp
import time
import random

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Tic-Tac-Toe board
board = [[None, None, None],
         [None, None, None],
         [None, None, None]]

turn = 'O'  # Player plays as 'O', CPU plays as 'X'
cell_size = 100  # Smaller board
board_x, board_y = 150, 100  # Position offset for board


def check_winner():
    for row in board:
        if row[0] == row[1] == row[2] and row[0] is not None:
            return row[0]

    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] and board[0][col] is not None:
            return board[0][col]

    if board[0][0] == board[1][1] == board[2][2] and board[0][0] is not None:
        return board[0][0]

    if board[0][2] == board[1][1] == board[2][0] and board[0][2] is not None:
        return board[0][2]

    return None


def reset_board():
    global board, turn
    board = [[None, None, None],
             [None, None, None],
             [None, None, None]]
    turn = 'O'


def get_cell(x, y):
    row = (y - board_y) // cell_size
    col = (x - board_x) // cell_size
    if 0 <= row < 3 and 0 <= col < 3:
        return row, col
    return None, None


def cpu_move():
    empty_cells = [(r, c) for r in range(3) for c in range(3) if board[r][c] is None]
    if empty_cells:
        r, c = random.choice(empty_cells)
        board[r][c] = 'X'


def tic_tac_toe():
    global turn
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    width, height = 640, 480  # Keeping a smaller view for hand movement

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (width, height))
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        hand_detected = False
        if turn == 'O' and results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                hand_detected = True
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

                # Detect a pinch gesture (thumb and index finger close together)
                x_thumb, y_thumb = int(thumb_tip.x * width), int(thumb_tip.y * height)
                x_index, y_index = int(index_tip.x * width), int(index_tip.y * height)
                distance = np.sqrt((x_thumb - x_index) ** 2 + (y_thumb - y_index) ** 2)

                if distance < 20:  # If fingers are pinched close together
                    row, col = get_cell(x_index, y_index)
                    if row is not None and board[row][col] is None:
                        board[row][col] = 'O'
                        turn = 'X'
                        time.sleep(0.5)

        # CPU makes a move after the player
        if turn == 'X':
            time.sleep(0.5)
            cpu_move()
            turn = 'O'

        # Draw grid
        for i in range(1, 3):
            cv2.line(frame, (board_x, board_y + i * cell_size), (board_x + 3 * cell_size, board_y + i * cell_size),
                     (255, 255, 255), 3)
            cv2.line(frame, (board_x + i * cell_size, board_y), (board_x + i * cell_size, board_y + 3 * cell_size),
                     (255, 255, 255), 3)

        # Draw X and O
        for r in range(3):
            for c in range(3):
                center_x = board_x + c * cell_size + cell_size // 2
                center_y = board_y + r * cell_size + cell_size // 2
                if board[r][c] == 'O':
                    cv2.circle(frame, (center_x, center_y), 30, (0, 0, 255), 3)
                elif board[r][c] == 'X':
                    cv2.line(frame, (center_x - 25, center_y - 25), (center_x + 25, center_y + 25), (255, 0, 0), 3)
                    cv2.line(frame, (center_x + 25, center_y - 25), (center_x - 25, center_y + 25), (255, 0, 0), 3)

        winner = check_winner()
        if winner:
            cv2.putText(frame, f"{winner} Wins!", (200, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
            cv2.imshow("Tic-Tac-Toe", frame)
            cv2.waitKey(2000)
            reset_board()

        if hand_detected:
            cv2.putText(frame, "Move hand & pinch to place mark", (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (255, 255, 0), 2)

        cv2.imshow("Tic-Tac-Toe", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    tic_tac_toe()
