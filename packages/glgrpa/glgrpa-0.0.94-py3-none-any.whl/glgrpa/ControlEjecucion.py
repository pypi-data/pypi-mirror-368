# src/glgrpa/ControlEjecucion.py

import json
import os
import inspect
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from functools import wraps
from .Windows import Windows
from .Terminal import Terminal
from .Email import Email

class ControlEjecucion(Windows, Terminal):
    """
    Clase para el control de estado y reintentos de ejecución siguiendo el patrón
    de herencia múltiple de glgrpa. Proporciona funcionalidad para:
    - Gestión de estado de ejecución con archivo JSON
    - Control de reintentos automáticos
    - Notificaciones por email en caso de éxito/fallo
    - Logging detallado con emojis siguiendo las convenciones del proyecto
    """
    
    def __init__(self, 
                 intentos_maximos: int = 3,
                 permitir_multiples_ejecuciones_diarias: bool = False,
                 dev: bool = False,
                 email_destinatarios: Optional[list] = None,
                 nombre_script: Optional[str] = None,
                 # Parámetros SMTP para Email
                 smtp_server: Optional[str] = None,
                 smtp_port: Optional[int] = None,
                 smtp_username: Optional[str] = None,
                 smtp_password: Optional[str] = None,
                 nombre_trabajador_virtual: Optional[str] = None,
                 nombre_aprendizaje: Optional[str] = None):
        """
        Inicializa el control de ejecución.
        
        :param intentos_maximos: Número máximo de reintentos por ejecución (default: 3)
        :param permitir_multiples_ejecuciones_diarias: Si permite múltiples ejecuciones por día
        :param dev: Modo desarrollo (delays más cortos, logging verboso)
        :param email_destinatarios: Lista de emails para notificaciones
        :param nombre_script: Nombre del script para logs y emails (se detecta automáticamente si no se especifica)
        :param smtp_server: Servidor SMTP para envío de emails
        :param smtp_port: Puerto SMTP
        :param smtp_username: Usuario SMTP
        :param smtp_password: Contraseña SMTP
        :param nombre_trabajador_virtual: Nombre del trabajador virtual para emails
        :param nombre_aprendizaje: Nombre del aprendizaje para emails
        """
        super().__init__(dev=dev)
        
        self.intentos_maximos = intentos_maximos
        self.permitir_multiples_ejecuciones_diarias = permitir_multiples_ejecuciones_diarias
        self.email_destinatarios = email_destinatarios or []
        
        # Detectar nombre del script automáticamente si no se especifica
        if nombre_script is None:
            try:
                frame = inspect.currentframe()
                if frame and frame.f_back:
                    caller_frame = frame.f_back  
                    caller_filename = caller_frame.f_globals.get('__file__', 'script_desconocido')
                    self.nombre_script = Path(caller_filename).stem
                else:
                    self.nombre_script = 'script_desconocido'
            except Exception:
                self.nombre_script = 'script_desconocido'
        else:
            self.nombre_script = nombre_script
            
        # Ruta del archivo de estado usando resolución correcta para tareas programadas
        self.archivo_estado = self.resolver_ruta_archivo("estado_ejecucion.json", usar_directorio_script=True)
        
        # Inicializar Email si hay destinatarios configurados y parámetros SMTP
        self.email_handler = None
        if (self.email_destinatarios and smtp_server and smtp_port and 
            smtp_username and smtp_password):
            try:
                self.email_handler = Email(
                    smtp_server=smtp_server,
                    smtp_port=smtp_port,
                    smtp_username=smtp_username,
                    smtp_password=smtp_password,
                    nombre_trabajador_virtual=nombre_trabajador_virtual or self.nombre_script,
                    nombre_aprendizaje=nombre_aprendizaje or self.nombre_script,
                    dev=dev
                )
                self.mostrar("📧 Sistema de notificaciones por email configurado")
            except Exception as e:
                self.mostrar(f"⚠️  No se pudo configurar el sistema de email: {str(e)}", True)
        elif self.email_destinatarios:
            self.mostrar("⚠️  Emails configurados pero faltan parámetros SMTP. Notificaciones deshabilitadas.", True)

    @staticmethod
    def resolver_ruta_variables_entorno(nombre_archivo_env: str = '.env.production') -> str:
        """
        Resuelve correctamente la ruta del archivo de variables de entorno.
        
        Método estático específico para resolver rutas de archivos .env cuando se ejecuta
        desde tareas programadas de Windows. Evita el problema de duplicación de rutas
        que ocurre cuando el directorio de trabajo actual no es el directorio del ejecutable.
        
        ### Ejemplo
        ```python
        from glgrpa import ControlEjecucion
        
        # Resolver ruta del archivo .env.production
        ruta_env = ControlEjecucion.resolver_ruta_variables_entorno()
        
        # Verificar si existe antes de cargar
        if os.path.exists(ruta_env):
            from dotenv import load_dotenv
            load_dotenv(ruta_env)
            print(f"✅ Variables cargadas desde: {ruta_env}")
        else:
            print(f"❌ No se encontró archivo: {ruta_env}")
        
        # Para otros archivos .env
        ruta_env_dev = ControlEjecucion.resolver_ruta_variables_entorno('.env.development')
        ```
        >>> "C:\\path\\to\\executable\\.env.production"  # Ruta resuelta correctamente
        
        :param nombre_archivo_env: Nombre del archivo de variables de entorno (default: '.env.production')
        :return: Ruta absoluta resuelta del archivo de variables de entorno
        
        ### Raises
        #### Exception
        - Si no se puede determinar la ruta del ejecutable actual
        """
        return Windows.resolver_ruta_archivo(nombre_archivo_env, usar_directorio_script=True)

    def leer_estado_ejecucion(self) -> Dict[str, Any]:
        """
        Lee el estado de ejecución desde el archivo JSON.
        
        :return: Diccionario con el estado de ejecución
        """
        estado_default = {
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "exitoso": False,
            "intentos_diarios": 0,
            "intentos_maximos": self.intentos_maximos,
            "intentos_realizados": 0,
            "ultimo_error": None,
            "timestamp": datetime.now().isoformat(),
            "nombre_script": self.nombre_script
        }
        
        try:
            if os.path.exists(self.archivo_estado):
                with open(self.archivo_estado, 'r', encoding='utf-8') as f:
                    estado = json.load(f)
                    self.mostrar(f"📄 Estado de ejecución leído: {estado['fecha']} - Intentos: {estado['intentos_realizados']}/{estado['intentos_maximos']}")
                    return estado
            else:
                self.mostrar("📄 No existe archivo de estado previo, creando nuevo estado")
                return estado_default
        except Exception as e:
            self.mostrar(f"❌ Error al leer estado de ejecución: {str(e)}", True)
            return estado_default

    def guardar_estado_ejecucion(self, estado: Dict[str, Any]) -> bool:
        """
        Guarda el estado de ejecución en el archivo JSON.
        
        :param estado: Diccionario con el estado a guardar
        :return: True si se guardó correctamente, False en caso contrario
        """
        try:
            estado["timestamp"] = datetime.now().isoformat()
            with open(self.archivo_estado, 'w', encoding='utf-8') as f:
                json.dump(estado, f, indent=2, ensure_ascii=False)
            self.mostrar(f"💾 Estado guardado: exitoso={estado['exitoso']}, intentos={estado['intentos_realizados']}")
            return True
        except Exception as e:
            self.mostrar(f"❌ Error al guardar estado: {str(e)}", True)
            return False

    def validar_puede_ejecutar(self, estado: Dict[str, Any]) -> tuple[bool, str]:
        """
        Valida si el script puede ejecutarse basado en el estado actual.
        
        :param estado: Estado actual de ejecución
        :return: Tupla (puede_ejecutar, razon)
        """
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        
        # Si es un día diferente, resetear contadores
        if estado["fecha"] != fecha_actual:
            self.mostrar(f"📅 Nueva fecha detectada: {fecha_actual}, reseteando contadores")
            estado.update({
                "fecha": fecha_actual,
                "intentos_diarios": 0,
                "intentos_realizados": 0,
                "exitoso": False,
                "ultimo_error": None
            })
            return True, "Nueva fecha - ejecución permitida"
        
        # Si ya fue exitoso hoy y no permite múltiples ejecuciones
        if estado["exitoso"] and not self.permitir_multiples_ejecuciones_diarias:
            return False, f"Script ya ejecutado exitosamente hoy ({estado['fecha']})"
        
        # Si se alcanzó el límite de intentos diarios
        if estado["intentos_realizados"] >= self.intentos_maximos:
            return False, f"Límite de intentos diarios alcanzado ({estado['intentos_realizados']}/{self.intentos_maximos})"
        
        return True, "Ejecución permitida"

    def enviar_notificacion_email(self, exitoso: bool, error_msg: Optional[str] = None, 
                                intentos_realizados: int = 0) -> bool:
        """
        Envía notificación por email del resultado de la ejecución usando los métodos
        estandarizados de la clase Email (enviar_email_exito/enviar_email_error).
        
        :param exitoso: Si la ejecución fue exitosa
        :param error_msg: Mensaje de error si aplicable
        :param intentos_realizados: Número de intentos realizados
        :return: True si se envió correctamente
        """
        if not self.email_handler or not self.email_destinatarios:
            return False
            
        try:
            fecha_actual = datetime.now().strftime("%d/%m/%Y")
            
            if exitoso:
                # Usar método estandarizado para emails de éxito
                resultado = self.email_handler.enviar_email_exito(
                    destinatarios=self.email_destinatarios,
                    titulo=f"Ejecución Exitosa - {self.nombre_script}",
                    subtitulo="El script de automatización se ejecutó correctamente",
                    mensaje=f"Script: {self.nombre_script}\nIntentos realizados: {intentos_realizados}/{self.intentos_maximos}\nEstado: Completado correctamente",
                    fecha=fecha_actual,
                    duracion="00:00:00"  # Puede implementarse cálculo de duración si se necesita
                )
            else:
                # Usar método estandarizado para emails de error
                resultado = self.email_handler.enviar_email_error(
                    destinatarios=self.email_destinatarios,
                    titulo=f"Ejecución Fallida - {self.nombre_script}",
                    subtitulo=f"El script falló tras {intentos_realizados} intentos",
                    mensaje=f"Script: {self.nombre_script}\nIntentos realizados: {intentos_realizados}/{self.intentos_maximos}\nÚltimo error: {error_msg or 'Error no especificado'}\nEstado: Límite de reintentos alcanzado",
                    fecha=fecha_actual,
                    duracion="00:00:00"
                )
            
            self.mostrar(f"📧 Email de notificación enviado: {'✅ Éxito' if exitoso else '❌ Fallo'}")
            return resultado
            
        except Exception as e:
            self.mostrar(f"❌ Error al enviar email de notificación: {str(e)}", True)
            return False

    def ejecutar_con_control_estado(self, funcion_principal: Callable, *args, **kwargs) -> bool:
        """
        Ejecuta una función con control de estado. Cada ejecución es independiente
        y controlada por tareas programadas de Windows (ej: 7:00, 7:30, 8:00).
        
        :param funcion_principal: Función a ejecutar
        :param args: Argumentos posicionales para la función
        :param kwargs: Argumentos con nombre para la función
        :return: True si la ejecución fue exitosa
        """
        self.mostrar(f"🚀 Iniciando control de ejecución para: {self.nombre_script}")
        
        # Leer estado actual
        estado = self.leer_estado_ejecucion()
        
        # Validar si puede ejecutar
        puede_ejecutar, razon = self.validar_puede_ejecutar(estado)
        if not puede_ejecutar:
            self.mostrar(f"🚫 Ejecución bloqueada: {razon}")
            return False
        
        self.mostrar(f"✅ Validación passed: {razon}")
        
        # Incrementar contador de intentos
        intento_actual = estado["intentos_realizados"] + 1
        self.mostrar(f"🔄 Ejecución {intento_actual}/{self.intentos_maximos}")
        
        try:
            # Actualizar estado antes del intento
            estado["intentos_realizados"] = intento_actual
            estado["intentos_diarios"] = intento_actual
            self.guardar_estado_ejecucion(estado)
            
            # Ejecutar función principal
            resultado = funcion_principal(*args, **kwargs)
            
            if resultado:
                # Ejecución exitosa
                estado["exitoso"] = True
                estado["ultimo_error"] = None
                self.guardar_estado_ejecucion(estado)
                
                self.mostrar(f"✅ Ejecución exitosa en intento {intento_actual}")
                
                # Enviar email de éxito
                self.enviar_notificacion_email(
                    exitoso=True, 
                    intentos_realizados=intento_actual
                )
                
                return True
            else:
                # Función retornó False
                error_msg = f"Función principal retornó False en intento {intento_actual}"
                estado["ultimo_error"] = error_msg
                self.mostrar(f"⚠️  {error_msg}")
                
                # Guardar estado del fallo
                self.guardar_estado_ejecucion(estado)
                
                # Si alcanzó el máximo de intentos, enviar email de fallo final
                if intento_actual >= self.intentos_maximos:
                    self.mostrar(f"❌ Límite de intentos alcanzado ({intento_actual}/{self.intentos_maximos})")
                    self.enviar_notificacion_email(
                        exitoso=False,
                        error_msg=error_msg,
                        intentos_realizados=intento_actual
                    )
                else:
                    self.mostrar(f"⏳ Esperando próxima ejecución programada. Intentos restantes: {self.intentos_maximos - intento_actual}")
                
                return False
                
        except Exception as e:
            # Error durante la ejecución
            error_msg = f"Error en intento {intento_actual}: {str(e)}"
            estado["ultimo_error"] = error_msg
            self.mostrar(f"❌ {error_msg}", True)
            
            # Tomar screenshot para debugging si está disponible
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_nombre = f"error_{self.nombre_script}_intento_{intento_actual}_{timestamp}"
                self.tomar_screenshot(screenshot_nombre)
                self.mostrar(f"📸 Screenshot guardado: {screenshot_nombre}.png")
            except Exception as screenshot_error:
                self.mostrar(f"⚠️  No se pudo tomar screenshot: {str(screenshot_error)}")
            
            # Guardar estado después del error
            self.guardar_estado_ejecucion(estado)
            
            # Si alcanzó el máximo de intentos, enviar email de fallo final
            if intento_actual >= self.intentos_maximos:
                self.mostrar(f"❌ Límite de intentos alcanzado ({intento_actual}/{self.intentos_maximos})")
                self.enviar_notificacion_email(
                    exitoso=False,
                    error_msg=error_msg,
                    intentos_realizados=intento_actual
                )
            else:
                self.mostrar(f"⏳ Esperando próxima ejecución programada. Intentos restantes: {self.intentos_maximos - intento_actual}")
            
            return False

    def decorador_ejecucion_controlada(self, 
                                     intentos_maximos: Optional[int] = None,
                                     permitir_multiples_ejecuciones_diarias: Optional[bool] = None,
                                     email_destinatarios: Optional[list] = None):
        """
        Decorador para aplicar control de ejecución a cualquier función.
        
        :param intentos_maximos: Override del número máximo de intentos
        :param permitir_multiples_ejecuciones_diarias: Override de múltiples ejecuciones diarias
        :param email_destinatarios: Override de destinatarios de email
        :return: Decorador
        """
        def decorador(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Usar valores override si se proporcionan
                _intentos_maximos = intentos_maximos or self.intentos_maximos
                _permitir_multiples = permitir_multiples_ejecuciones_diarias if permitir_multiples_ejecuciones_diarias is not None else self.permitir_multiples_ejecuciones_diarias
                _email_destinatarios = email_destinatarios or self.email_destinatarios
                
                # Crear instancia temporal con configuración específica, manteniendo configuración SMTP
                control = ControlEjecucion(
                    intentos_maximos=_intentos_maximos,
                    permitir_multiples_ejecuciones_diarias=_permitir_multiples,
                    dev=self.dev,
                    email_destinatarios=_email_destinatarios,
                    nombre_script=func.__name__,
                    # Mantener configuración SMTP de la instancia original
                    smtp_server=getattr(self.email_handler, 'get_configuracion', lambda x: None)('smtp_server') if self.email_handler else None,
                    smtp_port=getattr(self.email_handler, 'get_configuracion', lambda x: None)('smtp_port') if self.email_handler else None,
                    smtp_username=getattr(self.email_handler, 'get_configuracion', lambda x: None)('smtp_username') if self.email_handler else None,
                    smtp_password=getattr(self.email_handler, 'get_configuracion', lambda x: None)('smtp_password') if self.email_handler else None,
                    nombre_trabajador_virtual=getattr(self.email_handler, 'get_configuracion', lambda x: None)('nombre_trabajador_virtual') if self.email_handler else None,
                    nombre_aprendizaje=getattr(self.email_handler, 'get_configuracion', lambda x: None)('nombre_aprendizaje') if self.email_handler else None
                )
                
                return control.ejecutar_con_control_estado(func, *args, **kwargs)
                
            return wrapper
        return decorador
