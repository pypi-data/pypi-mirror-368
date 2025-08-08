import sqlite3
import jwt
from pymongo import MongoClient
from pymongo.collection import Collection
from ServexTools.ReplicaDb import ReplicaCluster
from bson.objectid import ObjectId
import pytz
import ServexTools.Tools as Tools
from bson.codec_options import CodecOptions
from pymongo.client_session import ClientSession
from flask import session as flaskSession
from typing import Optional

def Get(Coleccion,agregarzona=False):
    try:
        db,con= GetDB(agregarzona)
        if agregarzona==True:
            codec_options=CodecOptions(tz_aware=True,tzinfo=pytz.timezone('America/Santo_Domingo'))
            collection=db[Coleccion].with_options(codec_options)
        else:
            collection=db[Coleccion]
        return collection,con
    except Exception as ex:
        print("Error de conexion: {}".format(ex))
        return "",""

def GetDB(agregarzona=False):
    try:
        HOST,PASSWORD,USER,DATABASE,DATABASE_REPLICA,PORT,REPLICASET,TIMEOUT,DIRECTCONNNECTION = TypeConnection()
        Config={
            'serverSelectionTimeoutMS': TIMEOUT
        }
        if REPLICASET!="":
            Config.update({'replicaset':REPLICASET})
        if DIRECTCONNNECTION==True:
            Config.update({'directConnection':True})
        
        Replica=Tools.ReadFile('.Replica')=='True'
        if Replica:
                con=ReplicaCluster(f'mongodb://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}?authSource=admin',
                               f'mongodb://root:a123456-@38.253.88.210:{PORT}/{DATABASE_REPLICA}?authSource=admin',**Config)
        else:
            con=MongoClient(f'mongodb://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}?authSource=admin',**Config)
            
        if agregarzona==True:
            codec_options=CodecOptions(tz_aware=True,tzinfo=pytz.timezone('America/Santo_Domingo'))
            db = con[DATABASE].with_options(codec_options)
        else:
            db = con[DATABASE]
        return db,con
    except Exception as ex:
        print("Error de conexion: {}".format(ex))
        return "",""

def poner_historial(
    idcoleccion: int,
    accion: str,
    datos: dict,
    coleccion: Collection,
    idusuario: int,
    mongoDbSession: Optional[ClientSession] = None
):
    if accion == 'I':
        datos['_historial'] = [{
            '_idusuario': idusuario,
            '_accion': 'Registro',
            '_fechareg': Tools.FechaHora()
        }]
        return datos

    datos_antes = coleccion.find_one({idcoleccion: datos[idcoleccion]}, session = mongoDbSession)
    diferencia = {
        '_idusuario': idusuario,
        '_accion': 'Actualización',
        '_fechareg': Tools.FechaHora()
    }
    keys_antes = set(datos_antes.keys())
    keys_ahora = set(datos.keys())
    todos_los_keys = keys_antes | keys_ahora
    for k in todos_los_keys:
        dato_antes = datos_antes.get(k)
        dato_ahora = datos.get(k)
        if (dato_antes != dato_ahora) and (dato_ahora != Tools.NoActualizar()) and (k not in ['_historial', '_id', idcoleccion]):
            diferencia[k] = dato_ahora
    coleccion.update_one(
        {idcoleccion: datos[idcoleccion]},
        {'$push': {'_historial': diferencia}},
        session = mongoDbSession
    )
    return diferencia

def ProcesarDatos(
    Coleccion,
    args: dict,
    idcolecion = None,
    session = None,
    ColecionString = True,
    ReturnId = False,
    PonerHistorial = True
):
    try:
        idusuario = flaskSession['idusuario']
    except Exception:
        idusuario = 0
    if ColecionString:
        collection,client=Get(Coleccion)
    else:
        collection=Coleccion
    result=None
    Execcion=False
    try:
        _id=args['_id']
        args.pop('_id')
        id=ObjectId(str(_id))
    except Exception as ex:
        _id=None
    
    if _id is None:
        if idcolecion is not None:
            if  Tools.StrToInt(args[idcolecion])>0:
                raise Exception("La inserción del documento fue bloqueada por violación de la integridad de los datos.")
            
            try:
                idactual=collection.find_one({},sort=[(idcolecion, -1)],session=session)[idcolecion]
            except Exception as ex:
                idactual=0
                
            try:
                datos=args.copy()
                for quitar in datos:
                    if args[quitar]==Tools.NoActualizar():
                        args.pop(quitar)
            except Exception as ex:
                pass

            for id in range(1,101):
                try:
                    if idactual==0:
                        idinsertar=1
                        args.update({idcolecion:1})
                    else:
                        idinsertar=idactual+id
                        args.update({idcolecion:idinsertar})
                    if PonerHistorial:
                        copia_de_args = args.copy()
                        args = poner_historial(
                            idcolecion,
                            'I',
                            copia_de_args,
                            collection,
                            idusuario,
                            session,
                        )
                    result=collection.insert_one(document=args,session=session)
                    Execcion=False
                    idactual=idinsertar
                    break
                except Exception as ex:
                    Execcion=True
                    result=ex
                    if str(ex).count("Timeout")>0:
                        raise Exception("Tiempo de espera excedido. "+str(ex))        
        else:
            raise Exception("IdColeccion no especificado al procesar datos.")
    else:
        copia_de_args = args.copy()
        try:
            if idcolecion is None:
                raise Exception("IdColeccion no especificado.")
            if  Tools.StrToInt(args[idcolecion])==0:
                raise Exception("La actualización del documento fue bloqueada por violación de la integridad de los datos.")
            idactual=args[idcolecion]
            args.pop(idcolecion)
        except Exception as ex:
            pass
        
        try:
            datos=args.copy()
            for quitar in datos:
                if args[quitar]==Tools.NoActualizar():
                    args.pop(quitar)
        except Exception as ex:
            pass
        try:
            #if idcolecion
            if PonerHistorial:
                poner_historial(
                    idcolecion,
                    'U',
                    copia_de_args,
                    collection,
                    idusuario,
                    session
                )
            result=collection.update_one(filter={'_id':ObjectId(str(_id))},update={'$set':args},session=session)
            Execcion=False
        except Exception as ex:
            Execcion=True
            result=ex
            if str(ex).count("Timeout")>0:
                raise Exception("Tiempo de espera excedido. "+str(ex))
    
    if Execcion==True:
        raise Exception(str(result))
    if ReturnId:
        return result,idactual
    return result

def ProcesarDatosPRG(
    Coleccion: Collection,
    args: dict,
    idcolecion = None,
    session = None,
    PonerHistorial = True
):
    try:
        idusuario = flaskSession['idusuario']
    except Exception:
        idusuario = 0
    collection=Coleccion
    result=None
    Execcion=False
    idactual=0
    try:
        _id=args['_id']
        args.pop('_id')
        id=ObjectId(str(_id))
    except Exception as ex:
        _id=None
    
    if _id is None:
        if idcolecion is not None:
            if  Tools.StrToInt(args[idcolecion])>0:
                raise Exception("La inserción del documento fue bloqueada por violación de la integridad de los datos.")
            
            try:
                idactual=collection.find_one({},sort=[(idcolecion, -1)],session=session)[idcolecion]*(-1)
            except Exception as ex:
                idactual=0
                
            try:
                datos=args.copy()
                for quitar in datos:
                    if args[quitar]==Tools.NoActualizar():
                        args.pop(quitar)
            except Exception as ex:
                pass

            for id in range(1,101):
                try:
                    calculo=idactual+(id*(-1))
                    if idactual==0 or calculo==0:
                        args.update({idcolecion:id*(-1)})
                        idactual=id*(-1)
                    else:
                        args.update({idcolecion:idactual+(id*(-1))})
                        idactual=idactual+(id*(-1))
                    
                    args.update({"hora":Tools.OptenerHora(Tools.FechaHora(),True,True)})
                    if PonerHistorial:
                        copia_de_args = args.copy()
                        args = poner_historial(
                            idcolecion,
                            'I',
                            copia_de_args,
                            collection,
                            idusuario,
                            session
                        )
                    result=collection.insert_one(document=args,session=session)
                    Execcion=False
                    break
                except Exception as ex:
                    Execcion=True
                    result=ex
                    if str(ex).count("Timeout")>0:
                        raise Exception("Tiempo de espera excedido. "+str(ex))
        else:
            raise Exception("IdColeccion no especificado al procesar datos.")
            
    else:
        copia_de_args = args.copy()
        if idcolecion is None:
            raise Exception("IdColeccion no especificado.")
        if  Tools.StrToInt(args[idcolecion])==0:
            raise Exception("La actualización del documento fue bloqueada por violación de la integridad de los datos.")
        
        try:
            datos=args.copy()
            for quitar in datos:
                if args[quitar]==Tools.NoActualizar():
                    args.pop(quitar)
        except Exception as ex:
            pass

        # LOS DOCUMENTOS QUE FUERON PRE REGISTRADOS SE LES ASIGNÓ UN NUMERO EN NEGATIVO
        if args[idcolecion]<=0:
            #idactual=collection.find_one({},sort=[(idcolecion, -1)],session=session)[idcolecion]
            idactual=args[idcolecion]
            idactual=abs(idactual)
            for id in range(0,1000):
                try:
                    args.update({idcolecion:idactual+id})
                    idinsertar=idactual+id
                    if PonerHistorial:
                        poner_historial(
                            idcolecion,
                            'U',
                            copia_de_args,
                            collection,
                            idusuario,
                            session
                        )
                    result=collection.update_one(filter={'_id':ObjectId(str(_id))},update={'$set':args},session=session)
                    Execcion=False
                    idactual=idinsertar
                    break
                except Exception as ex:
                    Execcion=True
                    result=ex
        else:
            try:
                if args[idcolecion]>0:
                    idactual=Tools.StrToInt(args[idcolecion])
                    args.pop(idcolecion)
                if PonerHistorial:
                    poner_historial(
                        idcolecion,
                        'U',
                        copia_de_args,
                        collection,
                        idusuario,
                        session
                    )
                result=collection.update_one(filter={'_id':ObjectId(str(_id))},update={'$set':args},session=session)
                Execcion=False
            except Exception as ex:
                Execcion=True
                result=ex
                if str(ex).count("Timeout")>0:
                    raise Exception("Tiempo de espera excedido. "+str(ex))
    
    if Execcion==True:
        raise Exception(str(result))
    return result,idactual
    
def GetTestConexionMongo():
    msj="Exito"
    conectado=True
    try:
        db,con=GetDB()
        con.admin.command('ping')
        return msj,conectado
    except Exception as ex:
        print("Error de conexion: {}".format(ex))
        msj=str(ex)
        conectado=False
        return msj,conectado


def CallProced(NameProc,prm=None,dicionario=False):
    pass

def TypeConnection():
    try:
        cadenaconexion=ExecuteSQLite("SELECT cadena FROM conexion;")[0]
        cadenaconexion=cadenaconexion['cadena']
        conncadena=jwt.decode(cadenaconexion, "Ijusneed", algorithm="HS256")
        HOST=conncadena['SERVIDOR']
        PASSWORD=conncadena['PASSWORD']
        USER=conncadena['USER']
        DATABASE=conncadena['DATABASE']
        DATABASE_REPLICA=conncadena['DATABASE_REPLICA']
        PORT=conncadena['PORT']
        REPLICASET=conncadena['REPLICASET']
        TIMEOUT=conncadena['TIMEOUT']
        DIRECTCONNNECTION=conncadena['DIRECTCONNNECTION']
    except Exception as e:
            pass

    return HOST,PASSWORD,USER,DATABASE,DATABASE_REPLICA,PORT,REPLICASET,TIMEOUT,DIRECTCONNNECTION

#***************CONEXION SQLITE****************
def GetSQLite():
    conn = sqlite3.connect(Tools.OptenerRutaApp()+"conexion.db")
    conn.row_factory = sqlite3.Row
    curs=conn.cursor()
    return curs,conn

def ExecuteSQLite(query, args=()):
    cur,conn = GetSQLite()
    cur.execute(query, args)
    rv = cur.fetchall()
    result=Tools.IterarDatosSQliteToList(rv)
    cur.close()
    #return (rv[0] if rv else None) if one else rv
    return result

def create_database():
    db=Tools.OptenerRutaApp()+"conexion.db"
    if Tools.ExistFile(db):
        Tools.DeleteFile(db)
        
    conn = sqlite3.connect(db)
    c = conn.cursor()

    script = """

        CREATE TABLE IF NOT EXISTS conexion(
            idconexion INTEGER PRIMARY KEY AUTOINCREMENT,
            cadena TEXT
        );

        /* INSERTS */
  
        INSERT INTO conexion(idconexion, cadena)
            VALUES (1, "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJTRVJWSURPUiI6ImxvY2FsaG9zdCIsIlBBU1NXT1JEIjoiYTEyMzQ1Ni0iLCJVU0VSIjoicm9vdCIsIkRBVEFCQVNFIjoiZGJjZ3ZlbnRhcyIsIlBPUlQiOiIyNzAxNyJ9.0r14AQMiz-BAyVHbrjZUcNLV8bI4GogZuazTN3rqQio");

    """

    try:
        # execute script
        c.executescript(script)
        print("Base de datos creada con exito")

    except Exception as e:
        print(("Error: {}".format(e)))
        conn.rollback()

    finally:
        conn.close()
#***************CONEXION SQLITE****************