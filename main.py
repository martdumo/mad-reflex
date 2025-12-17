import customtkinter as ctk
import cv2
from PIL import Image, ImageTk

# Configuración de UI
ctk.set_appearance_mode("Dark")  # Full modo oscuro
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MAD-REFLEX v0.1")
        self.geometry("800x600")

        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Label para la cámara
        self.camera_label = ctk.CTkLabel(self, text="Iniciando Cámara...")
        self.camera_label.grid(row=0, column=0, padx=20, pady=20)

        # Botón de salida
        self.btn_quit = ctk.CTkButton(self, text="Salir", command=self.on_closing)
        self.btn_quit.grid(row=1, column=0, pady=20)

        # Inicializar OpenCV
        self.cap = cv2.VideoCapture(0)
        
        self.update_camera()

    def update_camera(self):
        ret, frame = self.cap.read()
        if ret:
            # Convertir color de BGR (OpenCV) a RGB (Tkinter/Pillow)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Voltear horizontalmente (Efecto Espejo)
            frame_rgb = cv2.flip(frame_rgb, 1)
            
            # Convertir a imagen compatible con CTk
            img = Image.fromarray(frame_rgb)
            img_tk = ctk.CTkImage(light_image=img, dark_image=img, size=(640, 480))
            
            self.camera_label.configure(image=img_tk, text="")
        
        # Llamarse a sí mismo cada 10ms
        self.after(10, self.update_camera)

    def on_closing(self):
        self.cap.release()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()