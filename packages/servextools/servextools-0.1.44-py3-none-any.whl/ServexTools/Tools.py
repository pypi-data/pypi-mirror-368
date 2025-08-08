import base64
import inspect
import json
import math
import os
from datetime import datetime,timedelta
import platform
import shutil
import time
import uuid
from zipfile import ZipFile
import pytz
import jwt
from flask import Request
import locale
import typing as t
import httpx
from ServexTools.Enumerable import TipoMensaje,Metodo
from shutil import rmtree
import re

def OptenerRutaApp():
    if not ExistFile('.raiz'):
        urlServicio=os.path.dirname(os.path.abspath(__file__))+"/"
        CreateFile('.raiz',urlServicio)

    if ReadFile(".raiz").count("\n"):
        Ruta=ReadFile(".raiz").replace('\n','/')
    else:
        Ruta=ReadFile(".raiz")+'/'
    return Ruta


def AgregarActualizarCampo(coleccion, nombrecampo, defaultval = '',conexion=None):
    try:
        db,client=conexion.GetDB()
        print('Agregando campo: { "'+str(nombrecampo)+'": "'+str(defaultval)+'" }')
        coll = db[coleccion]
        coll.update_many({}, {'$set': {nombrecampo: defaultval}})
    except Exception as e:
        EscribirLog("Error En "+inspect.stack()[0][3]+": "+str(e))
        return False,0
    
def AgregarActualizarCampoEnArray(coleccion, nombrecampo, valor, campoArray,conexion=None):
    try:
        db, client = conexion.GetDB()
        print(f'Agregando campo en array: {{ "{nombrecampo}": "{valor}" }}')
        coll = db[coleccion]
        
        # Primero, actualiza los documentos que tienen el campo
        result = coll.update_many(
            {campoArray: {"$exists": True}},
            [
                {
                    "$set": {
                        campoArray: {
                            "$map": {
                                "input": f"${campoArray}",
                                "in": {
                                    "$mergeObjects": [
                                        "$$this",
                                        {nombrecampo: valor}
                                    ]
                                }
                            }
                        }
                    }
                }
            ]
        )
        
        print(f"Documentos actualizados: {result.modified_count}")
        return True
        
    except Exception as e:
        EscribirLog("Error En " + inspect.stack()[0][3] + ": " + str(e))
        return False

def RegistrarAreas(nombre, archivo, visiblepara = 'T',conexion=None):
    try:
        conexion.ProcesarDatos('areas', {'_id': '0', 'idarea': 0, 'nombre':nombre,'archivo':archivo,'estatus':'A','visiblepara':visiblepara}, 'idarea')
    except Exception as e:
        EscribirLog("Error En "+inspect.stack()[0][3]+": "+str(e))
        return False,0

def EliminarArea(nombre,conexion=None):
    try:
        db,client=conexion.GetDB()
        coll = db['areas']
        coll.find_one_and_delete({'nombre':nombre})
    except Exception as e:
        EscribirLog("Error En "+inspect.stack()[0][3]+": "+str(e))
        return False,0

def CambiarNombreCampo(coleccion, nombrecampo, newnombre, esArray=False, campoArray=None,conexion=None):
    try:
        db, client = conexion.GetDB()
        coll = db[coleccion]

        if esArray and campoArray:
            print(f'Renombrando el campo {nombrecampo} => {newnombre} dentro del array {campoArray}')

            # Pipeline de actualización que renombra el campo dentro del arreglo
            pipeline = [
                {
                    "$set": {
                        campoArray: {
                            "$map": {
                                "input": f"${campoArray}",
                                "as": "item",
                                "in": {
                                    "$mergeObjects": [
                                        {
                                            "$arrayToObject": {
                                                "$filter": {
                                                    "input": {"$objectToArray": "$$item"},
                                                    "cond": {
                                                        "$ne": ["$$this.k", nombrecampo]
                                                    }
                                                }
                                            }
                                        },
                                        {
                                            newnombre: f"$$item.{nombrecampo}"
                                        }
                                    ]
                                }
                            }
                        }
                    }
                }
            ]

            # Ejecutar la actualización y obtener resultado
            result = coll.update_many({}, pipeline)

            print(f"Documentos modificados: {result.modified_count}")

        else:
            print(f'Renombrando campo normal {nombrecampo} => {newnombre}')
            result = coll.update_many({}, {'$rename': {nombrecampo: newnombre}})
            print(f"Documentos modificados: {result.modified_count}")

        return True
    except Exception as e:
        error_msg = f"Error En {inspect.stack()[0][3]}: {str(e)}"
        print(error_msg)
        EscribirLog(error_msg)
        return False

def CambiarNombreColeccion(coleccion, newnombre,conexion=None):
    try:
        db,client=conexion.GetDB()
        coll = db[coleccion]
        print(f'Renombrando coleccion ({coleccion} a {newnombre})')
        coll.rename(newnombre)
    except Exception as e:
        EscribirLog("Error En "+inspect.stack()[0][3]+": "+str(e))
        return False,0

def EliminarIndexColeccion(coleccion, nombreIndex,conexion=None):
    try:
        db,client=conexion.GetDB()
        coll = db[coleccion]
        print(f'Eliminando index ({nombreIndex}) de la coleccion ({coleccion})')
        coll.drop_index(nombreIndex)
    except Exception as e:
        EscribirLog("Error En "+inspect.stack()[0][3]+": "+str(e))
        return False,0

def EliminarColeccion(coleccion,conexion=None):
    try:
        db,client=conexion.GetDB()
        coll = db[coleccion]
        print(f'Eliminando la coleccion ({coleccion})')
        coll.drop()
    except Exception as e:
        EscribirLog("Error En "+inspect.stack()[0][3]+": "+str(e))
        return False,0

def CrearIndexColeccion(coleccion,nombreCampo, nombreIndex,unico=True,conexion=None):
    try:
        db,client=conexion.GetDB()
        coll = db[coleccion]
        print(f'Creando index ({nombreIndex}) en la coleccion ({coleccion})')
        if type(nombreCampo) == list:
            coll.create_index(nombreCampo, unique=unico, name=nombreIndex)
        else:
            coll.create_index([(nombreCampo,1)],unique=unico, name=nombreIndex)
    except Exception as e:
        EscribirLog("Error En "+inspect.stack()[0][3]+": "+str(e))
        return False,0

def FormatearValor(valor):
    formato=type(valor).__name__
    if formato=='Decimal':
        result=StrToFloat(str(valor))
    return result

def ProcesarDetalle(detalle,completar=True,calcular=True):
    dtDetalle=detalle
    detalle=[]
    detalleEliminar=[]
    TotalGeneral=0.0
    for deta in dtDetalle:
        if deta['estatus']!='E':
            if completar==True:
                deta['estatus']='C'
            detalle.append(deta)
            if calcular==True:
                TotalGeneral+=deta['total']
        else:
            detalleEliminar.append(deta)
    return detalle,detalleEliminar,TotalGeneral

def FormatearDatos(args:dict,ComposNoFormatear:t.Union[list,None]=None):
    try:
        JsonQuitados={}
        for deletCamp in ComposNoFormatear:
            valor=args[deletCamp]
            JsonQuitados.update({deletCamp:valor})
            args.pop(deletCamp)
    except Exception as ex:
        pass
    campos=args.keys()
    for camp in campos:
        valor=args[camp]
        if valor==None:
            args[camp]=''
        formato=type(valor).__name__
        if formato=='Decimal':
            result=StrToFloat(str(valor))
            args.update({camp:result})
        elif formato=='date':
            result=StrToDateAmerican(valor)
            args.update({camp:result})
    if JsonQuitados is not {}:
        args.update(JsonQuitados)
    return args

def OptenerFechaArchivo(rutaArchivo):
    try:
        date_format = "%Y-%m-%d"
        time_format = "%H:%M:%S"
        screados=os.path.getctime(rutaArchivo)
        time_val = time.localtime(screados)
        fechastrin=time.strftime(date_format+" "+time_format,time_val)
        return StrToDateTimeAmerican(fechastrin)
        # fecha=StrToDateTime(fechastrin)
        # return fecha
    except Exception as e:
        EscribirLog("Error En "+inspect.stack()[0][3]+": "+str(e))
        return StrToDate(rutaArchivo)

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return s, size_name[i]

def DateToNombre(dato:datetime):
    """PARA CONVERTIR DE STRING A FECHA FORMATO DEVUELTO(dia/mes/año)"""
    try:
        if platform.system()=='Linux':
            locale.setlocale(locale.LC_TIME, 'es_DO.utf8')
        if platform.system()=='Darwin':
            locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        date_format = '%A %d %B'
        formato=dato.strftime(date_format)
        return formato
    except Exception as e:
       EscribirLog("Error En "+inspect.stack()[0][3]+": "+str(e))

def ObtenerNombreMesPorNumero(mes):
    try:
        mesnombre = ''
        meses = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
        try:
            mesnombre = meses[mes - 1]
        except:
            mesnombre = "TODOS"
        return mesnombre
    except Exception as e:
       EscribirLog("Error En "+inspect.stack()[0][3]+": "+str(e))

def StrToDate(dato,AddDias=0.0,AddHoras=0.0,AddMinutos=0.0,AddSegundo=0.0):
    """PARA CONVERTIR DE STRING A FECHA FORMATO DEVUELTO(dia/mes/año)"""

    date_format = "%d/%m/%Y"
    try:
        formato=datetime.strptime(str(dato), date_format)+timedelta(days=AddDias,hours=AddHoras,minutes=AddMinutos,seconds=AddSegundo)
        return formato
    except Exception as e:
        EscribirLog("Error En "+inspect.stack()[0][3]+": "+str(e))
        formato=datetime.strptime(Fecha(), date_format)+timedelta(days=AddDias,hours=AddHoras,minutes=AddMinutos,seconds=AddSegundo)
        return formato

def StrDateDomToAmerican(dato,hora="",FechaDivisor="/"):
    """PARA CONVERTIR STRING DE FECHA CON FORMATO (dia/mes/año) A (año-mes-dia)\n
    PARA LA FECHA CON HORA SE RECIBE EL FORMATO (dia/mes/año H:M:S PM o AM) TAMBIEN SE ADMITE HORA EN FORMATO DE 24 HORA
    Y SE RETORTA (año-mes-dia H:M:S) EN UN DATETIME
    """
    try:
        formato=str(dato).split(FechaDivisor)
        if hora!="":
            horaDom=False
            listaAMPM=['AM','am','PM','pm']
            for dth in listaAMPM:
                if hora.count(dth):
                    horaDom=True
                    SpliH=hora.split(' ')
                    PM_pm=SpliH[1]
                    hora=SpliH[0]
                    hora=hora.split(':')
                    H=StrToInt(hora[0])
                    if PM_pm=="pm" or dth=="PM":
                        H=12+StrToInt(hora[0])

                    if (PM_pm=="am" or dth=="AM") and H==12:
                            H=0
                    M=StrToInt(hora[1])
                    S=StrToInt(hora[2])

                    break
            if horaDom==False:
                hora=hora.split(':')
                H=StrToInt(hora[0])
                M=StrToInt(hora[1])
                S=StrToInt(hora[2])

        year=StrToInt(formato[2])
        mes=StrToInt(formato[1])
        dia=StrToInt(formato[0])
        if hora!="":
            return datetime(year=year,month=mes,day=dia,hour=H,minute=M,second=S)
        else:
            return datetime(year=year,month=mes,day=dia,hour=0,minute=0,second=0)
    except Exception as e:
        EscribirLog("Error En "+inspect.stack()[0][3]+": "+str(e))
        raise Exception("Error En "+inspect.stack()[0][3]+": "+str(e))


def StrToDateAmerican(dato,AddDias=0.0,AddHoras=0.0,AddMinutos=0.0,AddSegundo=0.0):
    """PARA CONVERTIR DE STRING A FECHA FORMATO DEVUELTO(año-mes-dia)"""
    try:
        date_format = "%Y-%m-%d"
        formato=datetime.strptime(str(dato), date_format)+timedelta(days=AddDias,hours=AddHoras,minutes=AddMinutos,seconds=AddSegundo)
        return formato
    except Exception as e:
        EscribirLog("Error En "+inspect.stack()[0][3]+": "+str(e))
        #return DateTimeFormat(dato)

def StrToDateTime(dato,AddDias=0.0,AddHoras=0.0,AddMinutos=0.0,AddSegundo=0.0):
    date_format = "%d/%m/%Y"
    time_format = "%I:%M:%S %p"
    try:
        return datetime.strptime(str(dato), date_format+" "+time_format)+timedelta(days=AddDias,hours=AddHoras,minutes=AddMinutos,seconds=AddSegundo)
    except Exception as e:
        EscribirLog("Error En "+inspect.stack()[0][3]+": "+str(e))
        hora=Hora()
        try:
            hora = str(dato).split(' ')
            hora=hora[1]+' '+hora[2]
        except Exception as e:
            EscribirLog("Error En "+inspect.stack()[0][3]+": "+str(e))
        return datetime.strptime(Fecha()+" "+hora, date_format+" "+time_format)+timedelta(days=AddDias,hours=AddHoras,minutes=AddMinutos,seconds=AddSegundo)

def StrToDateTimeAmerican(dato,AddDias=0.0,AddHoras=0.0,AddMinutos=0.0,AddSegundo=0.0):
    try:
        date_format = "%Y-%m-%d"
        time_format = "%H:%M:%S"
        fecha=str(dato)
        if fecha.count("."):
            fecha=fecha.split('.')
            fecha=fecha[0]

        return datetime.strptime(fecha, date_format+" "+time_format)+timedelta(days=AddDias,hours=AddHoras,minutes=AddMinutos,seconds=AddSegundo)
    except Exception as e:
        EscribirLog("Error En "+inspect.stack()[0][3]+": "+str(e))
        return StrToDateAmerican(dato)

def DateFormat(dato,AddDias=0.0,AddHoras=0.0,AddMinutos=0.0,AddSegundo=0.0):
    try:
        date_format = "%d/%m/%Y"
        formato=datetime.strftime(dato, date_format)
        if AddDias!=0 or AddHoras!=0 or AddMinutos!=0 or AddSegundo!=0:
           formato=datetime.strptime(str(formato), date_format)+timedelta(days=AddDias,hours=AddHoras,minutes=AddMinutos,seconds=AddSegundo)
           formato=datetime.strftime(formato, date_format)
        return formato
    except Exception as e:
        EscribirLog("Error En "+inspect.stack()[0][3]+": "+str(e))
        return Fecha()

def DateFormatAmerican(dato,AddDias=0.0,AddHoras=0.0,AddMinutos=0.0,AddSegundo=0.0):
    try:
        date_format = "%Y-%m-%d"
        formato=datetime.strftime(dato, date_format)
        if AddDias!=0 or AddHoras!=0 or AddMinutos!=0 or AddSegundo!=0:
           formato=datetime.strptime(str(formato), date_format)+timedelta(days=AddDias,hours=AddHoras,minutes=AddMinutos,seconds=AddSegundo)
           formato=datetime.strftime(formato, date_format)
        return formato
    except Exception as e:
        EscribirLog("Error En "+inspect.stack()[0][3]+": "+str(e))
        return "__/__/____"

def DateTimeFormat(dato,AddDias=0.0,AddHoras=0.0,AddMinutos=0.0,AddSegundo=0.0,incluirSegundos=False):
    try:
        date_format = "%d/%m/%Y"
        time_format = "%I:%M %p" if incluirSegundos==False else "%I:%M:%S %p"
        formato=datetime.strftime(dato, date_format+" "+time_format)
        if AddDias!=0 or AddHoras!=0 or AddMinutos!=0 or AddSegundo!=0:
           formato=datetime.strptime(str(formato), date_format+" "+time_format)+timedelta(days=AddDias,hours=AddHoras,minutes=AddMinutos,seconds=AddSegundo)
           formato=datetime.strftime(formato, date_format+" "+time_format)
        return formato
    except Exception as e:
        EscribirLog("Error En "+inspect.stack()[0][3]+": "+str(e))
        return DateFormat(dato)

def DateTimeFormatAmerican(dato,AddDias=0.0,AddHoras=0.0,AddMinutos=0.0,AddSegundo=0.0):
    try:
        date_format = "%Y-%m-%d"
        time_format = "%H:%M:%S"
        formato=datetime.strftime(dato, date_format+" "+time_format)
        if AddDias!=0 or AddHoras!=0 or AddMinutos!=0 or AddSegundo!=0:
           formato=datetime.strptime(str(formato), date_format+" "+time_format)+timedelta(days=AddDias,hours=AddHoras,minutes=AddMinutos,seconds=AddSegundo)
           formato=datetime.strftime(formato, date_format+" "+time_format)
        return formato
    except Exception as e:
        EscribirLog("Error En "+inspect.stack()[0][3]+": "+str(e))
        return DateFormat(dato)

def DateTimeAdd_D_H_M_S(dato:datetime,AddDias=0.0,AddHoras=0.0,AddMinutos=0.0,AddSegundo=0.0):
    try:
        date_format = "%Y-%m-%d"
        time_format = "%H:%M:%S"
        fecha=str(dato)
        if fecha.count("."):
            fecha=fecha.split('.')
            fecha=fecha[0]
        formato=datetime.strptime(fecha, date_format+" "+time_format)+timedelta(days=AddDias,hours=AddHoras,minutes=AddMinutos,seconds=AddSegundo)
        return formato
    except Exception as e:
        EscribirLog("Error En "+inspect.stack()[0][3]+": "+str(e))
        return DateFormat(dato)

def OptenerHora(dato,incluirSegundos=False,Formato24h=False):
    try:
        tipoDato=type(dato)
        date_format = "%d/%m/%Y"

        time_format = "%I:%M %p" if incluirSegundos==False else "%I:%M:%S %p"
        if Formato24h:
            time_format = "%H:%M" if incluirSegundos==False else "%H:%M:%S"

        if tipoDato==datetime:
            formato=datetime.strftime(dato,time_format)
        if tipoDato==str:
            formato = datetime.strptime(dato,date_format+" "+time_format)
            formato=datetime.strftime(formato,time_format)


        return formato
    except Exception as e:
        EscribirLog("Error En "+inspect.stack()[0][3]+": "+str(e))
        return DateFormat(dato)

def OptenerFecha(dato,incluirSegundos=False,Formato24h=False):
    try:
        tipoDato=type(dato)
        date_format = "%d/%m/%Y"
        time_format = "%I:%M %p" if incluirSegundos==False else "%I:%M:%S %p"
        if Formato24h:
            date_format = "%Y-%m-%d"
            time_format = "%H:%M" if incluirSegundos==False else "%H:%M:%S"
        if tipoDato==datetime:
            formato=datetime.strftime(dato,date_format)
        if tipoDato==str:
            formato = datetime.strptime(dato,date_format+" "+time_format)
            formato=datetime.strftime(formato,date_format)


        return formato
    except Exception as e:
        EscribirLog("Error En "+inspect.stack()[0][3]+": "+str(e))
        return DateFormat(dato)

def FormatoMoneda(dato):
    try:
        if platform.system()=='Linux':
            locale.setlocale(locale.LC_MONETARY, 'es_DO.utf8')
        if platform.system()=='Darwin':
            locale.setlocale(locale.LC_MONETARY, 'en_US.UTF-8')
        formato=locale.currency(StrToFloat(dato), symbol=False, grouping=True, international=False)
        return formato
    except Exception as e:
        EscribirLog("Error En FormatoMoneda: "+str(e))
        return dato

def StrToInt(dato):
    try:
        result=int(dato)
        return result
    except Exception as e:
        return 0

def StrToByte(dato):
    try:
        result=bytes(dato)
        return result
    except Exception as e:
        return 0

def TiempoEspera(tiempo, IsGevent=False):
    """## Permite esperar un tiempo (float o int) y verifica periódicamente si existe el archivo .kill para salir inmediatamente."""
    import time
    check_interval = 0.01  # Intervalo de verificación en segundos
    elapsed = 0.0
    while elapsed < tiempo:
        if ExistFile('.kill'):
            os._exit(1)
        sleep_time = min(check_interval, tiempo - elapsed)
        if IsGevent:
            import gevent
            gevent.sleep(sleep_time)
        else:
            time.sleep(sleep_time)
        elapsed += sleep_time

def IterarDatos(dato):
    try:
        for v in dato:
            return v
    except Exception as e:
        return "Error"

def IterarDatosToList(dato,campoValid:t.Union[bool,str]=False,DatoValid:t.Union[bool,str,int,float,datetime]=False,Simbolo:t.Union[bool,str]=False):
    try:
        lista=[]
        for v in dato:
            if campoValid==False:
                lista.append(v)
            else:
                if Simbolo=="=":
                    if v[campoValid]==DatoValid:
                        lista.append(v)
                elif Simbolo==">":
                    if v[campoValid]>DatoValid:
                        lista.append(v)
                elif Simbolo==">=":
                    if v[campoValid]>=DatoValid:
                        lista.append(v)
                elif Simbolo=="<":
                    if v[campoValid]<DatoValid:
                        lista.append(v)
                elif Simbolo=="<=":
                    if v[campoValid]<=DatoValid:
                        lista.append(v)
                elif Simbolo=="!=":
                    if v[campoValid]!=DatoValid:
                        lista.append(v)


        return lista
    except Exception as e:
        return "Error"

def OptenerDatos(request:Request,remplazar=True):
    try:
        datos=request.get_json()['data']
        try:
            datos=json.loads(datos)
        except Exception as e:
            datos=datos
        if remplazar==True:
            for quitar in datos:
                if str(datos[quitar]).count("<stln>"):
                    datos[quitar]=str(datos[quitar]).replace("<stln>","\n")
        return dict(datos)
    except Exception as e:
        return str(e)
    
def escapar_regex(expresion):
    """
    Valida si una cadena tiene caracteres especiales de regex y los escapa.
    
    Args:
        expresion (str): La cadena a procesar.
    
    Returns:
        str: La expresión con los caracteres especiales escapados.
    """
    return re.escape(expresion)

def FormarOptionDdl(valor,nombre):
    try:
        return "<option value='"+str(valor)+"'>"+nombre+"</option>"
    except Exception as e:
        return 0

def NoActualizar():
    return "ELIMINAR"

def EjecutarComando(comando,clavesudo, opciones=[]):
    try:
        import subprocess
        import shlex
        
        # Parsear el comando manteniendo las comillas
        command = shlex.split(comando)
        if command[0] == 'sudo':
            command = command[1:]  # Remover sudo si está presente

        if platform.system() == 'Darwin':
            process = subprocess.Popen(
                ['sudo', '-S'] + command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        else:
            process = subprocess.Popen(
                ['/usr/bin/sudo', '-S'] + command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

        process.stdin.write(clavesudo + "\n")

        if opciones:
            for op in opciones:
                process.stdin.write(op + "\n")

        stdout, stderr = process.communicate()
        return stdout, stderr
        
    except Exception as e:
        EscribirLog("Error En EjecutarComando: " + str(e))
        return "Error EjecutarComando:" + str(e)

def Mensaje(iddatos=0,estatus='Exito',mensaje=None, JsonUpdate:t.Union[dict, bool]=False, tipomensaje: t.Union[TipoMensaje, TipoMensaje]=TipoMensaje.MSJ,AutoCerrarAlerta=True):
    """PARA MOSTRAR UN MENSAJE DE MODIFICACION ES OBLIGATORIO EL ID DEL DOCUMENTO.\n
PARA MOSTRAR UN MENSAJE DE ERROR ES NECESARIO ENVIAR EL PARAMETRO \n
PARA MOSTRAR UN MENSAJE EN FORMATO ALERTA ES NECESARIO ENVIAR EL PARAMETRO tipomensaje \n
estatus=Error,\n mensaje=MENSAJE A MOSTRAR.
    """
    msj= mensaje if mensaje is not None else 'Registro guardado con exito!.' if iddatos<=0 else 'Registro modificado con exito!.'
    Resp={'Estatus':estatus,'mensaje':msj,'ismodic':False if iddatos<=0 else True, 'Mostrar': tipomensaje,'AutoCerrar':AutoCerrarAlerta}
    if JsonUpdate!=False:
        Resp.update(JsonUpdate)

    return Resp

def MensajeV2(iddatos = 0, estatus = 'Exito', mensaje = None, tipomensaje: t.Union[TipoMensaje, TipoMensaje] = TipoMensaje.MSJ, AutoCerrarAlerta = True, e: Exception = None, **JsonUpdate):
    if e is not None:
        estatus = 'Error'
    if estatus != 'Exito':
        funcion = JsonUpdate.get('funcion') or inspect.stack()[1].function
        if e is not None:
            mensaje = str(e)
            EscribirLog(funcion + ': ' + mensaje)
        elif JsonUpdate.get('log', False):
            EscribirLog(funcion + ': ' + mensaje)
        else:
            print(funcion + ': ' + mensaje)
    msj = mensaje if mensaje is not None else 'Registro guardado con exito!.' if iddatos <= 0 else 'Registro modificado con exito!.'
    Resp = {
        'Estatus': estatus,
        'mensaje': msj,
        'ismodic': iddatos > 0,
        'Mostrar': tipomensaje,
        'AutoCerrar': AutoCerrarAlerta,
        **JsonUpdate
    }

    return Resp

def MensajeGeneral(estatus='Exito',mensaje='', **JsonUpdate):
    """PARA MOSTRAR UN MENSAJE DE MODIFICACION ES OBLIGATORIO EL ID DEL DOCUMENTO.\n
PARA MOSTRAR UN MENSAJE DE ERROR ES NECESARIO ENVIAR EL PARAMETRO \n
PARA MOSTRAR UN MENSAJE EN FORMATO ALERTA ES NECESARIO ENVIAR EL PARAMETRO tipomensaje \n
estatus=Error,\n mensaje=MENSAJE A MOSTRAR.
    """
    msj= mensaje
    Resp={'Estatus':estatus,'mensaje':msj,**JsonUpdate}
    return Resp


def GetHostName(request: Request):
    try:
        # Usar X-Forwarded-Host y X-Forwarded-Proto si están disponibles
        protocolo = request.headers.get('X-Forwarded-Proto', request.scheme)
        host = request.headers.get('X-Forwarded-Host', request.host)
        
        # Limpiar el host en caso de valores duplicados
        host = host.split(',')[0]  # Tomar solo el primer valor antes de la coma
        
        # Construir la URL directamente
        result = f"{protocolo}://{host}"
        return result
    except Exception as e:
        EscribirLog(f"Error en GetHostName: {str(e)}")
        return ''

# def GetHostName2(request:Request):
#     try:
#         from urllib.parse import urlparse
#         o = urlparse(request.base_url)
#         result=o.scheme+"://"+o.netloc
#         return result
#     except Exception as e:
#         EscribirLog(f"Error en GetHostName2: {str(e)}")
#         return ''

def StrToFloat(dato):
    try:
        dato=str(dato).replace(',','')
        result=float(dato)
        return result
    except Exception as e:
        EscribirLog(f"Error al convertir a float en StrToFloat: {str(e)}")
        return 0.0

def Base64ToImagen(base64Str:str):
    try:
        #decode base64 string data
        substrin= base64Str[0:14]
        formato= substrin.split('/')[1]
        base64Str=base64Str.replace('data:image/jpeg;base64,','').replace('data:image/png;base64,','')
        decoded_data=base64.b64decode((base64Str))
        #write the decoded data back to original format in  file
        ruta=OptenerRutaApp()+"Temp/"
        CrearDirectorio(ruta)
        nombreAchivo=uuid.uuid4().hex[0:8]+"."+formato
        #creado=CreateFile(ruta+nombreAchivo,decoded_data)
        img_file = open(ruta+nombreAchivo, 'wb')
        img_file.write(decoded_data)
        img_file.close()

        #if creado ==True:
        return ruta+nombreAchivo,formato
        #raise Exception("")
        return '',''
    except Exception as e:
        return '',''
    
def CopiarArchivo(RutaOrigen:str,RutaDestino:str,borrar:bool=False):
    try:
        shutil.copyfile(RutaOrigen,RutaDestino)
        if borrar==True:
            DeleteFile(RutaOrigen)
        return True
    except Exception as e:
        return False

def ReadFile(nombre,encoding='utf-8'):
    try:
        file=open(nombre,'r',encoding=encoding)
        result=file.read()
        file.close()
        return result
    except Exception as e:
        return ""

def ReadFileToList(nombre):
    try:
        file=open(nombre,'r')
        result=file.readlines()
        file.close()
        return result
    except Exception as e:
        return []

def WriteFile(nombre,datos):
    try:
        file=open(nombre,'w')
        result=file.write(datos)
        file.close()
        return result
    except Exception as e:
        return ""

def CreateFile(nombre,datos,reemplace=True):
    try:
        if reemplace:
            DeleteFile(nombre)
        file=open(nombre,'a')
        file.write(str(datos))
        file.close()
    except Exception as e:
        pass

def DeleteFile(nombre):
    try:
        os.remove(nombre)
    except Exception as e:
        pass

def DeleteListFile(nombre=[],tiempoEspera=60.0,IsGevent=True):
    try:
        TiempoEspera(tiempoEspera,IsGevent)
        for listFile in nombre:
            os.remove(listFile)
    except Exception as e:
        pass

def ExistFile(nombre):
    try:
       result=os.path.exists(nombre)
       return result
    except Exception as e:
        return False

def ExisteDirectorio(Ruta):
    try:
       result=os.path.isdir(Ruta)
       return result
    except Exception as e:
        return False

def CrearDirectorio(Ruta):
    """
    VALIDA SI NO EXITE EL DIRECTORIO PARA CREARLO.\n
    SI TODO ES CORRECTO DEVUELVE TRUE DE LO CONTRARIO DEVUELVE FALSE.
    """
    try:
       if ExisteDirectorio(Ruta=Ruta)==False:
            os.mkdir(Ruta)

    except Exception as e:
        return False

def BorrarDirectorio(Ruta):
    try:
        rmtree(Ruta)
    except Exception as e:
        return False

def BorrarDirectorioVacio(Ruta):
    try:
        os.rmdir(Ruta)
    except Exception as e:
        return False

def FechaHora(AddDias=0.0,AddHoras=0.0,AddMinutos=0.0,AddSegundo=0.0):
    # zona = pytz.timezone('America/Santo_Domingo')
    # fecha=datetime.now(tz=zona)+timedelta(days=AddDias,hours=AddHoras,minutes=AddMinutos,seconds=AddSegundo)
    if AddHoras>0.0 or AddHoras<0.0:
        AddMinutos+=AddHoras*60
    fecha=StrToDateTime(Fecha(AddDias=AddDias)+" "+Hora(AddMinutos,AddSegundo))
    return fecha

def Fecha(AddDias=0.0,AddHoras=0.0,AddMinutos=0.0,AddSegundo=0.0):
    zona = pytz.timezone('America/Santo_Domingo')
    fecha=datetime.now(tz=zona)+timedelta(days=AddDias,hours=AddHoras,minutes=AddMinutos,seconds=AddSegundo)
    #fecha = zona.localize(datetime.datetime.now())
    date_format = "%d/%m/%Y"
    fecha=fecha.strftime(date_format)
    return fecha

def Hora(AddMinutos=0.0,AddSegundo=0.0):
    zona = pytz.timezone('America/Santo_Domingo')
    fecha=datetime.now(tz=zona)+timedelta(minutes=AddMinutos,seconds=AddSegundo)
    time_format = "%I:%M:%S %p"
    fecha=fecha.strftime(time_format)
    return fecha


def Encriptar(datos, clave):
        result = ""
        try:
            result=jwt.encode({"Datos":datos},clave, algorithm="HS256").decode(encoding="utf-8")
        except Exception as ex:
            EscribirLog("Error En Encriptar: "+str(ex))
        return str(result)

def DesEncriptar(datos, clave):
        result = ""
        try:
            result=jwt.decode(datos,clave, algorithms=["HS256"])["Datos"]
        except Exception as ex:
            print(str(ex))
        return result

def BorrarArchivo(nombre,tiempoEspera=60.0,IsGevent=True):
    try:
        TiempoEspera(tiempoEspera,IsGevent)
        os.remove(nombre)
    except Exception as e:
        print('Excepcion Al borrar el archivo solicitado: '+str(e),"Error")

def BorrarArchivoHoraCreado(nombre,NumeroHoras=1,IsGevent=True):
    """ESTE METODO SOLO SE DEBE USAR CON UN HILO"""
    try:
        import ServexTools.GetTime as tim
        while True:
            fecha= OptenerFechaArchivo(nombre)
            horas=tim.CalHoras(fecha)
            if horas>=NumeroHoras:
                os.remove(nombre)
                break
            TiempoEspera(3600,IsGevent)
    except Exception as e:
        print('Excepcion Al borrar el archivo solicitado: '+str(e),"Error")

def IterarDatosSQliteToList(dato):
    try:
        lista=[]
        for v in dato:
            lista.append(dict(v))
        return lista
    except Exception as e:
        return "Error"


def Progressbar(data, ncols=100, color='#7AFF7A'):
    from tqdm import tqdm
    custom_format = '[{bar}] -> {percentage:.0f}% ({n:03}/{total:03} | Transcurrido: {elapsed} | Estimado: {remaining})'
    return tqdm(data,ncols=ncols,bar_format=custom_format,colour=color,dynamic_ncols=True)


def OptenerDatoApi(url, ruta, parametro: dict = {}, TiempoEspera=60, metodo: Metodo = Metodo.GET, headers=None):
    with httpx.Client(timeout=TiempoEspera) as client:
        if metodo == Metodo.GET:
            resp = client.get(f"{url}/{ruta}", json=parametro, headers=headers)
        else:
            resp = client.post(f"{url}/{ruta}", json=parametro, headers=headers)
    return resp.json()

def DesComprimir(RutaZip,RutaDescomprimir,eliminar=False):
    zip = ZipFile(RutaZip,"r")
    zip.extractall(RutaDescomprimir)
    zip.close()
    if eliminar:
        DeleteFile(RutaZip)
    return RutaDescomprimir


def EscribirLog(texto, tipo="Error"):
        
    try:
        dia = datetime.now().day
        mes = datetime.now().month
        year = datetime.now().year
        Hora = str(datetime.now().hour) + ":" + str(datetime.now().minute)
        tiempo = str(dia) + "/" + str(mes) + "/" + str(year) + " " + Hora
        Directorio=OptenerRutaApp()+"Log"
        if ExisteDirectorio(Directorio)==False:
            os.mkdir(Directorio)
        mensajeActual = ""
        Url = Directorio+"/Success.log" if tipo != "Error" else Directorio+"/Error.log"
        try:
            if ExistFile(Url):
                creados=OptenerFechaArchivo(Url)
                if CalDias(fechaInicial=creados)>=30:
                    DeleteFile(Url)
                else:
                    zise=os.path.getsize(Url)
                    numero,medida=convert_size(zise)
                    if medida=="MB" and numero>10.0:
                        DeleteFile(Url)
            else:
                CreateFile(Url,"")
        except Exception as e:
            print(str(e))
            
        if ExistFile(Url):
            mensajeActual = ReadFile(Url)
            
            
        mensaje=tiempo + ": " + texto + "\n" + mensajeActual
        msjprint=tiempo + ": " + texto + "\n"
        print(msjprint)
        WriteFile(Url,mensaje)
    except Exception as e:
        print(str(e))

def CalDias(fechaInicial,FechaActual=datetime.now(),tiempoGratis=0):
    days=0
    diff_date = FechaActual - fechaInicial
    if diff_date.total_seconds() > ((tiempoGratis+1)*60):
        days = math.ceil(diff_date.total_seconds()/86400)
    return days
