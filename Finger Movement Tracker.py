import cv2
import mediapipe as mp
import numpy as np
from math import hypot

class FingerCounter:
    def __init__(self):
        # Initialize mediapipe hands module
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Finger tip IDs (using MediaPipe hand landmark indices)
        self.finger_tips = [4, 8, 12, 16, 20]  # thumb, index, middle, ring, pinky
        self.finger_bases = [2, 5, 9, 13, 17]  # corresponding base points
        
    def calculate_distance(self, p1, p2):
        """Calculate Euclidean distance between two points"""
        return hypot(p1.x - p2.x, p1.y - p2.y)
    
    def is_finger_extended(self, landmarks, tip_idx, base_idx, is_thumb=False):
        """
        Determine if a finger is extended based on its tip and base positions
        Different logic for thumb vs other fingers
        """
        if is_thumb:
            # For thumb, compare with palm center
            palm_center = landmarks[0]
            return landmarks[tip_idx].x < palm_center.x if landmarks[0].x < 0.5 else landmarks[tip_idx].x > palm_center.x
        else:
            # For other fingers, compare tip-base distance with middle-base distance
            middle_point = landmarks[base_idx - 1]
            tip_to_base = self.calculate_distance(landmarks[tip_idx], landmarks[base_idx])
            mid_to_base = self.calculate_distance(middle_point, landmarks[base_idx])
            return tip_to_base > mid_to_base

    def count_fingers(self, frame):
        """Process frame and count extended fingers"""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.hands.process(rgb_frame)
        
        # Lists to store counts for both hands
        finger_counts = []
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )
                
                # Count extended fingers
                count = 0
                landmarks = hand_landmarks.landmark
                
                # Check thumb
                if self.is_finger_extended(landmarks, self.finger_tips[0], self.finger_bases[0], True):
                    count += 1
                
                # Check other fingers
                for tip_idx, base_idx in zip(self.finger_tips[1:], self.finger_bases[1:]):
                    if self.is_finger_extended(landmarks, tip_idx, base_idx):
                        count += 1
                
                finger_counts.append(count)
        
        return frame, finger_counts

    def run(self):
        """Run the finger counter with webcam feed"""
        cap = cv2.VideoCapture(0)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Flip frame horizontally for more intuitive interaction
            frame = cv2.flip(frame, 1)
            
            # Process frame and get finger counts
            frame, finger_counts = self.count_fingers(frame)
            
            # Display counts
            y_pos = 50
            for i, count in enumerate(finger_counts):
                text = f"Hand {i + 1}: {count} fingers"
                cv2.putText(
                    frame, text, (10, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
                )
                y_pos += 50
            
            # Display total
            if finger_counts:
                total = sum(finger_counts)
                cv2.putText(
                    frame, f"Total: {total} fingers",
                    (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 0), 2
                )
            
            # Show frame
            cv2.imshow('Finger Counter', frame)
            
            # Break loop on 'q' press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Clean up
        cap.release()
        cv2.destroyAllWindows()

def main():
    counter = FingerCounter()
    counter.run()

if __name__ == "__main__":
    main()