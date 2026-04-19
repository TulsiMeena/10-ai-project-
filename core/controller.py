import time
import numpy as np
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor
from core.base_module import BaseModule
from utils.logger import logger

class AIController:
    """
    Central Controller for the AI System.
    Manages the camera pipeline and asynchronous module execution.
    """

    def __init__(self, config: dict):
        self.config = config
        self.modules: List[BaseModule] = []
        self.executor = ThreadPoolExecutor(max_workers=min(len(config['modules']), 4) or 4)
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()
        logger.info("AI Controller initialized with ThreadPoolExecutor.")

    def add_module(self, module: BaseModule):
        self.modules.append(module)
        logger.info(f"Module added: {module.name}")

    def process_frame(self, frame: np.ndarray) -> (np.ndarray, Dict):
        """
        Execute the pipeline asynchronously:
        1. Run all enabled modules in parallel using threads.
        2. Aggregate results and overlay graphics.
        """
        self.frame_count += 1
        all_results = {}

        # Parallel Execution of Modules
        enabled_modules = [m for m in self.modules if m.enabled]

        def run_module(module):
            try:
                return module.name, module.process(frame)
            except Exception as e:
                logger.error(f"Error in module {module.name}: {e}")
                return module.name, None

        # Execute all modules in parallel
        module_outputs = list(self.executor.map(run_module, enabled_modules))

        # Overlay results sequentially to maintain drawing order
        for name, results in module_outputs:
            if results is not None:
                all_results[name] = results
                # Find corresponding module to call draw
                module = next((m for m in enabled_modules if m.name == name), None)
                if module:
                    frame = module.draw(frame, results)

        # FPS Calculation
        curr_time = time.time()
        elapsed = curr_time - self.start_time
        if elapsed >= 1.0:
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.start_time = curr_time

        frame = self._draw_system_ui(frame)
        return frame, all_results

    def _draw_system_ui(self, frame: np.ndarray) -> np.ndarray:
        import cv2
        cv2.putText(frame, f"FPS: {self.fps:.1f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "SYSTEM LIVE (ASYNC)", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        return frame

    def __del__(self):
        self.executor.shutdown()
