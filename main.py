import customtkinter as ctk
import cv2
import pyautogui
import numpy as np # Necesitaremos numpy para interpolación (instalar si falla: pip install numpy)
import time
from modules.hand_tracker import HandDetector

# --- CONFIGURACIÓN MAESTRA ---
W_CAM, H_CAM = 640, 480      # Resolución Cámara
FRAME_R = 100                # Reducción de marco (Deadzone exterior) -> Mayor = menos movimiento de mano necesario
MOUSE_SMOOTH = 5             # Suavizado del Mouse (mayor = más lento/suave)
SCROLL_SMOOTH = 10           # Suavizado del Scroll
CLICK_COOLDOWN = 0.5         # Segundos entre clicks para no spammear

pyautogui.FAILSAFE = False   # ¡CUIDADO! Permite llevar el mouse a las esquinas sin crashear

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MAD-REFLEX: AI Mouse & Scroll 🖱️")
        self.geometry("520x400")
        
        # UI
        self.status_label = ctk.CTkLabel(self, text="INICIANDO...", font=("Consolas", 24, "bold"))
        self.status_label.pack(pady=10)
        self.mode_label = ctk.CTkLabel(self, text="☝️ INDICE: Mover Mouse\n✌️ PAZ: Click Izquierdo\n👆👍 L: Click Derecho\n🖐️ MANO: Scroll Mode", font=("Arial", 14))
        self.mode_label.pack(pady=5)
        
        self.btn_quit = ctk.CTkButton(self, text="Salir", command=self.on_closing, fg_color="#AA0000")
        self.btn_quit.pack(pady=20)

        # Inicialización
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, W_CAM)
        self.cap.set(4, H_CAM)
        
        self.detector = HandDetector(max_hands=1)
        self.w_scr, self.h_scr = pyautogui.size() # Tamaño real de tu monitor
        
        # Variables de estado (Suavizado)
        self.plocX, self.plocY = 0, 0 # Previous Location
        self.clocX, self.clocY = 0, 0 # Current Location
        
        self.prev_scroll_y = 0
        self.curr_scroll_y = 0
        
        self.last_click_time = 0
        self.dragging = False

        self.update_system()

    def update_system(self):
        ret, frame = self.cap.read()
        if ret:
            # Espejo y buscar manos
            frame = cv2.flip(frame, 1)
            frame = self.detector.find_hands(frame, draw=True) # Dibujamos para guiarte mejor
            lm_list = self.detector.find_positions(frame)

            # Dibujar el Cuadro de Control (Todo lo que hagas debe ser dentro de este cuadro)
            cv2.rectangle(frame, (FRAME_R, FRAME_R), (W_CAM - FRAME_R, H_CAM - FRAME_R), (255, 0, 255), 2)

            if len(lm_list) != 0:
                # Dedo Índice (Punta)
                x1, y1 = lm_list[8][1:]
                # Dedo Medio (Punta)
                x2, y2 = lm_list[12][1:]
                
                # Checkear dedos levantados [Pulgar, Indice, Medio, Anular, Meñique]
                fingers = self.detector.fingers_up(lm_list)
                
                # --- LÓGICA DE ESTADOS ---

                # 1. MODO SCROLL (5 Dedos o 4 dedos abiertos) - Prioridad alta para que no mueva el mouse
                if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1:
                    # Scroll Lógica mejorada (Suavizado tipo App)
                    curr_y = lm_list[12][2] # Usamos dedo medio
                    
                    if self.prev_scroll_y == 0: self.prev_scroll_y = curr_y
                    
                    # Interp
                    self.curr_scroll_y = self.prev_scroll_y + (curr_y - self.prev_scroll_y) / (SCROLL_SMOOTH / 2) # Más responsivo
                    delta = self.curr_scroll_y - self.prev_scroll_y
                    
                    if abs(delta) > 2: # Pequeño deadzone
                        # Multiplicador
                        amount = delta * 8 
                        # Invertido: Mano Baja -> Pagina Sube
                        if amount > 0: pyautogui.scroll(int(amount))
                        else: pyautogui.scroll(int(amount))
                        
                        # Estado UI
                        self.status_label.configure(text="🖐️ SCROLLING", text_color="#FFD700")
                    
                    self.prev_scroll_y = self.curr_scroll_y
                    # Congelamos posición del mouse para que no salte al volver a modo mouse
                    self.plocX, self.plocY = pyautogui.position() 

                # 2. MODO MOVIMIENTO (Solo Índice Arriba) ☝️
                # Aceptamos [0,1,0,0,0] o [1,1,0,0,0] si el pulgar se confunde, 
                # pero idealmente [0,1,0,0,0]
                elif fingers[1] == 1 and fingers[2] == 0:
                    
                    # Convertir Coordenadas: Webcam -> Pantalla
                    # Usamos numpy interp para mapear el cuadro pequeño a la pantalla completa
                    x3 = np.interp(x1, (FRAME_R, W_CAM - FRAME_R), (0, self.w_scr))
                    y3 = np.interp(y1, (FRAME_R, H_CAM - FRAME_R), (0, self.h_scr))
                    
                    # Suavizar valor (Smoothening)
                    self.clocX = self.plocX + (x3 - self.plocX) / MOUSE_SMOOTH
                    self.clocY = self.plocY + (y3 - self.plocY) / MOUSE_SMOOTH
                    
                    # Mover Mouse
                    pyautogui.moveTo(self.clocX, self.clocY)
                    
                    # Actualizar previo
                    self.plocX, self.plocY = self.clocX, self.clocY
                    self.prev_scroll_y = 0 # Reset scroll
                    
                    self.status_label.configure(text="🖱️ MOVING MOUSE", text_color="#00FFFF")

                # 3. CLICK IZQUIERDO (Paz ✌️: Índice y Medio)
                elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0:
                    # Distancia entre dedos (para asegurar que es intencional)
                    # Si estan muy separados, no hacemos click. Si se juntan -> click?
                    # Por simplicidad, el gesto detectado es suficiente:
                    
                    current_time = time.time()
                    if (current_time - self.last_click_time) > CLICK_COOLDOWN:
                        self.status_label.configure(text="✅ LEFT CLICK", text_color="#00FF00")
                        pyautogui.click()
                        self.last_click_time = current_time

                # 4. CLICK DERECHO (L 👆👍: Pulgar e Indice)
                elif fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 0:
                     current_time = time.time()
                     if (current_time - self.last_click_time) > CLICK_COOLDOWN:
                        self.status_label.configure(text="🔘 RIGHT CLICK", text_color="orange")
                        pyautogui.rightClick()
                        self.last_click_time = current_time

                else:
                    self.status_label.configure(text="💤 IDLE", text_color="gray")
                    self.prev_scroll_y = 0

            # UI Update en Video (opcional para debug)
            # cv2.imshow("Hand Cam", frame)
            
        self.after(10, self.update_system)

    def on_closing(self):
        self.cap.release()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()