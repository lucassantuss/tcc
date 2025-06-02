function mediapipe() {
    const videoElement = document.createElement('video');
    videoElement.style.display = 'none'; // esconde o vídeo nativo
    document.body.appendChild(videoElement);

    const canvasElement = document.getElementById('videoCanvas');
    const canvasCtx = canvasElement.getContext('2d');
    let comboExercicio = $('#comboExercicio').val();

    let counter = 0;
    let stage = '---';
    let lastAngle = 0;
    let anguloEsquerdo = 0;
    let anguloDireito = 0;

    var landmark = {
        // ROSCA DIRETA
        LEFT_SHOULDER: 11,
        LEFT_ELBOW: 13,
        LEFT_WRIST: 15,

        // MEIO AGACHAMENTO
        LEFT_HIP: 24,
        LEFT_KNEE: 26,
        LEFT_ANKLE: 28,
        RIGHT_HIP: 23,
        RIGHT_KNEE: 25,
        RIGHT_ANKLE: 27
    };

    $(document).ready(function () {
        $('#comboExercicio').change(function () {
            comboExercicio = $(this).val();
            console.log(comboExercicio);
            counter = 0;
            stage = '---';
            lastAngle = 0;
        });
    });

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

    function onResults(results) {
        canvasCtx.save();
        canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
        canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);

        if (results.poseLandmarks) {
            // Traçar pontos e linhas
            drawConnectors(canvasCtx, results.poseLandmarks, POSE_CONNECTIONS, { color: '#0051ff', lineWidth: 4 });
            drawLandmarks(canvasCtx, results.poseLandmarks, { color: '#FF0000', lineWidth: 4 });

            analisarExercicio(results.poseLandmarks);
        }

        canvasCtx.restore();

        document.getElementById('counter').textContent = counter;
        document.getElementById('stage').textContent = stage;
        document.getElementById('angle').textContent = lastAngle.toFixed(2);
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
        switch (comboExercicio) {
            case 'roscaDireta':
                var leftShoulder = valorPoseLandmark(landmarks, landmark.LEFT_SHOULDER);
                var leftElbow = valorPoseLandmark(landmarks, landmark.LEFT_ELBOW);
                var leftWrist = valorPoseLandmark(landmarks, landmark.LEFT_WRIST);

                anguloEsquerdo = calcularAngulo(leftShoulder, leftElbow, leftWrist);

                if (anguloEsquerdo > 145) {
                    stage = 'baixo';
                }
                if (anguloEsquerdo < 30 && stage === 'baixo') {
                    stage = 'cima';
                    counter++;
                }

                var elbow = landmarks[landmark.LEFT_ELBOW]; // Cotovelo esquerdo
                var x = (elbow.x * canvasElement.width) + 10;
                var y = (elbow.y * canvasElement.height) - 10;
                canvasCtx.font = "40px Arial";
                canvasCtx.fillStyle = "#00FF00";
                canvasCtx.fillText(`${anguloEsquerdo.toFixed(2)}°`, x, y);
                lastAngle = anguloEsquerdo;
                break;
            case 'meioAgachamento':
                var leftHip = valorPoseLandmark(landmarks, landmark.LEFT_HIP);
                var leftKnee = valorPoseLandmark(landmarks, landmark.LEFT_KNEE);
                var leftAnkle = valorPoseLandmark(landmarks, landmark.LEFT_ANKLE);

                var rightHip = valorPoseLandmark(landmarks, landmark.RIGHT_HIP);
                var rightKnee = valorPoseLandmark(landmarks, landmark.RIGHT_KNEE);
                var rightAnkle = valorPoseLandmark(landmarks, landmark.RIGHT_ANKLE);

                anguloEsquerdo = calcularAngulo(leftHip, leftKnee, leftAnkle);
                anguloDireito = calcularAngulo(rightHip, rightKnee, rightAnkle);

                if (anguloEsquerdo >= 170 && anguloDireito >= 170) {
                    stage = 'baixo';
                }
                if ((anguloEsquerdo <= 100 && anguloDireito <= 100) && stage === 'baixo') {
                    stage = 'cima';
                    counter++;
                }

                canvasCtx.font = "40px Arial";
                canvasCtx.fillStyle = "#00FF00";

                // Joelho Esquerdo
                var lKnee = landmarks[landmark.LEFT_KNEE];
                var x = (lKnee.x * canvasElement.width) + 10;
                var y = (lKnee.y * canvasElement.height) - 10;
                canvasCtx.fillText(`${anguloEsquerdo.toFixed(2)}°`, x, y);
                
                // Joelho Direito
                var rKnee = landmarks[landmark.RIGHT_KNEE];
                var x = (rKnee.x * canvasElement.width) + 10;
                var y = (rKnee.y * canvasElement.height) - 10;
                canvasCtx.fillText(`${anguloDireito.toFixed(2)}°`, x, y);

                lastAngle = anguloEsquerdo;
                break;
            default:
                return;
                break;
        }
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