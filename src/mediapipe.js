function mediapipe() {
    const videoElement = document.createElement('video');
    videoElement.style.display = 'none'; // esconde o vídeo nativo
    document.body.appendChild(videoElement);

    const canvasElement = document.getElementById('videoCanvas');
    const canvasCtx = canvasElement.getContext('2d');

    let counter = 0;
    let stage = '---';
    let lastAngle = 0;

    // Ajustar canvas para o tamanho máximo da câmera disponível
    async function setupCamera() {
        const constraints = {
            audio: false,
            video: {
                facingMode: 'user',
                width: { ideal: window.innerWidth },
                height: { ideal: window.innerHeight }
            }

        };

        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        videoElement.srcObject = stream;

        await videoElement.play();

        canvasElement.width = window.innerWidth;
        canvasElement.height = window.innerHeight;

    }

    function calcularAngulo(a, b, c) {
        const radians = Math.atan2(c[1] - b[1], c[0] - b[0]) - Math.atan2(a[1] - b[1], a[0] - b[0]);
        let angulo = Math.abs(radians * 180.0 / Math.PI);
        if (angulo > 180.0) angulo = 360 - angulo;
        return angulo;
    }

    function valorPoseLandmark(landmarks, index) {
        if (!landmarks || landmarks.length <= index) return [0, 0];
        return [landmarks[index].x, landmarks[index].y];
    }

    function analisarExercicio(landmarks) {
        if (!landmarks) return;

        const LEFT_SHOULDER = 11;
        const LEFT_ELBOW = 13;
        const LEFT_WRIST = 15;

        const leftShoulder = valorPoseLandmark(landmarks, LEFT_SHOULDER);
        const leftElbow = valorPoseLandmark(landmarks, LEFT_ELBOW);
        const leftWrist = valorPoseLandmark(landmarks, LEFT_WRIST);

        const angulo = calcularAngulo(leftShoulder, leftElbow, leftWrist);
        lastAngle = angulo;

        if (angulo > 155) {
            stage = 'baixo';
        }
        if (angulo < 39 && stage === 'baixo') {
            stage = 'cima';
            counter++;
        }
    }


    function onResults(results) {
        canvasCtx.save();
        canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
        canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);

        if (results.poseLandmarks) {
            drawConnectors(canvasCtx, results.poseLandmarks, POSE_CONNECTIONS, { color: '#0051ff', lineWidth: 4 });
            drawLandmarks(canvasCtx, results.poseLandmarks, { color: '#FF0000', lineWidth: 4 });

            analisarExercicio(results.poseLandmarks);

            const elbow = results.poseLandmarks[13]; // Cotovelo esquerdo
            const x = (elbow.x * canvasElement.width) + 10;
            const y = (elbow.y * canvasElement.height) - 10;

            canvasCtx.font = "40px Arial";
            canvasCtx.fillStyle = "#00FF00";
            canvasCtx.fillText(`${lastAngle.toFixed(2)}°`, x, y);
        }

        canvasCtx.restore();

        document.getElementById('counter').textContent = counter;
        document.getElementById('stage').textContent = stage;
        document.getElementById('angle').textContent = lastAngle.toFixed(2);
    }

    async function main() {
        await setupCamera();

        const pose = new window.Pose({
            locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`
        });
        pose.setOptions({
            modelComplexity: 1,
            smoothLandmarks: true,
            minDetectionConfidence: 0.5,
            minTrackingConfidence: 0.5
        });
        pose.onResults(onResults);

        async function detectFrame() {
            await pose.send({ image: videoElement });
            requestAnimationFrame(detectFrame);
        }

        detectFrame();
    }
    return {
        main: main,
        onResults: onResults,
        analisarExercicio: analisarExercicio,
        valorPoseLandmark: valorPoseLandmark,
        calcularAngulo: calcularAngulo,
        setupCamera: setupCamera
    }
}