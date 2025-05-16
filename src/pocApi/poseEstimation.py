import cv2
import mediapipe as mp
import numpy as np
from PIL import Image
import io

mp_pose = mp.solutions.pose

def calcularAngulo(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angulo = np.abs(radians*180.0/np.pi)
    return 360 - angulo if angulo > 180.0 else angulo

def analisar_frame(imagem_bytes, exercicio="rosca_direta_halter_uni"):
    imagem = Image.open(io.BytesIO(imagem_bytes)).convert('RGB')
    imagem_np = np.array(imagem)

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        results = pose.process(imagem_np)
        if not results.pose_landmarks:
            return {"reps": 0, "msg": "Sem detecção"}

        landmarks = results.pose_landmarks.landmark

        match exercicio:
            case "rosca_direta_halter_uni":
                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                angulo = calcularAngulo(shoulder, elbow, wrist)
                return {"angulo": round(angulo, 2), "msg": "OK"}
            
            # Você pode adicionar outros casos como "meio_agachamento" etc.

    return {"msg": "Erro na análise"}
