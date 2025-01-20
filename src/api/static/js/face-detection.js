async function detectFaces(imageElement) {
    try {
        const response = await fetch('/api/detect-faces', {
            method: 'POST',
            body: JSON.stringify({
                image_url: imageElement.src
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        return await response.json();
    } catch (error) {
        console.error('Face detection failed:', error);
        return null;
    }
}

function drawFaceOverlay(ctx, faceData, adjustments) {
    if (!faceData) return;
    
    const {scale, x, y, rotation} = adjustments;
    
    // Transformationen anwenden
    ctx.save();
    ctx.translate(x, y);
    ctx.scale(scale, scale);
    ctx.rotate(rotation * Math.PI / 180);
    
    // Gesichtsmarkierungen zeichnen
    ctx.strokeStyle = '#00ff00';
    ctx.lineWidth = 2;
    
    faceData.landmarks.forEach(point => {
        ctx.beginPath();
        ctx.arc(point.x, point.y, 2, 0, 2 * Math.PI);
        ctx.stroke();
    });
    
    // Gesichtsrahmen zeichnen
    ctx.strokeRect(
        faceData.bbox.x,
        faceData.bbox.y,
        faceData.bbox.width,
        faceData.bbox.height
    );
    
    ctx.restore();
}

document.addEventListener('DOMContentLoaded', function() {
    const sourceInput = document.getElementById('source-image');
    const targetInput = document.getElementById('target-image');
    const sourcePreview = document.getElementById('source-preview');
    const targetPreview = document.getElementById('target-preview');
    const startButton = document.getElementById('start-swap');
    const resultSection = document.querySelector('.result-section');
    const resultImage = document.getElementById('result-image');

    // Preview-Funktionen
    function showPreview(file, previewElement) {
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                previewElement.src = e.target.result;
                previewElement.classList.remove('hidden');
            }
            reader.readAsDataURL(file);
        }
    }

    // Event Listener für File Uploads
    sourceInput.addEventListener('change', (e) => {
        showPreview(e.target.files[0], sourcePreview);
        checkCanStart();
    });

    targetInput.addEventListener('change', (e) => {
        showPreview(e.target.files[0], targetPreview);
        checkCanStart();
    });

    // Prüft ob der Start-Button aktiviert werden kann
    function checkCanStart() {
        startButton.disabled = !(sourceInput.files[0] && targetInput.files[0]);
    }

    // Face Swap Prozess
    startButton.addEventListener('click', async () => {
        const formData = new FormData();
        formData.append('source', sourceInput.files[0]);
        formData.append('target', targetInput.files[0]);
        formData.append('model_id', document.getElementById('model-select').value);

        try {
            startButton.disabled = true;
            startButton.textContent = 'Verarbeite...';

            const response = await fetch('/api/inference/swap', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('Fehler beim Face Swap');

            const result = await response.json();
            resultImage.src = result.output_url;
            resultSection.classList.remove('hidden');
        } catch (error) {
            console.error('Fehler:', error);
            alert('Fehler beim Face Swap: ' + error.message);
        } finally {
            startButton.disabled = false;
            startButton.textContent = 'Face Swap starten';
        }
    });
}); 