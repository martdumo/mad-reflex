import cv2
import mediapipe as mp

class HandDetector:
    def __init__(self, mode=False, max_hands=1, complexity=1, detection_con=0.7, track_con=0.5):
        self.mode = mode
        self.max_hands = max_hands
        self.complexity = complexity
        self.detection_con = detection_con
        self.track_con = track_con

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            model_complexity=self.complexity,
            min_detection_confidence=self.detection_con,
            min_tracking_confidence=self.track_con
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.tip_ids = [4, 8, 12, 16, 20] # Pulgar, Indice, Medio, Anular, Meñique
        self.results = None

    def find_hands(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        if self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
        return img

    def find_positions(self, img, hand_no=0):
        lm_list = []
        if self.results.multi_hand_landmarks:
            if len(self.results.multi_hand_landmarks) > hand_no:
                my_hand = self.results.multi_hand_landmarks[hand_no]
                h, w, c = img.shape
                for id, lm in enumerate(my_hand.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append([id, cx, cy])
        return lm_list

    def fingers_up(self, lm_list):
        """
        Devuelve lista [Pulgar, Indice, Medio, Anular, Meñique] con 1 o 0.
        Ej: Paz (Indice+Medio) -> [0, 1, 1, 0, 0]
        Ej: L (Pulgar+Indice)  -> [1, 1, 0, 0, 0]
        """
        fingers = []
        
        # --- PULGAR (Eje X) ---
        # Comparamos si la punta (4) está a la derecha o izquierda del nudillo (3)
        # Esto depende de si es mano izquierda o derecha, asumiremos Derecha para simplificar.
        # Si usas mano izquierda, el pulgar funcionará al revés.
        if lm_list[self.tip_ids[0]][1] < lm_list[self.tip_ids[0] - 1][1]: 
             # Nota: Como espejamos la cámara, la lógica "<" suele funcionar para "abierto" en mano derecha
             fingers.append(1)
        else:
             fingers.append(0)

        # --- OTROS 4 DEDOS (Eje Y) ---
        for id in range(1, 5):
            if lm_list[self.tip_ids[id]][2] < lm_list[self.tip_ids[id] - 2][2]:
                fingers.append(1) # Dedo Arriba
            else:
                fingers.append(0) # Dedo Abajo

        return fingers