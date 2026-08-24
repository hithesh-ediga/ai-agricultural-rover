"""
AI Agricultural Rover - Crop Disease Detection Node
Uses OpenCV to analyze live ESP32-CAM feed for leaf discoloration and lesions.
"""

import cv2
import numpy as np

def analyze_leaf_health(image_frame):
    """
    Applies color masking to detect unhealthy brown/yellow spots on green leaves.
    """
    # Convert image to HSV color space for better color filtering
    hsv = cv2.cvtColor(image_frame, cv2.COLOR_BGR2HSV)
    
    # Define color range for healthy green
    lower_green = np.array([35, 50, 50])
    upper_green = np.array([85, 255, 255])
    
    # Define color range for disease spots (brown/yellow)
    lower_disease = np.array([10, 100, 20])
    upper_disease = np.array([30, 255, 200])
    
    # Create masks
    healthy_mask = cv2.inRange(hsv, lower_green, upper_green)
    disease_mask = cv2.inRange(hsv, lower_disease, upper_disease)
    
    # Calculate disease percentage
    healthy_pixels = cv2.countNonZero(healthy_mask)
    disease_pixels = cv2.countNonZero(disease_mask)
    total_pixels = healthy_pixels + disease_pixels
    
    if total_pixels > 0:
        infection_rate = (disease_pixels / total_pixels) * 100
        return infection_rate
    return 0.0

if __name__ == "__main__":
    print("Initializing Vision Node...")
    # Placeholder for ESP32-CAM stream URL: cv2.VideoCapture("http://<ESP32_IP>/stream")
    # Using local camera (0) for testing
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not connect to camera stream.")
        exit()
        
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        infection_rate = analyze_leaf_health(frame)
        
        # Display alert on feed if infection is high
        if infection_rate > 15.0:
            cv2.putText(frame, f"WARNING: Disease Detected! ({infection_rate:.1f}%)", 
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        cv2.imshow('Crop Monitor Stream', frame)
        
        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()