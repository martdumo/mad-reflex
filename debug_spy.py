import sys
import os

print("--- REPORTE FORENSE ---")
print(f"1. Ejecutable de Python: {sys.executable}")
print(f"2. Versión: {sys.version}")

try:
    import mediapipe
    print(f"3. Ubicación del archivo mediapipe: {mediapipe.__file__}")
    
    # Esto es crucial: ¿Es una carpeta o un archivo suelto?
    if os.path.isdir(os.path.dirname(mediapipe.__file__)):
         print("4. Tipo: Paquete instalado (Carpeta) ✅")
    else:
         print("4. Tipo: Archivo suelto (POSIBLE CONFLICTO) ❌")

except ImportError as e:
    print(f"❌ Falló el import básico: {e}")

print("\n--- INTENTO DE ACCESO QUIRÚRGICO ---")
# Vamos a saltarnos el "import mediapipe" general e ir directo al archivo que da error
try:
    from mediapipe.python import solutions
    print("✅ Acceso directo a 'mediapipe.python.solutions' EXITOSO.")
except Exception as e:
    print(f"❌ Acceso directo FALLÓ con error detallado:\n{e}")

print("\n--- VERIFICANDO PROTOCÓLOS (Protobuf) ---")
try:
    import google.protobuf
    print(f"Protobuf Version: {google.protobuf.__version__}")
    print(f"File: {google.protobuf.__file__}")
except Exception as e:
    print(f"❌ Error Protobuf: {e}")