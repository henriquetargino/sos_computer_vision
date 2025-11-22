# cv
import cv2
import mediapipe as mp

# matematica
import numpy as np
import math

# requests e threading
import requests
import threading
import time


# definindo as cores em BGR
COR_NORMAL = (0, 255, 0)
COR_ALERTA = (0, 165, 255)
COR_PERIGO = (0, 0, 255)
COR_BARRA_FUNDO = (50, 50, 50)

class HandDetector():
    def __init__(self, mode=False, max_hands=2, detection_con=0.7, track_con=0.5):
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con
        
        # inicializa o mediapipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(self.mode, self.max_hands, 1, 
                                         self.detection_con, self.track_con)
        self.mp_draw = mp.solutions.drawing_utils
        self.tip_ids = [4, 8, 12, 16, 20]

    def find_hands(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        
        if self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                if draw:
                    # desenha os pontos na mao
                    self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
        return img

    def find_position(self, img, hand_no=0):
        self.lm_list = []
        if self.results.multi_hand_landmarks:
            if hand_no < len(self.results.multi_hand_landmarks):
                my_hand = self.results.multi_hand_landmarks[hand_no]
                for id, lm in enumerate(my_hand.landmark):
                    h, w, c = img.shape
                    # converte pra pixel
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    self.lm_list.append([id, cx, cy])
        return self.lm_list

    def fingers_up(self):
        if not self.lm_list: return []
        fingers = []
        
        # dedao (eixo x)
        if self.lm_list[self.tip_ids[0]][1] < self.lm_list[self.tip_ids[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # 4 dedos (eixo y)
        for id in range(1, 5):
            if self.lm_list[self.tip_ids[id]][2] < self.lm_list[self.tip_ids[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers

def calcular_distancia(p1, p2):
    # calcula a hipotenusa (distancia) entre dois pontos
    x1, y1 = p1
    x2, y2 = p2
    return math.hypot(x2 - x1, y2 - y1)

def webhook_socorro():
    url = "https://n8n-n8n.8cn8wt.easypanel.host/webhook-test/visao-computacional"
    try:
        requests.post(url, json={"evento": "SINAL_SOCORRO", "msg": "ALERTA: Gesto de ajuda detectado na câmera!", "nivel": "CRITICO"})
        print("🚨 [THREAD] WEBHOOK ATIVADO COM SUCESSO!")
    except Exception as e:
        print(f"❌ [THREAD] Erro: {e}")

def main():
    # abre a webcam
    cap = cv2.VideoCapture(1)
    cap.set(3, 1280)
    cap.set(4, 720)
    
    detector = HandDetector(max_hands=2, detection_con=0.75)

    # variaveis de controle de estado
    estagio_sinal = 0 
    tempo_inicio_sinal = 0
    tempo_ultimo_frame_armado = 0

    # configs de tempo
    TEMPO_LIMITE_SEQUENCIA = 2.0
    TOLERANCIA_DESARME = 0.5
    TEMPO_DISPLAY_SUCESSO = 4.0  
    
    ultimo_disparo = 0
    fator_distancia_dedos = 0.40

    print("--- SISTEMA DE SEGURANÇA INICIADO ---")

    while True:
        success, img = cap.read()
        if not success: break
        # inverte a camera
        img = cv2.flip(img, 1)

        img = detector.find_hands(img, draw=True)
        
        num_maos = 0
        if detector.results.multi_hand_landmarks:
            num_maos = len(detector.results.multi_hand_landmarks)

        detectou_sinal_neste_frame = False

        # loop pra cada mao encontrada
        for i in range(num_maos):
            lm = detector.find_position(img, hand_no=i)
            if len(lm) == 0: continue

            # printa a coordenada da base do mindinho no terminal
            print([lm[17][1]], [lm[17][2]])

            fingers = detector.fingers_up()
            
            # pegando pontos importantes da mao
            p_dedao = lm[4][1:]
            p_indicador = lm[8][1:]
            p_medio = lm[12][1:]
            p_base_mind = lm[17][1:]
            p_base_ind = lm[5][1:]

            largura_palma = calcular_distancia(p_base_ind, p_base_mind)
            
            # regras de deteccao
            quatro_dedos_up = (fingers[1]==1 and fingers[2]==1 and fingers[3]==1 and fingers[4]==1)
            
            # verifica se os dedos estao juntos
            dist_dedos = calcular_distancia(p_indicador, p_medio)
            dedos_juntos = dist_dedos < (largura_palma * fator_distancia_dedos)

            # verifica se o dedao ta pra dentro
            dist_dedao_mindinho = calcular_distancia(p_dedao, p_base_mind)
            dedao_dobrado = dist_dedao_mindinho < (largura_palma * 0.9)

            punho_fechado = (fingers == [0, 0, 0, 0, 0])
            
            # maquina de estados
            
            # estagio 1: armar (possivel sinal)
            if quatro_dedos_up and dedos_juntos and dedao_dobrado:
                estagio_sinal = 1
                if tempo_inicio_sinal == 0: tempo_inicio_sinal = time.time() 
                tempo_ultimo_frame_armado = time.time() 
                detectou_sinal_neste_frame = True
                
                # desenha a linha laranja
                cv2.line(img, p_dedao, p_base_mind, COR_ALERTA, 3)

                # bounding box (caixa de foco)
                lista_x = [c[1] for c in lm]
                lista_y = [c[2] for c in lm]
                x_min, x_max = min(lista_x), max(lista_x)
                y_min, y_max = min(lista_y), max(lista_y)
                # desenha o quadrado em volta da mao
                cv2.rectangle(img, (x_min-20, y_min-20), (x_max+20, y_max+20), COR_ALERTA, 3)

            # estagio 2: disparar (socorro)
            elif estagio_sinal == 1 and punho_fechado:
                tempo_atual = time.time()
                if (tempo_atual - tempo_inicio_sinal) < TEMPO_LIMITE_SEQUENCIA:
                    if (tempo_atual - ultimo_disparo) > TEMPO_DISPLAY_SUCESSO:
                        # dispara a thread do webhook
                        threading.Thread(target=webhook_socorro).start()
                        ultimo_disparo = tempo_atual
                    
                    estagio_sinal = 0 
                    tempo_inicio_sinal = 0 
                    detectou_sinal_neste_frame = True
                else:
                    estagio_sinal = 0
                    tempo_inicio_sinal = 0

        # reseta se perder o sinal por muito tempo
        if estagio_sinal == 1 and not detectou_sinal_neste_frame:
            if (time.time() - tempo_ultimo_frame_armado) > TOLERANCIA_DESARME:
                estagio_sinal = 0
                tempo_inicio_sinal = 0
        
        # ui e flash de tela
        tempo_desde_disparo = time.time() - ultimo_disparo
        altura, largura, _ = img.shape
        
        if tempo_desde_disparo < TEMPO_DISPLAY_SUCESSO:
            texto_tela = "SINAL DE SOCORRO ENVIADO"
            cor_tela = COR_PERIGO
            
            # barra de progresso
            pct_restante = 1 - (tempo_desde_disparo / TEMPO_DISPLAY_SUCESSO)
            largura_barra = int(largura * pct_restante)
            cv2.rectangle(img, (0, altura-40), (largura, altura), COR_BARRA_FUNDO, cv2.FILLED)
            cv2.rectangle(img, (0, altura-40), (largura_barra, altura), COR_PERIGO, cv2.FILLED)

            # flash de tela piscando
            if (time.time() % 1.0) < 0.5:
                cv2.rectangle(img, (0, 0), (largura, altura), COR_PERIGO, 30)
            
        elif estagio_sinal == 1:
            texto_tela = "Possivel Sinal..."
            cor_tela = COR_ALERTA
        else:
            texto_tela = "Normal"
            cor_tela = COR_NORMAL

        # desenha o texto na tela
        cv2.rectangle(img, (0, 0), (1280, 60), (0, 0, 0), -1)
        cv2.putText(img, texto_tela, (50, 45), cv2.FONT_HERSHEY_SIMPLEX, 1.2, cor_tela, 3)

        cv2.imshow("Signal for Help - Portfolio Henrique", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()