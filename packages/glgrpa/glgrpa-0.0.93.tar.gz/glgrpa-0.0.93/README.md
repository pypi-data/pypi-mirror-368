# glgrpa

`glgrpa` es una librería diseñada para automatizar tareas relacionadas con RPA (Robotic Process Automation) dentro del entorno del Grupo Los Grobo. Esta librería proporciona herramientas para interactuar con navegadores web, manejar archivos Excel, gestionar descargas y realizar operaciones específicas en aplicaciones como ARCA.

## Instalación

Puedes instalar la librería directamente desde PyPI (cuando esté publicada) utilizando pip:

```bash
pip install glgrpa
```

## Características

- **Automatización de Navegadores** : Basado en Selenium, permite interactuar con elementos web, realizar clics, ingresar texto, manejar ventanas y más.
- **Gestión de Descargas** : Facilita la organización y limpieza de carpetas de descargas personalizadas.
- **Manejo de Archivos Excel** : Permite leer archivos Excel y convertirlos en DataFrames de pandas.
- **Interacción con ARCA** : Automatiza tareas específicas en la plataforma ARCA, como el inicio de sesión, selección de relaciones y descarga de cartas de porte electrónicas.
- **Terminal y Logs** : Incluye herramientas para mostrar mensajes en la consola con colores y formatos para facilitar el seguimiento de la ejecución.

## Estructura del Proyecto

La librería está organizada en los siguientes módulos:

- **`src/Terminal`** : Proporciona herramientas para mostrar mensajes en la consola y gestionar tiempos de espera.
- **`src/Chrome`** : Contiene funcionalidades para interactuar con el navegador Chrome utilizando Selenium.
- **`src/Windows`** : Maneja operaciones relacionadas con el sistema de archivos en Windows, como mover archivos y crear estructuras de carpetas.
- **`src/Excel`** : Facilita la lectura de archivos Excel.
- **`src/ARCA`** : Incluye clases específicas para interactuar con la plataforma ARCA.

## Uso

### Ejemplo de Uso Básico

```python
from glgrpa.src.ARCA.Cartas_de_porte_electronicas.AplicativoCartasDePorteElectronicas import AplicativoCartaDePorteElectronica

# Inicializar la clase
app = AplicativoCartaDePorteElectronica(dev=True)

# Abrir navegador y navegar a ARCA
app.abrir_navegador()
app.navegar_inicio()

# Ingresar credenciales
app.ingresar_credenciales()

# Cambiar relación
app.cambiar_relacion("Nombre de la relación")

# Descargar cartas de porte
cpe_list = app.obtener_listado_cpe()
for cpe in cpe_list:
    app.descargar_carta_de_porte(cpe)
```

### Leer un Archivo Excel

```python
from glgrpa.src.Excel.Excel import Excel

# Leer un archivo Excel
excel = Excel("ruta_del_archivo.xlsx")
dataframe = excel.leer_excel("NombreHoja")
print(dataframe)
```

## Requisitos

Los requisitos de la librería están especificados en el archivo `requirements.txt`:

- `selenium`
- `pandas`
- `colorama`
- `openpyxl`
- `office365-rest-python-client`

## Autor

**Gabriel Bellome** < [gabriel.bellome@losgrobo.com](vscode-file://vscode-app/c:/Users/gabriel.bellome/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html) >

## Licencia

Este proyecto está bajo una licencia privada y es propiedad del Grupo Los Grobo.
