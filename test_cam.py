import cv2

def test_camera():
    # Intenta abrir la cámara por defecto (índice 0)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Error: No se pudo acceder a la cámara.")
        return

    print("✅ Cámara detectada. Presiona 'q' para salir.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Error al leer el frame.")
            break

        # Mostrar la imagen en una ventana nativa de Windows
        cv2.imshow('Test Camara - MAD REFLEX', frame)

        # Salir si se presiona 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_camera()