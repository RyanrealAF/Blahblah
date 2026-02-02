const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('audioInput');
const transcribeBtn = document.getElementById('transcribeBtn');
const renderBtn = document.getElementById('renderBtn');
const logA = document.getElementById('logTrackA');
let currentFile = null;

// Audio Context for Visualization
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

// 1. File Handling
dropZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFile);

function handleFile(e) {
    const file = e.target.files[0];
    if (file) {
        currentFile = file;
        dropZone.innerHTML = `<p style="color:#0f0;">LOADED: ${file.name}</p>`;
        transcribeBtn.classList.remove('disabled');
        visualizeAudio(file, 'inputCanvas');
        logA.textContent = "SYSTEM READY. FILE LOADED.";
    }
}

// 2. Visualization Logic (Real Analysis)
async function visualizeAudio(fileOrUrl, canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let arrayBuffer;

    try {
        if (fileOrUrl instanceof File) {
            arrayBuffer = await fileOrUrl.arrayBuffer();
        } else {
            const resp = await fetch(fileOrUrl);
            arrayBuffer = await resp.arrayBuffer();
        }

        const audioBuffer = await audioCtx.decodeAudioData(arrayBuffer);
        const rawData = audioBuffer.getChannelData(0);
        const step = Math.ceil(rawData.length / canvas.width);

        ctx.fillStyle = "#1a1a1a";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.beginPath();
        ctx.strokeStyle = canvasId === 'inputCanvas' ? "#00ffcc" : "#ff9900";
        ctx.lineWidth = 1;

        for (let i = 0; i < canvas.width; i++) {
            let min = 1.0;
            let max = -1.0;
            for (let j = 0; j < step; j++) {
                const datum = rawData[i * step + j];
                if (datum < min) min = datum;
                if (datum > max) max = datum;
            }
            // Normalize for canvas height
            const y1 = (1 + min) * 50;
            const y2 = (1 + max) * 50;
            ctx.moveTo(i, y1);
            ctx.lineTo(i, y2);
        }
        ctx.stroke();
    } catch (e) {
        console.error("Visualization failed", e);
    }
}

// 3. Track A: Transcribe
transcribeBtn.addEventListener('click', async () => {
    if (!currentFile || transcribeBtn.classList.contains('disabled')) return;
    
    logA.textContent = ">>> EXECUTING TRANSCRIBE PIPELINE...";
    transcribeBtn.textContent = "PROCESSING...";
    
    const formData = new FormData();
    formData.append('file', currentFile);
    formData.append('threshold', document.getElementById('thresholdKnob').value);

    try {
        const res = await fetch('/api/transcribe', { method: 'POST', body: formData });
        const data = await res.json();
        
        if (data.error) throw new Error(data.error);

        logA.innerHTML = `COMPLETE.<br>DIAGNOSTICS: ${JSON.stringify(data.diagnostics)}<br>WARNINGS: ${data.diagnostics.warnings.length}`;
        transcribeBtn.textContent = "TRANSCRIBE DONE";
        transcribeBtn.classList.add("disabled");
        renderBtn.classList.remove("disabled");
        
    } catch (err) {
        logA.textContent = "ERROR: " + err;
        transcribeBtn.textContent = "TRANSCRIBE FAILED";
    }
});

// 4. Track B: Render
renderBtn.addEventListener('click', async () => {
    if (renderBtn.classList.contains('disabled')) return;
    renderBtn.textContent = "RENDERING...";
    const formData = new FormData();
    formData.append('humanize', document.getElementById('humanizeSwitch').checked);
    formData.append('seed', document.getElementById('seedInput').value);

    try {
        const res = await fetch('/api/render', { method: 'POST', body: formData });
        const data = await res.json();
        if (data.error) throw new Error(data.error);

        // Update Metrics
        document.getElementById('val-mse').textContent = data.metrics.spectral_mse.toFixed(4);
        document.getElementById('val-f1').textContent = data.metrics.note_f1.toFixed(2);
        document.getElementById('val-mfcc').textContent = data.metrics.mfcc_dist.toFixed(2);

        // Play Audio
        const player = document.getElementById('audioPlayer');
        player.src = data.audio_url;

        // Visualize Output
        visualizeAudio(data.audio_url, 'outputCanvas');
        renderBtn.textContent = "RENDER COMPLETE";
    } catch (err) {
        console.error(err);
        renderBtn.textContent = "RENDER FAILED";
    }
});

// Update Knob Display
document.getElementById('thresholdKnob').addEventListener('input', (e) => {
    document.getElementById('threshValue').textContent = e.target.value;
});
