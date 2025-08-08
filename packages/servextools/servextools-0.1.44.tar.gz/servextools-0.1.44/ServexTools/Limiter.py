from flask import request, Response
from ServexTools.EscribirLog import EscribirLog
import time
import redis
from functools import wraps

def get_real_ip():
    """Obtener la IP real del cliente cuando nginx actúa como proxy"""
    # Primero intentar obtener la IP del header X-Real-IP (configurado en nginx)
    if request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    # Luego intentar X-Forwarded-For
    elif request.headers.get('X-Forwarded-For'):
        # X-Forwarded-For puede contener múltiples IPs, tomar la primera
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    # Si no hay headers de proxy, usar la IP directa
    else:
        return request.remote_addr
    
    
def limitar_peticiones(key, max_requests=15, window_seconds=60,redisconexion={'host':'localhost','port':6379,'db':2}):
    """
    Implementación manual de rate limiting usando Redis con detección de ataques
    
    Args:
        key: Clave única para identificar al cliente (usuario:IP)
        max_requests: Número máximo de peticiones permitidas en la ventana de tiempo
        window_seconds: Tamaño de la ventana de tiempo en segundos
        
    Returns:
        (bool, int): (permitido, peticiones_restantes)
    """
    try:
        # Configuración de Redis para almacenar los contadores de rate limiting
        redis_client = redis.Redis(host=redisconexion['host'], port=redisconexion['port'], db=redisconexion['db'], decode_responses=True)
        
        # Claves en Redis
        redis_key = f"rate_limit:{key}"
        redis_block_key = f"rate_limit_block:{key}"
        
        # Verificar si está bloqueado
        is_blocked = redis_client.get(redis_block_key)
        if is_blocked:
            block_ttl = redis_client.ttl(redis_block_key)
            EscribirLog(f"Cliente {key} bloqueado por {block_ttl} segundos más")
            return False, 0
        
        # Obtener el contador actual y su tiempo de expiración
        count = redis_client.get(redis_key)
        ttl = redis_client.ttl(redis_key)
        
        # Si no existe o ha expirado, crear nuevo contador
        if count is None or ttl < 0:
            # Establecer contador en 1 y tiempo de expiración
            redis_client.setex(redis_key, window_seconds, 1)
            # Registrar primera petición
            EscribirLog(f"Primera petición de {key} en nueva ventana de tiempo")
            return True, max_requests - 1
        
        # Convertir contador a entero
        count = int(count)
        
        # Incrementar contador
        new_count = redis_client.incr(redis_key)
        
        # Si excede el límite, denegar y bloquear temporalmente
        if new_count > max_requests:
            # Calcular tiempo de bloqueo progresivo (más peticiones = más tiempo bloqueado)
            exceso = new_count - max_requests
            block_time = min(window_seconds * (2 ** min(exceso, 5)), 86400)  # Máximo 24 horas
            
            # Bloquear por tiempo progresivo
            redis_client.setex(redis_block_key, block_time, 1)
            
            # Registrar bloqueo
            EscribirLog(f"ALERTA DE SEGURIDAD: Cliente {key} bloqueado por {block_time} segundos - Excedió límite con {new_count}/{max_requests}")
            
            return False, 0
        
        # Devolver permitido y peticiones restantes
        return True, max_requests - new_count
        
    except Exception as e:
        EscribirLog(f"Error en limitar_peticiones: {str(e)}")
        # En caso de error, permitir la petición
        return True, 0

def rate_limit(max_requests=15, window_seconds=60, key_func=None):
    """
    Decorador para limitar peticiones a una ruta
    
    Args:
        max_requests: Número máximo de peticiones permitidas en la ventana de tiempo
        window_seconds: Tamaño de la ventana de tiempo en segundos
        key_func: Función para obtener la clave única del cliente (por defecto IP)
        
    Returns:
        Decorador para aplicar a una ruta
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Obtener clave única del cliente
            if key_func:
                key = key_func()
            else:
                key = get_real_ip()
                
            # Aplicar limitación
            permitido, restantes = limitar_peticiones(key, max_requests, window_seconds)
            
            # Si no está permitido, devolver error 429 con headers de rate limiting
            if not permitido:
                EscribirLog(f"ALERTA DE SEGURIDAD: Límite excedido para {key}")
                headers = {
                    'X-RateLimit-Limit': str(max_requests),
                    'X-RateLimit-Remaining': '0',
                    'X-RateLimit-Reset': str(int(time.time()) + window_seconds),
                    'Retry-After': str(window_seconds)
                }
                return Response(
                    "Demasiadas solicitudes. Por favor, inténtelo más tarde.", 
                    status=429,
                    headers=headers
                )
                
            # Ejecutar la función original
            response = f(*args, **kwargs)
            
            # Si la respuesta es un objeto Response, añadir headers de rate limiting
            if isinstance(response, Response):
                response.headers['X-RateLimit-Limit'] = str(max_requests)
                response.headers['X-RateLimit-Remaining'] = str(restantes)
                response.headers['X-RateLimit-Reset'] = str(int(time.time()) + window_seconds)
                
            return response
        return decorated_function
    return decorator