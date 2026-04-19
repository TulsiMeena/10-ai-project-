import cv2
import yaml
import uvicorn
import asyncio
import numpy as np
import time
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from core.controller import AIController
from utils.logger import logger

# Load configuration
with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

app = FastAPI(title=config['system']['name'])

# Initialize Controller
controller = AIController(config)

# Note: Module initialization will be handled carefully to avoid import errors
# before they are fully implemented.
try:
    from modules.face_detector import FaceDetectorModule
    face_module = FaceDetectorModule("FaceDetector", config['modules']['face_detector'])
    controller.add_module(face_module)
except ImportError:
    logger.warning("FaceDetectorModule not found yet. Skipping...")
except Exception as e:
    logger.error(f"Failed to load FaceDetectorModule: {e}")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def index():
    from fastapi.responses import FileResponse
    return FileResponse('static/index.html')

def gen_frames():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        logger.warning("Camera not found. Using black frames for simulation.")
        # Create a blank black frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        while True:
            processed_frame, _ = controller.process_frame(frame.copy())
            ret, buffer = cv2.imencode('.jpg', processed_frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            time.sleep(0.03)
    else:
        while True:
            success, frame = cap.read()
            if not success:
                break
            else:
                processed_frame, _ = controller.process_frame(frame)
                ret, buffer = cv2.imencode('.jpg', processed_frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.get("/video_feed")
async def video_feed():
    from fastapi.responses import StreamingResponse
    return StreamingResponse(gen_frames(),
                             media_type="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
