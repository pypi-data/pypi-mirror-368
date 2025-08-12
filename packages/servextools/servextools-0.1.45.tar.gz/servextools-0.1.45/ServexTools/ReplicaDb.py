from __future__ import annotations
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from typing import Mapping, Sequence, Any, Iterable, Union, Dict, Optional
from pymongo.client_session import ClientSession
from bson.raw_bson import RawBSONDocument
from pymongo.results import InsertManyResult, InsertOneResult, UpdateResult, DeleteResult
from pymongo.operations import _Pipeline
from ServexTools.EscribirLog import EscribirLog,Tools
from ServexTools.socket_manager import get_socketio
io=get_socketio()

EjecutoElHilo=False
ListaColasReplica=[]
class ReplicaCollection:
    global ListaColasReplica
    def __init__(self, conexion_local: MongoClient, conexion_replica: MongoClient, db_local: Database, db_replica: Database, col_local: Collection, col_replica: Collection) -> None:
        self.conexion_local = conexion_local
        self.conexion_replica = conexion_replica
        self.db_local = db_local
        self.db_replica = db_replica
        self.col_local = col_local
        self.col_replica = col_replica
        self._replica_thread: Optional[io.start_background_task] = None
        self.name = col_local.name if hasattr(col_local, 'name') else None
    
    def __getattr__(self, name: str) -> Any:
        if self.col_replica is not None:
            getattr(self.col_replica, name)
        return getattr(self.col_local, name)

    
    def _process_replica(self, func, args, kwargs):
        """Procesa las operaciones de replicación en cola"""
        try:
            try:
                
                Replic_data = {
                    'nombre_coleccion': self.col_local.name,
                    'accion': func.__name__ if hasattr(func, '__name__') else str(func),
                    'datos': {
                        'args': [],
                        'kwargs': {}
                    }
                }
                
                # Guardamos los argumentos
                for arg in args:
                    if isinstance(arg, dict):
                        Replic_data['datos']['args'].append(arg)
                    else:
                        Replic_data['datos']['args'].append(arg)
                
                # Guardamos los kwargs
                for k, v in kwargs.items():
                    if isinstance(v, dict):
                        Replic_data['datos']['kwargs'][k] = v
                    else:
                        Replic_data['datos']['kwargs'][k] = v
                
                result=self.db_local['colas_replica'].insert_one(Replic_data)    
                
                    
                # if args or kwargs:
                #     func(*args, **kwargs)
                # else:
                #     func() 
                        
                self.procesar_cola(result.inserted_id)
                self.sincronizar_datos()
            except Exception as ex:
                EscribirLog(f"Error en el hilo de replicación: {str(ex)}", "Error")
            
        except Exception as e:
            EscribirLog(f"Error en el hilo de replicación: {str(e)}", "Error")
    
    
    def _queue_replica_operation(self, func, *args, **kwargs):
        """Encola una operación de replicación"""
        self._replica_thread = io.start_background_task(self._process_replica, func, args, kwargs)
    
    def _convert_args(self, accion, args, kwargs):
        """Convierte los argumentos al tipo correcto según la operación"""
        converted_args = list(args)
        if accion in ['update_one', 'update_many', 'find_one', 'find', 'delete_one', 'delete_many']:
            if converted_args and len(converted_args) > 0:
                # Convertir el primer argumento (filtro) a diccionario si es necesario
                if isinstance(converted_args[0], str):
                    try:
                        converted_args[0] = eval(converted_args[0])
                    except:
                        print(f"Error al convertir filtro: {converted_args[0]}")
                        return None, None
                # Si hay un segundo argumento (update), también convertirlo
                if len(converted_args) > 1 and isinstance(converted_args[1], str):
                    try:
                        converted_args[1] = eval(converted_args[1])
                    except:
                        print(f"Error al convertir update: {converted_args[1]}")
                        return None, None
        
        # Convertir kwargs si es necesario
        converted_kwargs = {}
        for k, v in kwargs.items():
            if isinstance(v, str) and (v.startswith('{') or v.startswith('[')):
                try:
                    converted_kwargs[k] = eval(v)
                except:
                    print(f"Error al convertir kwarg {k}: {v}")
                    converted_kwargs[k] = v
            else:
                converted_kwargs[k] = v
        
        return converted_args, converted_kwargs

    def procesar_cola(self,_id):
        """Procesar las operaciones de cola"""
        if self.db_replica is None:
            return
            
        # Obtenemos todos los Datos de la cola
        DatosEnCola = self.db_local['colas_replica'].find_one({'_id': _id})
        
        try:
            # Obtenemos la acción y los datos
            accion = DatosEnCola['accion']
            nombre_coleccion = DatosEnCola['nombre_coleccion']
            args = DatosEnCola['datos']['args']
            kwargs = DatosEnCola['datos']['kwargs']
            
            # Convertir argumentos
            converted_args, converted_kwargs = self._convert_args(accion, args, kwargs)
            if converted_args is None:
                return
            
            # Obtenemos la colección de réplica correspondiente
            col_replica = self.db_replica[nombre_coleccion]
            
            # Ejecutamos la acción en la réplica
            func = getattr(col_replica, accion)
            func(*converted_args, **converted_kwargs)
            
            # Si la operación fue exitosa, eliminamos el registro de la cola
            self.db_local['colas_replica'].delete_one({'_id': DatosEnCola['_id']})
            
        except Exception as ex:
            EscribirLog(f"Error al procesar {accion} en {nombre_coleccion}: {str(ex)}", "Error")
            if str(ex).count("duplicate key error") == 0:
                    # Guardamos los datos originales de la operación
                    error_data = {
                        'nombre_coleccion': self.col_local.name,
                        'accion': func.__name__ if hasattr(func, '__name__') else str(func),
                        'datos': {
                            'args': [],
                            'kwargs': {}
                        },
                        'error': str(ex),
                        'fecha_error': Tools.FechaHora(),
                    }
                    
                    # Guardamos los argumentos
                    for arg in args:
                        if isinstance(arg, dict):
                            error_data['datos']['args'].append(arg)
                        else:
                            error_data['datos']['args'].append(arg)
                    
                    # Guardamos los kwargs
                    for k, v in kwargs.items():
                        if isinstance(v, dict):
                            error_data['datos']['kwargs'][k] = v
                        else:
                            error_data['datos']['kwargs'][k] = v
                    
                    self.db_local['errores_replica'].insert_one(error_data)
                    
            self.db_local['colas_replica'].delete_one({'_id': DatosEnCola['_id']})
    
    def sincronizar_datos(self):
        """Procesa los errores almacenados en la colección errores_replica"""
        if self.db_replica is None:
            return
            
        # Obtenemos todos los errores ordenados por fecha y acción
        errores = self.db_local['errores_replica'].find().sort([
            ('fecha_error', 1),
            ('accion', 1)
        ])
        
        for error in errores:
            try:
                # Obtenemos la acción y los datos
                accion = error['accion']
                nombre_coleccion = error['nombre_coleccion']
                args = error['datos']['args']
                kwargs = error['datos']['kwargs']
                
                # Convertir argumentos
                converted_args, converted_kwargs = self._convert_args(accion, args, kwargs)
                if converted_args is None:
                    continue
                
                # Obtenemos la colección de réplica correspondiente
                col_replica = self.db_replica[nombre_coleccion]
                
                # Ejecutamos la acción en la réplica
                func = getattr(col_replica, accion)
                func(*converted_args, **converted_kwargs)
                
                # Si la operación fue exitosa, eliminamos el error
                self.db_local['errores_replica'].delete_one({'_id': error['_id']})
                
            except Exception as ex:
                EscribirLog(f"Error al procesar {accion} en {nombre_coleccion}: {str(ex)}", "Error")
                if str(ex).count("duplicate key error") > 0:
                    self.db_local['errores_replica'].delete_one({'_id': error['_id']})
                continue
    
    def find(self, *args, **kwargs):
        return self.col_local.find(*args, **kwargs)
    
    def find_one(self, *args, **kwargs):
        return self.col_local.find_one(*args, **kwargs)
    
    def aggregate(self, *args, **kwargs):
        return self.col_local.aggregate(*args, **kwargs)
    
    def list_indexes(self):
        """Lista los índices de la colección local"""
        return self.col_local.list_indexes()
    
    def drop(self):
        """Elimina la colección local"""
        self.col_replica.drop()
        return self.col_local.drop()
    
    def insert_one(
        self,
        document: Any | RawBSONDocument,
        bypass_document_validation: bool = False,
        session: ClientSession | None = None,
        comment: Any | None = None
    ) -> InsertOneResult:
        result = self.col_local.insert_one(
            document,
            bypass_document_validation=bypass_document_validation,
            session=session, comment=comment
        )
        
        if self.col_replica is not None:
            replica_session = getattr(session, 'replica_session', None) if session else None
            self._queue_replica_operation(
                self.col_replica.insert_one,
                document,
                bypass_document_validation=bypass_document_validation,
                session=replica_session,
                comment=comment
            )
        return result

    def insert_many(
        self,
        documents: Iterable[Any | RawBSONDocument],
        ordered: bool = True,
        bypass_document_validation: bool = False,
        session: ClientSession | None = None,
        comment: Any | None = None
    ) -> InsertManyResult:
        result = self.col_local.insert_many(
            documents, ordered=ordered,
            bypass_document_validation=bypass_document_validation,
            session=session, comment=comment
        )
        try:
            if self.db_replica is not None:
                replica_session = getattr(session, 'replica_session', None) if session else None
                self._queue_replica_operation(
                    self.col_replica.insert_many,
                    documents,
                    ordered=ordered,
                    bypass_document_validation=bypass_document_validation,
                    session=replica_session,
                    comment=comment
                )
        except Exception as e:
            EscribirLog("Error Ermes: " + str(e))
        return result
        # if self.col_replica is not None:
        #     replica_session = getattr(session, 'replica_session', None) if session else None
        #     self._queue_replica_operation(
        #         self.col_replica.insert_many,
        #         documents,
        #         ordered=ordered,
        #         bypass_document_validation=bypass_document_validation,
        #         session=replica_session,
        #         comment=comment
        #     )
        # return result

    def update_one(
        self,
        filter: Mapping[str, Any],
        update: Mapping[str, Any] | _Pipeline,
        upsert: bool = False,
        bypass_document_validation: bool = False,
        collation = None,
        array_filters: Sequence[Mapping[str, Any]] | None = None,
        hint = None,
        session: ClientSession | None = None,
        let: Mapping[str, Any] | None = None,
        comment: Any | None = None
    ) -> UpdateResult:
        result = self.col_local.update_one(
            filter, update, upsert=upsert,
            bypass_document_validation=bypass_document_validation,
            collation=collation, array_filters=array_filters,
            hint=hint, session=session, let=let, comment=comment
        )
        
        if self.col_replica is not None:
            replica_session = getattr(session, 'replica_session', None) if session else None
            self._queue_replica_operation(
                self.col_replica.update_one,
                filter, update,
                upsert=upsert,
                bypass_document_validation=bypass_document_validation,
                collation=collation,
                array_filters=array_filters,
                hint=hint,
                session=replica_session,
                let=let,
                comment=comment
            )
        return result

    def update_many(
        self,
        filter: Mapping[str, Any],
        update: Mapping[str, Any] | _Pipeline,
        upsert: bool = False,
        array_filters: Sequence[Mapping[str, Any]] | None = None,
        bypass_document_validation: bool = False,
        collation = None,
        hint = None,
        session: ClientSession | None = None,
        let: Mapping[str, Any] | None = None,
        comment: Any | None = None
    ) -> UpdateResult:
        result = self.col_local.update_many(
            filter, update, upsert=upsert,
            array_filters=array_filters,
            bypass_document_validation=bypass_document_validation,
            collation=collation, hint=hint,
            session=session, let=let, comment=comment
        )
        
        if self.col_replica is not None:
            replica_session = getattr(session, 'replica_session', None) if session else None
            self._queue_replica_operation(
                self.col_replica.update_many,
                filter, update,
                upsert=upsert,
                array_filters=array_filters,
                bypass_document_validation=bypass_document_validation,
                collation=collation,
                hint=hint,
                session=replica_session,
                let=let,
                comment=comment
            )
        return result

    def delete_one(
        self,
        filter: Mapping[str, Any],
        collation = None,
        hint = None,
        session: ClientSession | None = None,
        let: Mapping[str, Any] | None = None,
        comment: Any | None = None
    ) -> DeleteResult:
        result = self.col_local.delete_one(
            filter, collation=collation,
            hint=hint, session=session,
            let=let, comment=comment
        )
        
        if self.col_replica is not None:
            replica_session = getattr(session, 'replica_session', None) if session else None
            self._queue_replica_operation(
                self.col_replica.delete_one,
                filter,
                collation=collation,
                hint=hint,
                session=replica_session,
                let=let,
                comment=comment
            )
        return result

    def delete_many(
        self,
        filter: Mapping[str, Any],
        collation = None,
        hint = None,
        session: ClientSession | None = None,
        let: Mapping[str, Any] | None = None,
        comment: Any | None = None
    ) -> DeleteResult:
        result = self.col_local.delete_many(
            filter, collation=collation,
            hint=hint, session=session,
            let=let, comment=comment
        )
        
        if self.col_replica is not None:
            replica_session = getattr(session, 'replica_session', None) if session else None
            self._queue_replica_operation(
                self.col_replica.delete_many,
                filter,
                collation=collation,
                hint=hint,
                session=replica_session,
                let=let,
                comment=comment
            )
        return result

    def create_index(self, keys, **kwargs):
        """
        Crea un índice en la colección local y lo replica en la colección remota
        """
        # Crear el índice en la colección local
        result = self.col_local.create_index(keys, **kwargs)
        
        # Si hay una conexión de réplica, crear el mismo índice allí
        if self.col_replica is not None:
            try:
                self.col_replica.create_index(keys, **kwargs)
            except Exception as ex:
                # Si falla por índice único duplicado, intentar sin la restricción única
                if 'unique' in kwargs and str(ex).count('unique'):
                    kwargs.pop('unique')
                    try:
                        self.col_replica.create_index(keys, **kwargs)
                    except Exception as e:
                        EscribirLog(f"Error al crear índice en réplica: {str(e)}", "Error")
                else:
                    EscribirLog(f"Error al crear índice en réplica: {str(ex)}", "Error")
        
        return result

    def create_indexes(self, indexes):
        """
        Crea múltiples índices en la colección local y los replica en la colección remota
        """
        # Crear índices en la colección local
        result = self.col_local.create_indexes(indexes)
        
        # Si hay una conexión de réplica, crear los mismos índices allí
        if self.col_replica is not None:
            try:
                self.col_replica.create_indexes(indexes)
            except Exception as ex:
                # Intentar crear los índices uno por uno en caso de error
                for index in indexes:
                    try:
                        self.col_replica.create_index(**index)
                    except Exception as e:
                        if 'unique' in index and str(e).count('unique'):
                            index.pop('unique')
                            try:
                                self.col_replica.create_index(**index)
                            except Exception as err:
                                EscribirLog(f"Error al crear índice en réplica: {str(err)}", "Error")
                        else:
                            EscribirLog(f"Error al crear índice en réplica: {str(e)}", "Error")
        
        return result

class ReplicaDB:
    def __init__(self, conexion_local: MongoClient, conexion_replica: MongoClient, db_local: Database, db_replica: Database) -> None:
        self.conexion_local = conexion_local
        self.conexion_replica = conexion_replica
        self.db_local = db_local
        self.db_replica = db_replica
        self.name = db_local.name if hasattr(db_local, 'name') else None
    
    def __getattr__(self, name: str) -> Any:
        return getattr(self.db_local, name)
    
    def list_collection_names(self):
        """Retorna los nombres de las colecciones en la base de datos local"""
        return self.db_local.list_collection_names()
    
    def __getitem__(self, name: str) -> ReplicaCollection:
        col_local = self.db_local[name]
        col_replica = self.db_replica[name] if self.db_replica is not None else None
        return ReplicaCollection(
            self.conexion_local, 
            self.conexion_replica, 
            self.db_local, 
            self.db_replica,
            col_local,
            col_replica
        )

class ReplicaCluster:
    def __init__(self, conexion_local: str, conexion_replica: str, 
                 local_kwargs: dict = None, replica_kwargs: dict = None, **kwargs) -> None:
        """
        Args:
            conexion_local: URI de conexión local
            conexion_replica: URI de conexión réplica
            local_kwargs: Configuración específica para conexión local
            replica_kwargs: Configuración específica para conexión réplica
            **kwargs: Configuración común para ambas conexiones si no se especifica local_kwargs o replica_kwargs
        """
        self.replica_db_name = conexion_replica.split('/')[-1].split('?')[0]
        
        self.conexion_local = MongoClient(conexion_local, **(local_kwargs or kwargs or {}))
        try:
            self.conexion_replica = MongoClient(conexion_replica, **(replica_kwargs or kwargs or {}))
        except Exception as ex:
            self.conexion_replica = None
    
    def __getattr__(self, name: str) -> Any:
        return getattr(self.conexion_local, name)
    
    def start_session(self):
        """
        Inicia una sesión en la conexión local y crea una sesión paralela para la réplica
        
        Returns:
            tuple: (sesión_local, sesión_réplica) - la sesión_réplica puede ser None si falla
        """
        session_local = self.conexion_local.start_session()
        session_replica = None
        
        if self.conexion_replica is not None:
            try:
                # Creamos una sesión con las mismas opciones que la local
                session_replica = self.conexion_replica.start_session(
                    causal_consistency=session_local.options.get('causal_consistency'),
                    default_transaction_options=session_local.options.get('default_transaction_options'),
                    snapshot=session_local.options.get('snapshot')
                )
            except Exception as ex:
                session_replica = None
        
        # Guardamos la referencia a la sesión réplica
        session_local.replica_session = session_replica
        return session_local

    def __getitem__(self, name: str) -> ReplicaDB:
        return ReplicaDB(self.conexion_local, self.conexion_replica, 
                        self.conexion_local[name], 
                        self.conexion_replica[self.replica_db_name] if self.conexion_replica is not None else None)
