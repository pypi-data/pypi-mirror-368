import ServexTools.conexion as con
import pickle
import base64
from uuid import uuid4
from flask import session
from pymongo import ASCENDING
from ServexTools.socket_manager import get_socketio
socketio = get_socketio()

db, client = con.GetDB()
class SessionMeta(type):
    def __getitem__(cls, key, sessionidusuario = None):
        instance = cls(sessionidusuario)
        return instance[key]

    def __setitem__(cls, key, value, sessionidusuario = None):
        instance = cls(sessionidusuario)
        instance[key] = value

class Session(metaclass = SessionMeta):
    def __init__(self, sessionidusuario = None):
        from flask import session
        try:
            self.idusuario = session['idusuario']
        except:
            self.idusuario = sessionidusuario
        self.reportes_temp = db['reportes_temp']
        self.chunk_size = 1024 * 1024  # 1MB chunk size
    
    def __setitem__(self, key, *values):
        if not values:
            return

        json_filtro_chunks = {
            '__idusuario': self.idusuario,
            '__nombre_session': {'$regex': f'^{key}_chunk_\\d+$'}
        }
        self.reportes_temp.delete_many(json_filtro_chunks)

        json_filtro = { 
            '__idusuario': self.idusuario,
            '__nombre_session': key
        }
        self.reportes_temp.delete_one(json_filtro)

        serialized_data = base64.b64encode(pickle.dumps(list(values))).decode('utf-8')

        data_length = len(serialized_data)
        chunks_count = (data_length + self.chunk_size - 1) // self.chunk_size

        self.reportes_temp.insert_one({
            **json_filtro,
            '__valor': [{'chunks_count': chunks_count, 'total_size': data_length}]
        })

        for i in range(chunks_count):
            start = i * self.chunk_size
            end = min((i + 1) * self.chunk_size, data_length)
            chunk_data = serialized_data[start:end]

            self.reportes_temp.insert_one({
                '__idusuario': self.idusuario,
                '__nombre_session': f"{key}_chunk_{i}",
                '__valor': [chunk_data]
            })

    def __getitem__(self, key):
        idusuario = self.idusuario
        result = self.reportes_temp.find_one({
            '__idusuario': idusuario,
            '__nombre_session': key
        })

        if result is None:
            return None

        metadata = result['__valor'][0]

        if not isinstance(metadata, dict) or 'chunks_count' not in metadata:
            return result['__valor'][0]

        chunks_count = metadata['chunks_count']

        serialized_data = ""
        for i in range(chunks_count):
            chunk = self.reportes_temp.find_one({
                '__idusuario': idusuario,
                '__nombre_session': f"{key}_chunk_{i}"
            })

            if chunk is None:
                raise ValueError(f"Chunk {i} no encontrado para la clave {key}")

            serialized_data += chunk['__valor'][0]
        try:
            data = pickle.loads(base64.b64decode(serialized_data.encode('utf-8')))
            return data[0]
        except Exception as e:
            print(f"Error al deserializar datos: {e}")
            return None

def _formatear_find_paginacion(dt: dict):
    is_pagination_data = False
    
    if 'parametros_tabla' in dt:
        for key in dt['parametros_tabla'].keys():
            if isinstance(key, str) and key.startswith('ps_') or key in ['SubFilas', 'FilasPlus'] and dt['parametros_tabla'][key]:
                is_pagination_data = True
                break
    
    formatear_a_tupla = [
        'NombreColumnas',
        'DatosColumnas',
        'ClassColumnas',
        'FormatoColumnas',
        'TotalizarColumnas',
        'SubColumnasDatos',
        'MarcarRows'
    ]
    
    dt = dt['parametros_tabla']
    
    for key in formatear_a_tupla:
        if key in dt and dt[key] is not None and isinstance(dt[key], list):
            dt[key] = _convertir_lista_a_tupla_recursivo(dt[key])
    
    if 'SubFilas' in dt and dt['SubFilas'] and isinstance(dt['SubFilas'], list):
        dt['SubFilas'] = _convertir_lista_a_tupla_recursivo(dt['SubFilas'])
    
    if 'FilasPlus' in dt and dt['FilasPlus'] and isinstance(dt['FilasPlus'], list):
        dt['FilasPlus'] = _convertir_lista_a_tupla_recursivo(dt['FilasPlus'])

def _convertir_lista_a_tupla_recursivo(lista):
    if not isinstance(lista, list):
        return lista
    
    resultado = []
    for item in lista:
        if isinstance(item, list):
            resultado.append(_convertir_lista_a_tupla_recursivo(item))
        else:
            resultado.append(item)
    
    return tuple(resultado)

def find_paginacion(RUTA_TABLA, idusuario, page = 0):
    col = db['paginacion_server']
    
    if page == 0:
        datos = list(col.find({"ruta_tabla": RUTA_TABLA, "idusuario": idusuario}))
        for dt in datos:
            _formatear_find_paginacion(dt)
    else:
        datos = col.find_one({"ruta_tabla": RUTA_TABLA, "idusuario": idusuario, "page": page})
        if datos:
            _formatear_find_paginacion(datos)
    
    return datos


def ensure_pagination_indexes():
    """Ensure that the required indexes exist in the pagination collection."""
    try:
        collection = db['paginacion_server']
        # Create compound index for the most common query pattern
        collection.create_index([("ruta_tabla", ASCENDING), 
                              ("idusuario", ASCENDING), 
                              ("page", ASCENDING)], 
                             name="pagination_query_idx")
        # Create individual indexes for flexibility
        collection.create_index("ruta_tabla", name="ruta_tabla_idx")
        collection.create_index("idusuario", name="idusuario_idx")
        collection.create_index("page", name="page_idx")
    except Exception as e:
        print(f"Error creating indexes: {str(e)}")

# Ensure indexes are created when the module is imported
ensure_pagination_indexes()

def insert_paginacion(RUTA_TABLA, datos, ps_idusuario, longitud_paginacion = 200, parametros_tabla: dict = {}, totales: dict = None):
    delete_paginacionRT(RUTA_TABLA)
    
    is_pagination_data = False
    if isinstance(parametros_tabla, dict):
        for key in parametros_tabla.keys():
            if isinstance(key, str) and key.startswith('ps_') or key in ['SubFilas', 'FilasPlus'] and parametros_tabla[key]:
                is_pagination_data = True
                break
    
    if is_pagination_data and isinstance(datos, list):
        data_list = datos
    elif isinstance(datos, list) and datos and not isinstance(datos[0], dict):
        data_list = [{"data": item} for item in datos]
    elif isinstance(datos, list) and datos and isinstance(datos[0], dict):
        data_list = datos
    elif not isinstance(datos, list):
        data_list = [{"data": datos}]
    else:
        data_list = []
    
    total_rows = len(data_list)
    
    num_chunks = (total_rows + longitud_paginacion - 1) // longitud_paginacion
    chunks = [
        data_list[i * longitud_paginacion:(i + 1) * longitud_paginacion]
        for i in range(num_chunks)
    ]
    
    shared_params = {
        "total_rows": total_rows,
        **parametros_tabla
    }
    collection = db['paginacion_server']
    for page_num, chunk_data in enumerate(chunks, 1):
        try:
            records = chunk_data if chunk_data else []
            doc = {
                "ruta_tabla": RUTA_TABLA,
                "idusuario": ps_idusuario,
                "paginas": records,
                "page": page_num,
                "total_conteo": shared_params['total_rows'],
                "parametros_tabla": shared_params
            }
            
            # Almacenar los totales calculados durante la carga inicial
            if totales:
                doc["totales"] = totales
                
            collection.insert_one(doc)
        except Exception as e:
            print(f"Error procesando página {page_num}: {str(e)}")
            raise

def delete_paginacion(RUTA_TABLA, ps_idusuario):
    col = db['paginacion_server']
    col.delete_many({"ruta_tabla": RUTA_TABLA, "idusuario": ps_idusuario})

def delete_paginacionRT(RUTA_TABLA):
    col = db['paginacion_server']
    col.delete_many({"ruta_tabla": RUTA_TABLA})