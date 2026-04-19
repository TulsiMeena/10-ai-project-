import cv2
import mediapipe as mp
import numpy as np
import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from core.base_module import BaseModule
from utils.logger import logger

class FaceDetectorModule(BaseModule):
    """
    Module 1: Face Detection + Tracking
    Uses MediaPipe Tasks for high-performance multi-face detection.
    Includes persistent ID tracking logic with temporal memory.
    """

    def __init__(self, name: str, config: dict = None):
        super().__init__(name, config)

        # Initialize MediaPipe Face Detector Task
        base_options = python.BaseOptions(model_asset_path='models/face_detector.tflite')
        options = vision.FaceDetectorOptions(
            base_options=base_options,
            min_detection_confidence=self.config.get('min_detection_confidence', 0.5)
        )
        self.detector = vision.FaceDetector.create_from_options(options)

        # Tracking state
        self.next_id = 0
        # {id: {'centroid': (x,y), 'last_seen': timestamp, 'disappeared': frames}}
        self.tracked_faces = {}
        self.max_disappeared = 15 # Frames to keep ID if face is lost
        logger.info("Face Detector Module initialized with MediaPipe Tasks and Persistent Tracking.")

    def _calculate_distance(self, c1, c2):
        return np.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)

    def process(self, frame: np.ndarray) -> dict:
        """
        Detect faces and extract bounding boxes.
        Includes Centroid Tracking with frame persistence.
        """
        results = {}
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        detection_result = self.detector.detect(mp_image)

        current_detections = []
        if detection_result.detections:
            for detection in detection_result.detections:
                bbox = detection.bounding_box
                x, y, w, h = bbox.origin_x, bbox.origin_y, bbox.width, bbox.height
                score = detection.categories[0].score
                centroid = (x + w // 2, y + h // 2)

                current_detections.append({
                    'bbox': [x, y, w, h],
                    'confidence': score,
                    'centroid': centroid
                })

        # --- Persistent Centroid Tracking ---
        # 1. Update existing tracks
        matched_detections = set()
        updated_tracks = {}

        # Copy current tracks to attempt matching
        track_ids = list(self.tracked_faces.keys())

        if len(current_detections) > 0:
            for tid in track_ids:
                tdata = self.tracked_faces[tid]

                # Find closest detection
                min_dist = 50 # threshold
                best_idx = -1

                for i, det in enumerate(current_detections):
                    if i in matched_detections: continue
                    dist = self._calculate_distance(tdata['centroid'], det['centroid'])
                    if dist < min_dist:
                        min_dist = dist
                        best_idx = i

                if best_idx != -1:
                    # Match found
                    det = current_detections[best_idx]
                    det['id'] = tid
                    updated_tracks[tid] = {
                        'centroid': det['centroid'],
                        'disappeared': 0
                    }
                    matched_detections.add(best_idx)
                else:
                    # No match for this track
                    tdata['disappeared'] += 1
                    if tdata['disappeared'] <= self.max_disappeared:
                        updated_tracks[tid] = tdata
        else:
            # No detections, increment all disappeared
            for tid in track_ids:
                self.tracked_faces[tid]['disappeared'] += 1
                if self.tracked_faces[tid]['disappeared'] <= self.max_disappeared:
                    updated_tracks[tid] = self.tracked_faces[tid]

        # 2. Register new detections
        for i, det in enumerate(current_detections):
            if i not in matched_detections:
                det['id'] = self.next_id
                updated_tracks[self.next_id] = {
                    'centroid': det['centroid'],
                    'disappeared': 0
                }
                self.next_id += 1

        self.tracked_faces = updated_tracks
        results['faces'] = [d for d in current_detections if 'id' in d]
        return results

    def draw(self, frame: np.ndarray, results: dict) -> np.ndarray:
        faces = results.get('faces', [])
        for face in faces:
            x, y, w, h = face['bbox']
            conf = face['confidence']
            face_id = face.get('id', '?')

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            label = f"ID: {face_id} [{conf:.2f}]"
            cv2.putText(frame, label, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        return frame
