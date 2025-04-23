import cv2
import mediapipe as mp
import numpy as np
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Calculo dos vetores para achar os angulos
def calculateAngle(a, b, c):
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = np.array(c) # End

    # Fórmula da subtração dos vetores em X e Y, utilizando arcotangente
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)

    if angle > 180.0:
        angle = 360-angle

    return angle

# VIDEO FEED
# Ativa um dispositivo de vídeo conectado ao PC por parâmetro, 0 = webcam
cap = cv2.VideoCapture(0)

# Variáveis do contador de flexão bíceps
counter = 0
stage = None

## Setup mediapipe instance
# Ativa a EPH e por parâmetro (qualidade minima de detecção e tracking - maior melhor - em %)
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
# Enquanto tiver rodando, mantém o while de pé
    while cap.isOpened():
        # ret = return - ainda não usado
        # frame = quadros captados
        ret, frame = cap.read()

        # Mudar a cor da imagem, a camera vem na ordenação BGR, o MediaPipe só entende RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Economiza memória
        image.flags.writeable = False

        # Detecta iamgem
        results = pose.process(image)

        # Volta as cores para BGR
        image.flags.writeable = True
        image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Extrai os pontos de referência
        try:
            landmarks = results.pose_landmarks.landmark # Coordenadas de fato

            # Exemplo para pegar dados de um ponto específico
            shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

            # Calcula angulo
            angle = calculateAngle(shoulder, elbow, wrist)

            # Visualiza ângulo
            # Parâmetros:
            # imagem que estamos trabalhando,
            # o angulo em string,
            # chama a multiplicação de vetores da tuplica entre o ponto de ref do cotovelo e as dimensões da webcam - precisa ser um túplica do tipo int
            # Configs de Fonte: tipo, tamanho, cor, grossura de linha e tipo de linha
            cv2.putText(image, str(angle), tuple(np.multiply(elbow, [640, 480]).astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        
            # Contador de flexão do bíceps
            if angle > 160:
                stage = "down"
            if angle < 34 and stage == "down":
                stage = "up"
                counter += 1
                print(counter)
        except:
            pass

        # Renderiza o contador de flexão
        # Seta caixa de status
        # Parâmetros: 
        # Onde vamos aplicar o desenho
        # Coordenadas
        # Tamanho do retangulo
        # Cores do retangulo
        # Tamanho da linha (-1 preenche ao ret inteiro)
        cv2.rectangle(image, (0,0), (225, 73), (245, 117, 16), -1)

        # Rep data
        cv2.putText(image, 'REPS', (15, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(image, str(counter), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

        # Stage Data
        cv2.putText(image, 'STAGE', (65, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(image, stage, (60, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

        # Variaveis para mudar config cor e tamanho - dspec = drawing specifications
        landmark_dspec = mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2)
        connection_dspec = mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)

        # Renderiza detecções - traça o esqueleto e sobrepõe na imagem
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS, landmark_dspec, connection_dspec)

        # Printa os pontos e seus dados + a conexão de cada ponto
        # print(landmarks)
        # print(mp_pose.POSE_CONNECTIONS)
        # Itera pelo vetor que contém o mapa de todos os 33 pontos - len: 0-32
        # for lndmark in mp_pose.PoseLandmark:
            # print (lndmark)

        # print(f'Ombro esquerdo:  ' + str(shoulder))
        # print(f'Cotovelo esquerdo: ' + str(elbow))
        # print(f'Punho esquerdo: ' + str(wrist))

        # Abre um popup e por parâmetro (título, frame captado da webcam)
        cv2.imshow('MediaPipe Feed', image)

        # print(f'Angulo: {calculateAngle(shoulder, elbow, wrist)}')

        # Quebra o loop caso alguma tecla seja pressionada e ela seja o 'Q'
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    # Desliga a webcam e fecha as janelas
    cap.release()
    cv2.destroyAllWindows()