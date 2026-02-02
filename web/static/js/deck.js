const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('audioInput');
const transcribeBtn = document.getElementById('transcribeBtn');
const renderBtn = document.getElementById('renderBtn');
const logA = document.getElementById('logTrackA');
const statusLed = document.getElementById('statusLed');
const statusText = document.getElementById('statusText');
let currentFile = null;

// Audio Context for Visualization
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

// 1. Knob Logic
function initKnob(knob) {
    let isDragging = false;
    let startY = 0;
    let startVal = parseFloat(knob.dataset.value);
    const min = parseFloat(knob.dataset.min);
    const max = parseFloat(knob.dataset.max);
    const display = document.getElementById(knob.id === 'thresholdKnob' ? 'threshValue' : '');

    function updateKnob(val) {
        val = Math.max(min, Math.min(max, val));
        knob.dataset.value = val;
        // Map 0.1-0.9 to -135 to 135 degrees
        const percent = (val - min) / (max - min);
        const deg = -135 + (percent * 270);
        knob.style.transform = `rotate(${deg}deg)`;
        if (display) display.textContent = val.toFixed(2);
    }

    // Set initial rotation
    updateKnob(startVal);

    knob.addEventListener('mousedown', e => {
        isDragging = true;
        startY = e.clientY;
        startVal = parseFloat(knob.dataset.value);
        e.preventDefault();
    });

    window.addEventListener('mousemove', e => {
        if (!isDragging) return;
        const delta = startY - e.clientY;
        const sensitivity = 0.005;
        updateKnob(startVal + delta * sensitivity);
    });

    window.addEventListener('mouseup', () => {
        isDragging = false;
    });
}

document.querySelectorAll('.knob').forEach(initKnob);

// 2. File Handling
dropZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFile);

function handleFile(e) {
    const file = e.target.files[0];
    if (file) {
        currentFile = file;
        dropZone.querySelector('p').textContent = `LOADED: ${file.name.toUpperCase()}`;
        dropZone.style.borderColor = 'var(--led-cyan)';
        transcribeBtn.classList.remove('disabled');
        transcribeBtn.classList.add('active-btn');
        visualizeAudio(file, 'inputCanvas');
        logA.textContent = "> SOURCE TAPE LOADED. ANALYZER READY.";
    }
}

// 3. Visualization Logic
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

        ctx.fillStyle = "#080808";
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Draw grid lines
        ctx.strokeStyle = "#1a1a1a";
        ctx.lineWidth = 1;
        for(let x=0; x<canvas.width; x+=50) {
            ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
        }

        ctx.beginPath();
        ctx.strokeStyle = canvasId === 'inputCanvas' ? "#00ffcc" : "#ff9900";
        ctx.lineWidth = 1;

        const amp = canvas.height / 2;
        for (let i = 0; i < canvas.width; i++) {
            let min = 1.0;
            let max = -1.0;
            for (let j = 0; j < step; j++) {
                const datum = rawData[i * step + j];
                if (datum < min) min = datum;
                if (datum > max) max = datum;
            }
            ctx.moveTo(i, amp + min * amp);
            ctx.lineTo(i, amp + max * amp);
        }
        ctx.stroke();
    } catch (e) {
        console.error("Visualization failed", e);
    }
}

// 4. Track A: Transcribe
transcribeBtn.addEventListener('click', async () => {
    if (!currentFile || transcribeBtn.classList.contains('disabled')) return;

    logA.textContent = ">>> EXECUTING TRANSCRIBE PIPELINE... [TRACK A]";
    transcribeBtn.textContent = "BUSY...";
    transcribeBtn.classList.add('blink');

    const formData = new FormData();
    formData.append('file', currentFile);
    formData.append('threshold', document.getElementById('thresholdKnob').dataset.value);

    try {
        const res = await fetch('/api/transcribe', { method: 'POST', body: formData });
        const data = await res.json();

        if (data.error) throw new Error(data.error);

        const warnCount = data.diagnostics.warnings.length;
        logA.innerHTML = `> TRACK A COMPLETE.<br>> CONFIDENCE: ${(data.diagnostics.confidence * 100).toFixed(1)}%<br>> WARNINGS: ${warnCount}`;

        transcribeBtn.textContent = "DONE";
        transcribeBtn.classList.remove('active-btn', 'blink');
        transcribeBtn.classList.add('disabled');

        renderBtn.classList.remove('disabled');
        renderBtn.classList.add('active-btn');

        statusLed.className = 'led-indicator active';
        statusText.textContent = "MIDI READY";

    } catch (err) {
        logA.textContent = "!! ERROR: " + err.message;
        transcribeBtn.textContent = "FAIL";
        transcribeBtn.classList.remove('blink');
    }
});

// 5. Track B: Render
renderBtn.addEventListener('click', async () => {
    if (renderBtn.classList.contains('disabled')) return;

    renderBtn.textContent = "RENDERING...";
    renderBtn.classList.add('blink');
    statusText.textContent = "RENDERING...";

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
        document.getElementById('val-mfcc').textContent = data.metrics.mfcc_dist.toFixed(0);

        // Play Audio
        const player = document.getElementById('audioPlayer');
        player.src = data.audio_url + '?t=' + new Date().getTime();

        // Visualize Output
        visualizeAudio(data.audio_url, 'outputCanvas');

        renderBtn.textContent = "RENDER DONE";
        renderBtn.classList.remove('blink');
        statusText.textContent = "OUTPUT READY";

    } catch (err) {
        console.error(err);
        renderBtn.textContent = "FAIL";
        renderBtn.classList.remove('blink');
        statusLed.className = 'led-indicator error';
        statusText.textContent = "RENDER ERROR";
    }
});
