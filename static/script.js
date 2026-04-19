document.addEventListener('DOMContentLoaded', () => {
    console.log('AI Camera System Frontend Initialized');

    const videoFeed = document.getElementById('video-feed');
    const statusText = document.getElementById('status-text');

    // Error handling for video feed
    videoFeed.onerror = () => {
        console.error('Failed to load video feed');
        statusText.innerText = 'CONNECTION ERROR';
        statusText.parentElement.style.color = '#ef4444';
        document.querySelector('.status-indicator').style.backgroundColor = '#ef4444';
        document.querySelector('.status-indicator').style.boxShadow = '0 0 10px #ef4444';
    };

    // Keyboard controls for mode switching
    document.addEventListener('keydown', (event) => {
        const key = event.key.toLowerCase();
        console.log(`Key pressed: ${key}`);

        // Example mode switching logic
        if (key === 'f') {
            console.log('Toggling Face Detection');
            // This would typically call a backend API to toggle module
        }
    });

    // Pulse check (Optional)
    setInterval(() => {
        // We could fetch system stats here (FPS, CPU usage, etc.)
    }, 2000);
});
