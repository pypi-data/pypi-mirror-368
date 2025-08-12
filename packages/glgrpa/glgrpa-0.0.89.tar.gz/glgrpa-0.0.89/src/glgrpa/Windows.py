# src/Windows/Windows.py

import os
import platform
from datetime import datetime
import time
from .Terminal import Terminal

class Windows(Terminal):
    def __init__(self, dev: bool = False):
        super().__init__(dev=dev)
        # Determinar la carpeta de descargas personalizada según el sistema operativo
        if platform.system() == "Windows":
            self.carpeta_descargas_personalizada = os.path.join(os.environ.get("USERPROFILE", ""), "DescargaPersonalizada")
        else:
            self.carpeta_descargas_personalizada = os.path.join(os.environ.get("HOME", ""), "DescargaPersonalizada")
        
        # Crear la carpeta si no existe
        if not os.path.exists(self.carpeta_descargas_personalizada):
            os.makedirs(self.carpeta_descargas_personalizada, exist_ok=True)
        
        # Purga inicial de la carpeta
        self.purgar_carpeta_descargas_personalizada()
        
    def purgar_carpeta_descargas_personalizada(self):
        """ Purga la carpeta de descargas """
        
        # Obtener los archivos de la carpeta de descargas 
        archivos = [f for f in os.listdir(self.carpeta_descargas_personalizada)]
        
        # Eliminar los archivos
        for archivo in archivos:
            os.remove(os.path.join(self.carpeta_descargas_personalizada, archivo))

    def crear_carpeta_si_no_existe(self, carpeta: str) -> bool:
        """ Crea la carpeta de descargas si no existe """
        try:
            if not os.path.exists(carpeta):
                os.makedirs(carpeta)
            
            return True
        except Exception as e:
            return False
        
    def buscar_ultimo_archivo(self, ruta:str, extension: str) -> str:
        """ Busca el último archivo de una extensión específica en la carpeta de descargas """
        
        # Obtener los archivos de la carpeta de descargas
        archivos = [f for f in os.listdir(ruta) if f.endswith(extension)]
        
        # Si no se encontraron archivos, se lanza una excepción
        if not archivos:
            raise FileNotFoundError(f"No se encontraron archivos {extension} en la carpeta de descargas.")
        
        # Ordenar los archivos por fecha de modificación
        archivos.sort(key=lambda f: os.path.getmtime(os.path.join(ruta, f)), reverse=True)
        return os.path.join(ruta, archivos[0])
        
    def mover_archivo(self, ruta_archivo: str, ruta_destino: str) -> str| bool:
        """ Mueve un archivo a una carpeta destino """

        self.mostrar(f"Moviendo archivo {ruta_archivo} a {ruta_destino}")
        
        # Crear las carpetas si no existen
        if not self.crear_carpeta_si_no_existe(ruta_destino):
            self.mostrar(f"No se pudo crear la carpeta {ruta_destino}", True)
            return False

        # Obtener el nombre del archivo
        nombre_archivo = os.path.basename(ruta_archivo)
        nueva_ruta = os.path.join(ruta_destino, nombre_archivo)
        time.sleep(3)
        
        # Verificar si el archivo ya existe en la carpeta destino
        if os.path.exists(nueva_ruta):
            self.mostrar(f"El archivo {nombre_archivo} ya existe en la carpeta {ruta_destino}", True)
            return nueva_ruta
        
        # Mover el archivo
        try:
            os.rename(ruta_archivo, nueva_ruta)
        except Exception as e:
            self.mostrar(f"No se pudo mover el archivo {ruta_archivo} a la carpeta {ruta_destino}", True)
            self.mostrar(f"Error: {e}", True)
            return False
            
        return nueva_ruta
    
    def armar_estructura_de_carpetas(self, ruta: str) -> str| bool:
        r""" Arma la estructura de carpetas en la ruta indicada [ruta\anio\mes\dia]. Devuelve la ruta destino """
        try:
            # Obtener la fecha actual
            fecha_actual = datetime.now()
            anio = fecha_actual.strftime("%Y")
            mes = fecha_actual.strftime("%m")
            dia = fecha_actual.strftime("%d")
            
            # Crear la estructura de carpetas
            ruta_destino = os.path.join(ruta, anio, mes, dia)
            
            return ruta_destino
        except Exception as e:
            self.mostrar(f"No se pudo crear la estructura de carpetas en la ruta {ruta}")
            return False
        
    def copiar_al_portapapeles(self, texto: str) -> bool:
        """ Copia el texto al portapapeles """
        try:
            import pyperclip
            pyperclip.copy(texto)
            self.mostrar(f"📃 Texto copiado al portapapeles:\n{texto}")
            return True
        except ImportError:
            self.mostrar("❌ No se pudo importar la librería 'pyperclip'. Asegúrate de tenerla instalada.", True)
            return False
        except Exception as e:
            self.mostrar(f"❌ Error desconocido al copiar al portapapeles: {e}", True)
            return False
    
    def tomar_screenshot(self, nombre_archivo: str | None = None) -> str:
        """ Toma un screenshot de la pantalla completa y lo guarda en la carpeta logs """
        try:
            import pyautogui
            
            # Generar nombre del archivo si no se proporciona
            if not nombre_archivo:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nombre_archivo = f"screenshot_{timestamp}.png"
            
            # Asegurar que tenga extensión .png
            if not nombre_archivo.endswith('.png'):
                nombre_archivo += '.png'
            
            # Crear ruta en carpeta logs
            carpeta_logs = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
            if not os.path.exists(carpeta_logs):
                os.makedirs(carpeta_logs, exist_ok=True)
            
            ruta_screenshot = os.path.join(carpeta_logs, nombre_archivo)
            
            # Tomar screenshot
            screenshot = pyautogui.screenshot()
            screenshot.save(ruta_screenshot)
            
            self.mostrar(f"📸 Screenshot guardado en: {ruta_screenshot}")
            return ruta_screenshot
            
        except ImportError as e:
            if "pyscreeze" in str(e) or "Pillow" in str(e):
                self.mostrar("⚠️ Screenshot no disponible: falta dependencia Pillow/pyscreeze", True)
                self.mostrar("💡 Para habilitar screenshots, instalar: pip install Pillow", True)
            else:
                self.mostrar(f"❌ No se pudo importar pyautogui: {e}", True)
            return ""
        except Exception as e:
            if "pyscreeze" in str(e) or "Pillow" in str(e):
                self.mostrar("⚠️ Screenshot fallido: Pillow no compatible con esta versión de Python", True)
                self.mostrar("💡 Instalar versión compatible: pip install Pillow==9.5.0", True)
            else:
                self.mostrar(f"❌ Error al tomar screenshot: {e}", True)
            return ""