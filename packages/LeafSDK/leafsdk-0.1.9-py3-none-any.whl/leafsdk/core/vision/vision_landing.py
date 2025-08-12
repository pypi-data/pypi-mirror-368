# leafsdk/core/vision/vision_landing.py

import cv2
import numpy as np
from leafsdk import logger

class VisionLanding:
    def __init__(self, camera_index=0, marker_size_cm=20.0):
        self.camera_index = camera_index
        self.marker_size_cm = marker_size_cm
        self.cap = None
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.parameters = cv2.aruco.DetectorParameters()
        self.running = False

    def start_camera(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            logger.error("Failed to open camera.")
            raise RuntimeError("Camera not accessible.")
        logger.info("Camera started.")

    def stop_camera(self):
        if self.cap:
            self.cap.release()
            self.running = False
            logger.info("Camera stopped.")

    def detect_marker_center(self):
        if not self.cap:
            logger.warning("Camera not started.")
            return None

        ret, frame = self.cap.read()
        if not ret:
            logger.warning("Failed to read frame.")
            return None

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = cv2.aruco.detectMarkers(gray, self.aruco_dict, parameters=self.parameters)

        if ids is not None:
            for marker_corners in corners:
                corner_array = marker_corners[0]
                center = np.mean(corner_array, axis=0)
                logger.info(f"Marker detected at: {center}")
                return tuple(center)

        logger.debug("No marker detected.")
        return None

    def track_and_land_loop(self):
        logger.info("Starting vision landing loop.")
        self.running = True
        while self.running:
            center = self.detect_marker_center()
            if center:
                logger.info(f"Marker center at {center}")
                # Placeholder: Send control signals here
            cv2.waitKey(10)  # to avoid freezing
