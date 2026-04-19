import cv2
import numpy as np
import yaml
from core.controller import AIController
from modules.face_detector import FaceDetectorModule
from utils.logger import logger

def test_pipeline():
    # 1. Load config
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # 2. Initialize Controller
    controller = AIController(config)

    # 3. Initialize Module
    face_module = FaceDetectorModule("FaceDetector", config['modules']['face_detector'])
    controller.add_module(face_module)

    # 4. Create a dummy frame (black image)
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    # 5. Process frame
    logger.info("Processing test frame...")
    processed_frame, results = controller.process_frame(frame)

    # 6. Verify results
    assert 'FaceDetector' in results
    assert 'faces' in results['FaceDetector']
    assert processed_frame.shape == (480, 640, 3)

    logger.info("Integration test passed successfully!")

if __name__ == "__main__":
    try:
        test_pipeline()
    except Exception as e:
        logger.error(f"Integration test failed: {e}")
        exit(1)
