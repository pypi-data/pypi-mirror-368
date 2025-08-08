from datetime import datetime
import math

def CalDias(fechaInicial,FechaActual=datetime.now(),tiempoGratis=0):
    days=0
    diff_date = FechaActual - fechaInicial
    if diff_date.total_seconds() > ((tiempoGratis+1)*60):
        days = math.ceil(diff_date.total_seconds()/86400)
    return days

def CalDiasExactos(fechaInicial):
    FechaActual=datetime.now()
    diff_date = FechaActual - fechaInicial
    return diff_date.days

def CalHoras(fechaInicial,FechaActual=datetime.now(),tiempoGratis=0,redondear=True):
    horas=0
    diff_date = FechaActual - fechaInicial
    if diff_date.total_seconds() > ((tiempoGratis+1)*60):
        if redondear:
            horas = math.ceil(diff_date.total_seconds()/3600)
        else:
           return CalMinutos(fechaInicial,FechaActual,tiempoGratis)
    return horas

def CalMinutos(fechaInicial,FechaActual=datetime.now(),tiempoGratis=0):
    minutos=0
    diff_date = FechaActual - fechaInicial
    if diff_date.total_seconds() > ((tiempoGratis+1)*60):
        minutos = math.ceil(diff_date.total_seconds()/60)
    return minutos

def CalSegundos(fechaInicial):
    FechaActual=datetime.now()
    diff_date = FechaActual - fechaInicial
    return diff_date.total_seconds()

def CalHolaYMinutos(fechaInicial,fechaFinal=datetime.now()):
    horas=0
    diff_date = fechaFinal-fechaInicial
    tim=str(diff_date).split(':')

    horas=tim[0]
    minutos=tim[1]
    horasYminutos=tim[0]+':'+tim[1]
    #return horas,minutos,horasYminutos
    return horasYminutos


def CalMinutosTransc(fechaInicial):
    try:
        horas=0
        diff_date = datetime.now()-fechaInicial
        tim=str(diff_date).split(':')

        horas=tim[0]
        minutos=tim[1]
        horasYminutos=tim[0]+tim[1]
        #return horas,minutos,horasYminutos
        return int(horasYminutos)
    except Exception as e:
        return 10