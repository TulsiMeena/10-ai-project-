/**
 * Module 1: Face Detection + Tracking (Client-side)
 * Uses MediaPipe Face Detection JS SDK.
 */
class FaceDetectorModule extends BaseModule {
    constructor(name) {
        super(name);
        this.faceDetection = null;
        this.results = null;

        // Tracking state
        this.nextId = 0;
        this.trackedFaces = new Map(); // id -> {centroid: {x,y}, disappeared: frames}
        this.maxDisappeared = 20;
    }

    async init() {
        this.faceDetection = new FaceDetection({
            locateFile: (file) => {
                return `https://cdn.jsdelivr.net/npm/@mediapipe/face_detection/${file}`;
            }
        });

        this.faceDetection.setOptions({
            model: 'short',
            minDetectionConfidence: 0.5
        });

        this.faceDetection.onResults((results) => {
            this.results = results;
        });

        console.log("FaceDetectorModule initialized.");
    }

    async process(videoElement) {
        await this.faceDetection.send({ image: videoElement });

        if (!this.results || !this.results.detections) return { faces: [] };

        const currentDetections = this.results.detections.map(det => {
            const bbox = det.boundingBox;
            return {
                bbox: [bbox.xCenter - bbox.width/2, bbox.yCenter - bbox.height/2, bbox.width, bbox.height],
                centroid: { x: bbox.xCenter, y: bbox.yCenter },
                confidence: det.categories[0].score
            };
        });

        // Persistent Tracking Logic
        const updatedTracks = new Map();
        const matchedIndices = new Set();

        // 1. Update existing tracks
        for (const [id, tdata] of this.trackedFaces.entries()) {
            let minDist = 0.08; // threshold
            let bestIdx = -1;

            for (let i = 0; i < currentDetections.length; i++) {
                if (matchedIndices.has(i)) continue;
                const dist = Math.sqrt(
                    Math.pow(tdata.centroid.x - currentDetections[i].centroid.x, 2) +
                    Math.pow(tdata.centroid.y - currentDetections[i].centroid.y, 2)
                );
                if (dist < minDist) {
                    minDist = dist;
                    bestIdx = i;
                }
            }

            if (bestIdx !== -1) {
                currentDetections[bestIdx].id = id;
                updatedTracks.set(id, { centroid: currentDetections[bestIdx].centroid, disappeared: 0 });
                matchedIndices.add(bestIdx);
            } else {
                tdata.disappeared++;
                if (tdata.disappeared <= this.maxDisappeared) {
                    updatedTracks.set(id, tdata);
                }
            }
        }

        // 2. Add new detections
        for (let i = 0; i < currentDetections.length; i++) {
            if (!matchedIndices.has(i)) {
                currentDetections[i].id = this.nextId;
                updatedTracks.set(this.nextId, { centroid: currentDetections[i].centroid, disappeared: 0 });
                this.nextId++;
            }
        }

        this.trackedFaces = updatedTracks;
        return { faces: currentDetections.filter(d => d.id !== undefined) };
    }

    draw(ctx, results, canvas) {
        if (!results || !results.faces) return;

        const { width, height } = canvas;

        results.faces.forEach(face => {
            const [x, y, w, h] = face.bbox;

            // Draw Box
            ctx.strokeStyle = '#00ff88';
            ctx.lineWidth = 3;
            ctx.strokeRect(x * width, y * height, w * width, h * height);

            // Draw Label
            ctx.fillStyle = '#00ff88';
            ctx.font = 'bold 16px Courier New';
            const label = `ID:${face.id} [${(face.confidence * 100).toFixed(0)}%]`;
            ctx.fillText(label, x * width, y * height - 10);

            // Draw scan lines effect
            ctx.fillStyle = 'rgba(0, 255, 136, 0.1)';
            ctx.fillRect(x * width, y * height, w * width, 2);
        });
    }
}
