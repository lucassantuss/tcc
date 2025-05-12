import cv2
import mediapipe as mp
import numpy as np
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# VIDEO FEED
# Ativa um dispositivo de vídeo conectado ao PC por parâmetro, 0 = webcam
cap = cv2.VideoCapture(0)

# Variáveis do contador de flexão bíceps
counter = 0
stage = None

# Calculo dos vetores para achar os angulos
def calcularAngulo(a, b, c):
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = np.array(c) # End

    # Fórmula da subtração dos vetores em X e Y, utilizando arcotangente
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angulo = np.abs(radians*180.0/np.pi)

    if angulo > 180.0:
        angulo = 360-angulo

    return angulo

def valorPoseLandmark(membro_enum):
    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        return [landmarks[membro_enum.value].x, landmarks[membro_enum.value].y]
    return [0, 0]  # ou levante uma exceção, dependendo do que quiser

def analisarExercicio(imagem, exercicio):
    global counter, stage 
    # Extrai os pontos de referência
    try:
        landmarks = results.pose_landmarks.landmark # Coordenadas de fato

        match exercicio:
            case "rosca_direta_halter_uni":
                # Exemplo para pegar dados de um ponto específico
                shoulder = valorPoseLandmark(mp_pose.PoseLandmark.LEFT_SHOULDER)
                elbow    = valorPoseLandmark(mp_pose.PoseLandmark.LEFT_ELBOW)
                wrist    = valorPoseLandmark(mp_pose.PoseLandmark.LEFT_WRIST)

                # Calcula angulo
                angulo = calcularAngulo(shoulder, elbow, wrist)

                # Visualiza ângulo
                # Parâmetros:
                # imagem que estamos trabalhando,
                # o angulo em string,
                # chama a multiplicação de vetores da tuplica entre o ponto de ref do cotovelo e as dimensões da webcam - precisa ser um túplica do tipo int
                # Configs de Fonte: tipo, tamanho, cor, grossura de linha e tipo de linha
                cv2.putText(imagem, str(angulo), tuple(np.multiply(elbow, [640, 480]).astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            
                # Contador de flexão do bíceps
                if angulo > 160:
                    stage = "down"
                if angulo < 34 and stage == "down":
                    stage = "up"
                    counter += 1
                    print(counter)
            
            case "supino_reto_banco":
                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                angulo = calcularAngulo(shoulder, elbow, wrist)

                cv2.putText(imagem, str(angulo), tuple(np.multiply(elbow, [640, 480]).astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            
                if angulo > 160:
                    stage = "down"
                if angulo < 34 and stage == "down":
                    stage = "up"
                    counter += 1
                    print(counter)

            case "cadeira_flexora":
                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                angulo = calcularAngulo(shoulder, elbow, wrist)

                cv2.putText(imagem, str(angulo), tuple(np.multiply(elbow, [640, 480]).astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            
                if angulo > 160:
                    stage = "down"
                if angulo < 34 and stage == "down":
                    stage = "up"
                    counter += 1
                    print(counter)

            case "meio_agachamento":
                l_hip = valorPoseLandmark(mp_pose.PoseLandmark.LEFT_HIP)
                l_knee = valorPoseLandmark(mp_pose.PoseLandmark.LEFT_KNEE)
                l_ankle = valorPoseLandmark(mp_pose.PoseLandmark.LEFT_ANKLE)

                r_hip = valorPoseLandmark(mp_pose.PoseLandmark.RIGHT_HIP)
                r_knee = valorPoseLandmark(mp_pose.PoseLandmark.RIGHT_KNEE)
                r_ankle = valorPoseLandmark(mp_pose.PoseLandmark.RIGHT_ANKLE)

                l_angle = calcularAngulo(l_hip, l_knee, l_ankle)
                r_angle = calcularAngulo(r_hip, r_knee, r_ankle)

                cv2.putText(imagem, str(l_angle), tuple(np.multiply(l_knee, [640, 480]).astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.putText(imagem, str(r_angle), tuple(np.multiply(r_knee, [640, 480]).astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            
                if l_angle >= 170 and r_angle >= 170:
                    stage = "up"
                if (l_angle <= 100 and r_angle <= 100) and stage == "up":
                    stage = "down"
                    counter += 1
                    print(counter)
            
            case _:
                print("Exercício não reconhecido")
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
    cv2.rectangle(imagem, (0,0), (225, 73), (245, 117, 16), -1)

    # Rep data
    cv2.putText(imagem, 'REPS', (15, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(imagem, str(counter), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

    # Stage Data
    cv2.putText(imagem, 'STAGE', (65, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(imagem, stage, (60, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

    # Variaveis para mudar config cor e tamanho - dspec = drawing specifications
    landmark_dspec = mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2)
    connection_dspec = mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)

    # Renderiza detecções - traça o esqueleto e sobrepõe na imagem
    mp_drawing.draw_landmarks(imagem, results.pose_landmarks, mp_pose.POSE_CONNECTIONS, landmark_dspec, connection_dspec)

## Setup mediapipe instance
# Ativa a EPH e por parâmetro (qualidade minima de detecção e tracking - maior melhor - em %)
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
# Enquanto tiver rodando, mantém o while de pé
    while cap.isOpened():
        # ret = return - ainda não usado
        # frame = quadros captados
        ret, frame = cap.read()

        # Mudar a cor da imagem, a camera vem na ordenação BGR, o MediaPipe só entende RGB
        imagem = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Economiza memória
        imagem.flags.writeable = False

        # Detecta iamgem
        results = pose.process(imagem)

        # Volta as cores para BGR
        imagem.flags.writeable = True
        imagem = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        ex1 = "rosca_direta_halter_uni"
        ex2 = "meio_agachamento"
        analisarExercicio(imagem, ex1)

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
        cv2.imshow('APE', imagem)

        # print(f'Angulo: {calculateAngle(shoulder, elbow, wrist)}')

        # Quebra o loop caso alguma tecla seja pressionada e ela seja o 'Q'
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    # Desliga a webcam e fecha as janelas
    cap.release()
    cv2.destroyAllWindows()