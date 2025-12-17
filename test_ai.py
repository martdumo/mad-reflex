
import sys
print(f"🐍 Python Version: {sys.version}")

try:
    import mediapipe as mp
    print("✅ Librería MediaPipe importada.")
    
    # Esta es la línea que fallaba antes
    mp_hands = mp.solutions.hands
    print("✅ Módulo 'solutions.hands' encontrado.")
    
    hands = mp_hands.Hands()
    print("✅ Modelo de Manos inicializado correctamente.")
    
except ImportError as e:
    print(f"❌ Error de Importación: {e}")
except AttributeError as e:
    print(f"❌ Error de Atributo (El problema persistente): {e}")
except Exception as e:
    print(f"❌ Otro error inesperado: {e}")