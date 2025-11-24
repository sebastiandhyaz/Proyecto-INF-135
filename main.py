import os
import sys
import subprocess

def main():
    # Comando para ejecutar Streamlit con la configuración correcta para Codespaces
    cmd = [
        sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
        "--server.address=0.0.0.0",
        "--server.port=8501"
    ]
    
    print("🚀 Iniciando Simulador de SO...")
    print("👉 Espera a que cargue y abre el link que aparecerá abajo...")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n🛑 Simulador detenido.")

if __name__ == "__main__":
    main()
