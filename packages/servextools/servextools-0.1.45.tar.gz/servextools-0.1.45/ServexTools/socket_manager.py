from ServexTools.Enumerable import async_mode
def init():
    from gevent import monkey
    monkey.patch_all()

_socketio_instance = None

# Forma recomendada: usar URL explícita para Redis
REDIS_URL = 'redis://localhost:6379/0'  # Puedes parametrizar esto con variables de entorno
# Configuración del pool de conexiones para Redis
REDIS_POOL_OPTIONS = {
    'socket_timeout': 5,
    'socket_connect_timeout': 5,
    'health_check_interval': 30
}

def get_socketio():
    global _socketio_instance
    return _socketio_instance

def init_socketio(app,isProduccion=False,Proyecto="Servex",async_mode:async_mode=async_mode.GEVENT):
    """
    Inicializa el socketio.
    
    Args:
        app: La aplicación Flask.
        isProduccion: Indica si el entorno es de producción.
        Proyecto: El nombre del proyecto.
    Returns:
        SocketIO: Instancia de SocketIO.
    
    Notas:
        Si no existe el archivo sctkRedis, se crea con un UUID aleatorio.
        Es necesario que importes 
            from gevent import monkey
        y parches al principio de la aplicación antes de las importaciones
            monkey.patch_all()
    Notas:
        Puedes usar la función init() para parchear gevent.
    """
    import uuid
    import ServexTools.Tools as Tools
    from flask_socketio import SocketIO
    global _socketio_instance
    if _socketio_instance is None:
        if not Tools.ExistFile('sctkRedis'):
            Tools.CreateFile(nombre="sctkRedis",datos=uuid.uuid4().hex)
        
        canalredis = Tools.ReadFile("sctkRedis")
        if isProduccion:
            _socketio_instance = SocketIO(app,
                            ping_timeout=15000,  # Reducido de 25000
                            ping_interval=5000,  # Reducido de 10000
                            cors_allowed_origins="*",
                            async_mode=async_mode,
                            message_queue=REDIS_URL,
                            channel=Proyecto + canalredis,
                            logger=False,
                            engineio_logger=False,
                            async_handlers=True,  # Manejo asíncrono de eventos
                            websocket=True,  # Forzar websocket como transporte preferido
                            redis_options=REDIS_POOL_OPTIONS)  # Opciones optimizadas para Redis
        else:
            _socketio_instance = SocketIO(app,
                        ping_timeout=5000,
                        ping_interval=2000,
                        cors_allowed_origins="*",
                        async_mode='threading',
                        websocket=True)  # Forzar websocket como transporte preferido
    return _socketio_instance

# Nota: Puedes usar variables de entorno para REDIS_URL en producción para mayor flexibilidad y seguridad.
