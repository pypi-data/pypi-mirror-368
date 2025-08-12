# ServexTools
[![PyPI version](https://badge.fury.io/py/servextools.svg)](https://pypi.org/project/servextools/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Framework avanzado para desarrollo de sistemas empresariales Python/Flask con MongoDB

---

## Descripción General
ServexTools es un framework completo para acelerar el desarrollo de aplicaciones empresariales en Python, especialmente orientado a sistemas basados en Flask y MongoDB. Proporciona un conjunto de herramientas optimizadas para manejo de datos, generación de interfaces, seguridad, comunicación en tiempo real y más.

### Características principales
- **Integración avanzada con MongoDB**: CRUD optimizado, replicación automática, manejo de transacciones y sesiones distribuidas
- **Generación de tablas HTML de alto rendimiento**: Procesamiento vectorizado con Polars y NumPy para grandes volúmenes de datos
- **WebSockets optimizados**: Comunicación bidireccional en tiempo real con configuración para alta disponibilidad
- **Sistema de sesiones distribuidas**: Almacenamiento eficiente de datos de sesión en MongoDB
- **Seguridad integrada**: Limitación de peticiones, encriptación JWT, protección contra ataques
- **Utilidades de fecha/hora**: Conversión, formateo y cálculos con soporte para zonas horarias
- **Logs avanzados**: Sistema de logs con rotación, categorización y notificaciones en tiempo real
- **Operaciones con archivos**: Manipulación segura, compresión y procesamiento eficiente

---

## Estructura del Proyecto

```
ServexTools/
├── Tools.py           # Utilidades generales y funciones de ayuda (989 líneas)
├── Table.py           # Generación de tablas HTML de alto rendimiento (1494 líneas)
├── ReplicaDb.py       # Sistema de replicación MongoDB en tiempo real (560 líneas)
├── conexion.py        # Abstracción para conexiones a bases de datos (432 líneas)
├── Necesario.py       # Manejo de sesiones distribuidas y paginación (241 líneas)
├── socket_manager.py  # Gestión optimizada de WebSockets (72 líneas)
├── EscribirLog.py     # Sistema de logs avanzado (163 líneas)
├── Limiter.py         # Control de tasa de peticiones y seguridad (138 líneas)
├── TablePV.py         # Tablas especializadas para punto de venta (632 líneas)
├── GetTime.py         # Utilidades avanzadas de tiempo y fecha (62 líneas)
├── Enumerable.py      # Enumeraciones y constantes del sistema (7 líneas)
└── __init__.py        # Inicialización del paquete
```

---

## Instalación

```bash
pip install servextools
```

## Uso Rápido

### Conexión y operaciones con MongoDB
```python
from ServexTools import conexion

# Conexión básica
coleccion, cliente = conexion.Get('usuarios')

# Inserción con manejo automático de historial
from ServexTools import Tools
datos = {"nombre": "Juan", "edad": 30}
conexion.ProcesarDatos('usuarios', datos, 'idusuario', PonerHistorial=True)

# Replicación automática entre instancias
from ServexTools.ReplicaDb import ReplicaCluster
cluster = ReplicaCluster(
    'mongodb://user:pass@servidor-principal:27017/db?authSource=admin',
    'mongodb://user:pass@servidor-replica:27017/db?authSource=admin'
)
coleccion = cluster['midb']['usuarios']
coleccion.insert_one({"nombre": "Ana", "edad": 25})  # Se replica automáticamente
```

### Generación de tablas HTML de alto rendimiento
```python
from ServexTools import Table

# Datos de ejemplo (funciona eficientemente con miles o millones de registros)
datos = [
    {"Nombre": "Juan", "Edad": 30, "Salario": 2500.50},
    {"Nombre": "Ana", "Edad": 25, "Salario": 3200.75}
]

# Configuración de columnas
columnas = ("Nombre", "Edad", "Salario")
datos_columnas = ("Nombre", "Edad", "Salario")
class_columnas = ("text-left", "text-center", "text-right")
formato_columnas = ("", "", "moneda")
totalizar_columnas = (False, False, True)

# Generar tabla HTML con paginación y formateo automático
html = Table.CrearTabla(
    datos,
    NombreColumnas=columnas,
    DatosColumnas=datos_columnas,
    ClassColumnas=class_columnas,
    FormatoColumnas=formato_columnas,
    TotalizarColumnas=totalizar_columnas,
    paginacion=True,
    LongitudPaginacion=100
)
```

### WebSockets optimizados
```python
from flask import Flask
from ServexTools.socket_manager import init_socketio, init

# Inicializar gevent al principio de la aplicación
init()

app = Flask(__name__)
# Configuración optimizada para producción con Redis
socketio = init_socketio(app, isProduccion=True, Proyecto="MiAplicacion")

@socketio.on('connect')
def handle_connect():
    print('Cliente conectado')

@socketio.on('mensaje')
def handle_mensaje(data):
    socketio.emit('respuesta', {'status': 'recibido'})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
```

### Control de tasa de peticiones
```python
from flask import Flask
from ServexTools.Limiter import rate_limit

app = Flask(__name__)

@app.route('/api/datos')
@rate_limit(max_requests=15, window_seconds=60)
def obtener_datos():
    # Esta ruta está protegida contra abusos
    return {'datos': 'información importante'}
```

### Sesiones distribuidas
```python
from flask import Flask
from ServexTools.Necesario import Session

app = Flask(__name__)
app.secret_key = 'clave-secreta'

@app.route('/guardar')
def guardar_datos():
    # Almacena grandes volúmenes de datos en MongoDB
    Session['datos_usuario'] = {'historial': [...], 'preferencias': {...}}
    return 'Datos guardados'

@app.route('/recuperar')
def recuperar_datos():
    # Recupera datos de forma eficiente
    datos = Session['datos_usuario']
    return datos
```

---

## Componentes Principales

### Tools.py
Colección extensa de utilidades para operaciones comunes en aplicaciones empresariales:

- **Manipulación de fechas**: Conversión, formateo, cálculos y zonas horarias
  ```python
  from ServexTools import Tools
  
  # Conversión y formateo
  fecha = Tools.StrToDate("25/12/2023")
  fecha_formateada = Tools.DateFormat(fecha)
  
  # Cálculos con fechas
  fecha_futura = Tools.DateTimeAdd_D_H_M_S(fecha, AddDias=5, AddHoras=2)
  ```

- **Operaciones con archivos**
  ```python
  # Lectura/escritura segura
  contenido = Tools.ReadFile("config.json")
  Tools.WriteFile("log.txt", "Nueva entrada de log")
  
  # Operaciones con directorios
  if not Tools.ExisteDirectorio("datos"):
      Tools.CrearDirectorio("datos")
  ```

- **Formateo de datos**
  ```python
  # Conversión de tipos
  numero = Tools.StrToInt("123")
  decimal = Tools.StrToFloat("123.45")
  
  # Formateo de moneda
  valor_formateado = Tools.FormatoMoneda(1234.56)  # "$1,234.56"
  ```

- **Seguridad**
  ```python
  # Encriptación/desencriptación JWT
  token = Tools.Encriptar({"usuario": 123}, "clave-secreta")
  datos = Tools.DesEncriptar(token, "clave-secreta")
  ```

- **Manejo de respuestas API**
  ```python
  from ServexTools.Enumerable import TipoMensaje
  
  # Respuesta estándar
  respuesta = Tools.Mensaje(
      iddatos=usuario_id,
      estatus="Exito",
      mensaje="Operación completada",
      tipomensaje=TipoMensaje.MSJ
  )
  ```

### Table.py
Sistema avanzado para generación de tablas HTML con procesamiento vectorizado:

- **Características avanzadas**:
  - Procesamiento paralelo con Polars y NumPy para millones de registros
  - Paginación cliente/servidor automática
  - Formateo condicional de celdas
  - Cálculo de totales y subtotales
  - Marcado condicional de filas
  - Subfilas y datos anidados
  - Exportación a diferentes formatos

- **Optimizaciones**:
  - Caché LRU para operaciones repetitivas
  - Procesamiento por lotes para grandes volúmenes
  - Generación eficiente con StringIO
  - Notificaciones de progreso en tiempo real

### ReplicaDb.py
Sistema de replicación MongoDB en tiempo real:

- **Replicación transparente**: Las operaciones se replican automáticamente a un servidor secundario
- **Cola de operaciones**: Sistema de cola para garantizar la consistencia
- **Manejo de errores**: Reintentos automáticos y registro de errores
- **API compatible**: Implementa la misma API que PyMongo para facilitar la integración

### conexion.py
Abstracción para conexiones a bases de datos:

- **Conexión MongoDB**: Configuración automática con parámetros óptimos
- **Historial de cambios**: Registro automático de modificaciones en documentos
- **Transacciones**: Soporte para operaciones atómicas
- **Integridad de datos**: Validación automática antes de operaciones

### socket_manager.py
Gestión optimizada de WebSockets:

- **Configuración para producción**: Optimizaciones para entornos de alta disponibilidad
- **Integración con Redis**: Comunicación entre múltiples instancias
- **Canales seguros**: Generación automática de canales únicos
- **Configuración de timeouts**: Ajustes para mantener conexiones estables

### Limiter.py
Control avanzado de tasa de peticiones:

- **Protección contra abusos**: Limitación de peticiones por IP o usuario
- **Bloqueo progresivo**: Mayor tiempo de bloqueo para intentos repetidos
- **Detección de ataques**: Identificación de patrones sospechosos
- **Integración con Redis**: Almacenamiento distribuido de contadores

### Necesario.py
Sistema de sesiones distribuidas:

- **Almacenamiento en MongoDB**: Soporte para grandes volúmenes de datos en sesión
- **Fragmentación automática**: División de datos grandes en fragmentos
- **Paginación servidor**: Sistema optimizado para tablas con millones de registros
- **Índices automáticos**: Creación de índices para consultas eficientes

---

## Dependencias Principales
- **flask**: Framework web
- **pymongo**: Cliente MongoDB
- **polars-lts-cpu**: Procesamiento de datos vectorizado
- **numpy**: Operaciones numéricas vectorizadas
- **flask-socketio**: Comunicación en tiempo real
- **gevent**: Servidor WSGI asíncrono
- **redis**: Almacenamiento en memoria distribuido
- **PyJWT**: Tokens web JSON
- **pytz**: Soporte para zonas horarias
- **httpx**: Cliente HTTP asíncrono

---

## Licencia
MIT - Ver archivo [LICENSE](LICENSE)

---

## Contribución
Las contribuciones son bienvenidas. Por favor, asegúrate de seguir las convenciones de código existentes y añadir pruebas para nuevas funcionalidades.
