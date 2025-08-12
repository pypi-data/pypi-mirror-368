from ServexTools.EscribirLog import EscribirLog
from ServexTools import Tools
from flask import request
import re

def GetMetaData(datosusuario:dict=None)->tuple:
    try:
        usuarionombre=datosusuario.get('nombre')+' '+datosusuario.get('apellido') if datosusuario else ''
        
        # Obtener IP del cliente (considerando proxies)
        ip_cliente = request.environ.get('HTTP_X_FORWARDED_FOR')
        if ip_cliente:
            ip_cliente = ip_cliente.split(',')[0].strip()
        else:
            ip_cliente = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        
        # Obtener información del navegador y sistema operativo
        user_agent = request.headers.get('User-Agent', '')
        
        # Obtener otros headers relevantes
        referer = request.headers.get('Referer', '')
        accept_language = request.headers.get('Accept-Language', '')
        accept_encoding = request.headers.get('Accept-Encoding', '')
        host = request.headers.get('Host', '')
        
        # Obtener fecha y hora actual
        fecha_conexion = Tools.FechaHora()
        
        # Obtener información adicional del request
        metodo_http = request.method
        url_completa = request.url
        esquema = request.scheme  # http o https
        
        # Crear objeto con todos los datos de conexión
        datos_conexion = {
            'usuario_nombre': usuarionombre,
            'ip_cliente': ip_cliente,
            'user_agent': user_agent,
            'navegador_info': _ParsearUserAgent(user_agent) if user_agent else {},
            'fecha_conexion': fecha_conexion,
            'metodo_http': metodo_http,
            'url_acceso': url_completa,
            'esquema': esquema,
            'host': host,
            'referer': referer,
            'idioma_preferido': accept_language,
            'codificacion_aceptada': accept_encoding,
            'headers_adicionales': {
                'X-Forwarded-For': request.headers.get('X-Forwarded-For', ''),
                'X-Real-IP': request.headers.get('X-Real-IP', ''),
                'Connection': request.headers.get('Connection', ''),
                'Cache-Control': request.headers.get('Cache-Control', '')
            },
            'estado': 'A',
            'fecha_registro': fecha_conexion
        }
        
        return datos_conexion,''
    except Exception as e:
        EscribirLog("Error GetMetaData: "+str(e))
        return None,str(e)

def _ParsearUserAgent(user_agent:str)->dict:
    """
    Parsear User-Agent para extraer información del navegador y sistema operativo
    """
    try:
        if not user_agent:
            return {}
        
        info = {
            'navegador': 'Desconocido',
            'version_navegador': '',
            'sistema_operativo': 'Desconocido',
            'dispositivo_tipo': 'Desktop',
            'es_movil': False,
            'es_tablet': False,
            'es_bot': False
        }
        
        user_agent_lower = user_agent.lower()
        
        # Detectar bots/crawlers
        bots = ['bot', 'crawler', 'spider', 'scraper', 'googlebot', 'bingbot', 'facebookexternalhit']
        if any(bot in user_agent_lower for bot in bots):
            info['es_bot'] = True
            info['dispositivo_tipo'] = 'Bot'
        
        # Detectar navegadores
        if 'chrome' in user_agent_lower and 'chromium' not in user_agent_lower:
            info['navegador'] = 'Chrome'
            match = re.search(r'chrome/(\d+\.[\d\.]*)', user_agent_lower)
            if match:
                info['version_navegador'] = match.group(1)
        elif 'firefox' in user_agent_lower:
            info['navegador'] = 'Firefox'
            match = re.search(r'firefox/(\d+\.[\d\.]*)', user_agent_lower)
            if match:
                info['version_navegador'] = match.group(1)
        elif 'safari' in user_agent_lower and 'chrome' not in user_agent_lower:
            info['navegador'] = 'Safari'
            match = re.search(r'version/(\d+\.[\d\.]*)', user_agent_lower)
            if match:
                info['version_navegador'] = match.group(1)
        elif 'edge' in user_agent_lower or 'edg/' in user_agent_lower:
            info['navegador'] = 'Edge'
            match = re.search(r'edg?[e]?/(\d+\.[\d\.]*)', user_agent_lower)
            if match:
                info['version_navegador'] = match.group(1)
        elif 'opera' in user_agent_lower or 'opr/' in user_agent_lower:
            info['navegador'] = 'Opera'
            match = re.search(r'(?:opera|opr)/(\d+\.[\d\.]*)', user_agent_lower)
            if match:
                info['version_navegador'] = match.group(1)
        
        # Detectar sistema operativo
        if 'windows' in user_agent_lower:
            info['sistema_operativo'] = 'Windows'
            if 'windows nt 10' in user_agent_lower:
                info['sistema_operativo'] = 'Windows 10/11'
            elif 'windows nt 6.3' in user_agent_lower:
                info['sistema_operativo'] = 'Windows 8.1'
            elif 'windows nt 6.2' in user_agent_lower:
                info['sistema_operativo'] = 'Windows 8'
            elif 'windows nt 6.1' in user_agent_lower:
                info['sistema_operativo'] = 'Windows 7'
        elif 'macintosh' in user_agent_lower or 'mac os' in user_agent_lower:
            info['sistema_operativo'] = 'macOS'
        elif 'linux' in user_agent_lower:
            info['sistema_operativo'] = 'Linux'
        elif 'android' in user_agent_lower:
            info['sistema_operativo'] = 'Android'
            info['es_movil'] = True
            info['dispositivo_tipo'] = 'Mobile'
        elif 'iphone' in user_agent_lower:
            info['sistema_operativo'] = 'iOS'
            info['es_movil'] = True
            info['dispositivo_tipo'] = 'Mobile'
        elif 'ipad' in user_agent_lower:
            info['sistema_operativo'] = 'iPadOS'
            info['es_tablet'] = True
            info['dispositivo_tipo'] = 'Tablet'
        
        # Detectar dispositivos móviles adicionales
        mobile_indicators = ['mobile', 'android', 'iphone', 'ipod', 'blackberry', 'windows phone']
        if any(indicator in user_agent_lower for indicator in mobile_indicators) and not info['es_tablet']:
            info['es_movil'] = True
            info['dispositivo_tipo'] = 'Mobile'
        
        # Detectar tablets adicionales
        tablet_indicators = ['tablet', 'ipad']
        if any(indicator in user_agent_lower for indicator in tablet_indicators):
            info['es_tablet'] = True
            info['dispositivo_tipo'] = 'Tablet'
            info['es_movil'] = False
        
        return info
        
    except Exception as e:
        EscribirLog(f"Error en ParsearUserAgent: {str(e)}")
        return {}