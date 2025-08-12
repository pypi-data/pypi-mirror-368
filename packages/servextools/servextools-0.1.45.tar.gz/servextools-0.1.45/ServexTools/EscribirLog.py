from datetime import datetime
import os
import ServexTools.Tools as Tools
from ServexTools.GetTime import CalDias

def GetDirectorio():
    return Tools.OptenerRutaApp()
        
                
def EscribirLog(texto, tipo="Error"):
        
    try:
        dia = datetime.now().day
        mes = datetime.now().month
        year = datetime.now().year
        Hora = str(datetime.now().hour) + ":" + str(datetime.now().minute)
        tiempo = str(dia) + "/" + str(mes) + "/" + str(year) + " " + Hora
        Directorio=GetDirectorio()+"Log"
        if Tools.ExisteDirectorio(Directorio)==False:
            os.mkdir(Directorio)
        mensajeActual = ""
        Url = Directorio+"/Success.log" if tipo != "Error" else Directorio+"/Error.log"
        try:
            if Tools.ExistFile(Url):
                creados=Tools.OptenerFechaArchivo(Url)
                if CalDias(fechaInicial=creados)>=30:
                    Tools.DeleteFile(Url)
                else:
                    zise=os.path.getsize(Url)
                    numero,medida=Tools.convert_size(zise)
                    if medida=="MB" and numero>10.0:
                        Tools.DeleteFile(Url)
            else:
                Tools.CreateFile(Url,"")
        except Exception as e:
            print(str(e))
            
        if Tools.ExistFile(Url):
            mensajeActual = Tools.ReadFile(Url)
            
            
        mensaje=tiempo + ": " + texto + "\n" + mensajeActual
        msjprint=tiempo + ": " + texto + "\n"
        print(msjprint)
        Tools.WriteFile(Url,mensaje)
    except Exception as e:
        print(str(e))

def EscribirConsola(texto):        
    try:
        dia = datetime.now().day
        mes = datetime.now().month
        year = datetime.now().year
        Hora = str(datetime.now().hour) + ":" + str(datetime.now().minute)
        tiempo = str(dia) + "/" + str(mes) + "/" + str(year) + " " + Hora
        Directorio=GetDirectorio()+"Log"
        if Tools.ExisteDirectorio(Directorio)==False:
            os.mkdir(Directorio)
        mensajeActual = ""
        Url = Directorio+"/Consola.log"
        try:
            if Tools.ExistFile(Url):
                creados=Tools.OptenerFechaArchivo(Url)
                if CalDias(fechaInicial=creados)>=30:
                    Tools.DeleteFile(Url)
                else:
                    zise=os.path.getsize(Url)
                    numero,medida=Tools.convert_size(zise)
                    if medida=="MB" and numero>10.0:
                        Tools.DeleteFile(Url)
            else:
                Tools.CreateFile(Url,"")
        except Exception as e:
            print(str(e))
            
        if Tools.ExistFile(Url):
            mensajeActual = Tools.ReadFile(Url)
            
           
        mensaje=tiempo + ": " + texto + "\n" + mensajeActual
        msjprint=tiempo + ": " + texto + "\n"
        # mensaje="******" + tiempo + "******\n" + texto + "\n******************\n" + mensajeActual
        # msjprint="******" + tiempo + "******\n" + texto + "\n******************\n"
        print(msjprint)
        Tools.WriteFile(Url,mensaje)
    except Exception as e:
        print(str(e))

def EscribirProcesos(texto):        
    try:
        dia = datetime.now().day
        mes = datetime.now().month
        year = datetime.now().year
        Hora = str(datetime.now().hour) + ":" + str(datetime.now().minute)
        tiempo = str(dia) + "/" + str(mes) + "/" + str(year) + " " + Hora
        Directorio=GetDirectorio()+"Log"
        if Tools.ExisteDirectorio(Directorio)==False:
            os.mkdir(Directorio)
        mensajeActual = ""
        Url = Directorio+"/Procesos.log"
        
        try:
            if Tools.ExistFile(Url):
                creados=Tools.OptenerFechaArchivo(Url)
                if CalDias(fechaInicial=creados)>=30:
                    Tools.DeleteFile(Url)
                else:
                    zise=os.path.getsize(Url)
                    numero,medida=Tools.convert_size(zise)
                    if medida=="MB" and numero>10.0:
                        Tools.DeleteFile(Url)
            else:
                Tools.CreateFile(Url,"")
        except Exception as e:
            print(str(e))
            
        if Tools.ExistFile(Url):
            mensajeActual = Tools.ReadFile(Url)
            
           
        mensaje=tiempo + ": " + texto + "\n" + mensajeActual
        Tools.WriteFile(Url,mensaje)
    except Exception as e:
        print(str(e))
        
def EscribirUpdate(texto):        
    try:
        from app import socketio as io
        dia = datetime.now().day
        mes = datetime.now().month
        year = datetime.now().year
        Hora = str(datetime.now().hour) + ":" + str(datetime.now().minute)
        tiempo = str(dia) + "/" + str(mes) + "/" + str(year) + " " + Hora
        Directorio=GetDirectorio()+"Log"
        if Tools.ExisteDirectorio(Directorio)==False:
            os.mkdir(Directorio)
        mensajeActual = ""
        Url = Directorio+"/Update.log"
        try:
            if Tools.ExistFile(Url):
                creados=Tools.OptenerFechaArchivo(Url)
                if CalDias(fechaInicial=creados)>=30:
                    Tools.DeleteFile(Url)
                else:
                    zise=os.path.getsize(Url)
                    numero,medida=Tools.convert_size(zise)
                    if medida=="MB" and numero>10.0:
                        Tools.DeleteFile(Url)
            else:
                Tools.CreateFile(Url,"")
        except Exception as e:
            print(str(e))
            
        if Tools.ExistFile(Url):
            mensajeActual = Tools.ReadFile(Url)
            
           
        mensaje=tiempo + ": " + texto + "\n" + mensajeActual
        Tools.WriteFile(Url,mensaje)
        io.emit("EscribirEnConsola",mensaje)
        EscribirConsola(texto)
    except Exception as e:
        print(str(e))