# leafsdk/core/vision/camera_stabilizer.py

import cv2
import numpy as np
from leafsdk import logger

class CameraStabilizer:
    def __init__(self, camera_index=0):
        self.cap = cv2.VideoCapture(camera_index)
        self.prev_gray = None

    def compute_optical_flow(self):
        ret, frame = self.cap.read()
        if not ret:
            logger.warning("Camera frame read failed.")
            return None

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if self.prev_gray is None:
            self.prev_gray = gray
            logger.debug("Initialized optical flow.")
            return None

        flow = cv2.calcOpticalFlowFarneback(
            self.prev_gray, gray, None,
            0.5, 3, 15, 3, 5, 1.2, 0
        )
        self.prev_gray = gray
        avg_flow = np.mean(flow, axis=(0, 1))
        logger.info(f"Optical flow: {avg_flow}")
        return avg_flow

    def release(self):
        self.cap.release()
        logger.info("Camera released.")
