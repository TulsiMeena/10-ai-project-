/**
 * Abstract Base Class for all AI Modules in JS.
 */
class BaseModule {
    constructor(name, config = {}) {
        if (this.constructor === BaseModule) {
            throw new Error("BaseModule is abstract and cannot be instantiated directly.");
        }
        this.name = name;
        this.config = config;
        this.enabled = config.enabled !== false;
    }

    /**
     * Process frame data and return results.
     */
    async process(videoElement) {
        throw new Error("Method 'process()' must be implemented.");
    }

    /**
     * Draw visual overlays on the canvas.
     */
    draw(ctx, results, canvas) {
        throw new Error("Method 'draw()' must be implemented.");
    }
}
