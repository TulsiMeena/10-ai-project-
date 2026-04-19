/**
 * Central Controller for the JS-based AI System.
 */
class AIController {
    constructor() {
        this.modules = [];
        this.video = document.getElementById('input-video');
        this.canvas = document.getElementById('output-canvas');
        this.ctx = this.canvas.getContext('2d');

        this.fps = 0;
        this.lastTime = performance.now();
        this.frameCount = 0;

        console.log("AI Controller initialized.");
    }

    async init() {
        try {
            // Setup Camera
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 1280, height: 720 },
                audio: false
            });
            this.video.srcObject = stream;
            await this.video.play();

            // Match canvas size to video
            this.canvas.width = this.video.videoWidth;
            this.canvas.height = this.video.videoHeight;

            // Load Modules
            const faceModule = new FaceDetectorModule("FaceDetector");
            await faceModule.init();
            this.modules.push(faceModule);

            this.log("System initialized and camera active.");
            this.render();
        } catch (err) {
            console.error("Initialization failed:", err);
            this.log(`CRITICAL ERROR: ${err.message}`);
        }
    }

    async render() {
        this.frameCount++;
        const now = performance.now();
        const delta = now - this.lastTime;

        if (delta >= 1000) {
            this.fps = (this.frameCount * 1000) / delta;
            this.frameCount = 0;
            this.lastTime = now;
            document.getElementById('fps-val').innerText = this.fps.toFixed(1);
        }

        // Draw video frame to canvas
        this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);

        // Process Modules
        for (const module of this.modules) {
            if (module.enabled) {
                const startTime = performance.now();
                const results = await module.process(this.video);
                const latency = performance.now() - startTime;

                module.draw(this.ctx, results, this.canvas);

                if (module.name === "FaceDetector") {
                    document.getElementById('latency-val').innerText = `${latency.toFixed(0)} ms`;
                }
            }
        }

        requestAnimationFrame(() => this.render());
    }

    log(msg) {
        const console = document.getElementById('log-console');
        const entry = document.createElement('div');
        entry.innerText = `[${new Date().toLocaleTimeString()}] ${msg}`;
        console.prepend(entry);
    }
}
