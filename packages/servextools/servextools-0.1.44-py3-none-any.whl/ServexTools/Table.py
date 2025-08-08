from functools import lru_cache
from flask import Blueprint, request
from io import StringIO
from ServexTools.Necesario import insert_paginacion, find_paginacion
from ServexTools.EscribirLog import EscribirLog
from ServexTools import Tools
import typing as t
from typing import List
import polars as pl
import numpy as np
import inspect
import platform
from flask import session
import os
import multiprocessing as mp
from ServexTools.socket_manager import get_socketio
socketio = get_socketio()


bp = Blueprint('Table', __name__)

system = platform.system().lower()

COLUMNA = "NombreColumnas"
DATO = "DatosColumnas"
CLASS = "ClassColumnas"
FORMATO = "ColumnasFormato"
TOTALIZAR = "ColumnasTotalizar"
SUBDATOS = "SubColumnasDatos"
FORMAT_HANDLERS = {
    'dict': lambda x, key: x[key] if x and key in x else '',
    'list': lambda x, key: next((item[key] for item in x if isinstance(item, dict) and key in item), ''),
    'df': lambda x, key: x[key][0] if len(x[key]) > 0 else ''
}

VECTOR_FORMAT_HANDLERS = {
    'moneda': np.vectorize(Tools.FormatoMoneda, otypes=[str]),
    'date': np.vectorize(Tools.DateFormat, otypes=[str]),
    'datetime': np.vectorize(Tools.DateTimeFormat, otypes=[str]),
    'encriptar': np.vectorize(Tools.Encriptar, otypes=[str])
}
def CrearTabla(
    Datos: t.Union[list, list],
    NombreColumnas: t.Union[tuple, tuple] = None,
    DatosColumnas: t.Union[tuple, tuple] = None,
    ClassColumnas: t.Union[tuple, tuple] = None,
    FormatoColumnas: t.Union[tuple, bool] = False,
    TotalizarColumnas: t.Union[tuple, bool] = False,
    ColumnasJson: t.Union[list, dict] = None,
    SubColumnasDatos: t.Union[list, bool] = False,
    SubFilas: t.Union[list, bool] = False,
    FilasPlus: t.Union[list, bool] = False,
    MarcarRows: t.Union[tuple, bool] = False,
    Titulo="Detalle",
    nombreClase='TablaFilas',
    idtable="table",
    MostrarLosTH=False,
    MostralConteo=True,
    TablaNumero=0,
    IncluirScript=True,
    RealizarReplace=False,
    paginacion=False,
    paginacion_server=False,
    LongitudPaginacion=200,
    claseprincipal="AlturaGrid",
    progressBar=False,
    sessionidusuario=None,
    reporte=False,
    conteo=True,
    iddivtable="griddatos",
    ps_paginando=False,
    ps_conteo=0,
    ps_offset=0,
    ps_func='',
    ps_current_active_page=1
):
    """
    Generador de tablas HTML con múltiples opciones avanzadas.
    
    Crea tablas HTML dinámicas con soporte para paginación en cliente o servidor,
    procesamiento vectorizado para grandes conjuntos de datos, cálculo de totales,
    formateo de celdas, y visualización progresiva con barras de progreso.
    
    Args:
        Datos: Lista de diccionarios con los datos a mostrar en la tabla
        NombreColumnas: Tupla con los nombres de las columnas a mostrar
        DatosColumnas: Tupla con los nombres de las claves en los diccionarios de Datos
        ClassColumnas: Tupla con las clases CSS para cada columna
        FormatoColumnas: Tupla con los formatos a aplicar a cada columna (moneda, fecha, etc.)
        TotalizarColumnas: Tupla de booleanos indicando qué columnas deben totalizarse
        ColumnasJson: Alternativa para definir columnas en formato JSON
        SubColumnasDatos: Configuración para acceder a datos anidados
        SubFilas: Configuración para generar subfilas en la tabla
        FilasPlus: Configuración para agregar filas adicionales
        MarcarRows: Configuración para aplicar estilos condicionales a filas
        Titulo: Título de la tabla
        nombreClase: Clase CSS para las filas
        idtable: ID HTML para la tabla
        MostrarLosTH: Si se deben mostrar los encabezados cuando no hay datos
        MostralConteo: Si se debe mostrar el contador de registros
        TablaNumero: Número identificador para la tabla
        IncluirScript: Si se debe incluir el script JavaScript
        RealizarReplace: Si se deben reemplazar saltos de línea en los datos
        paginacion: Habilitar paginación en cliente
        paginacion_server: Habilitar paginación en servidor
        LongitudPaginacion: Número de registros por página
        claseprincipal: Clase CSS principal para el contenedor
        progressBar: Mostrar barra de progreso durante la generación
        sessionidusuario: ID de sesión del usuario para notificaciones
        reporte: Generar versión para reportes
        conteo: Mostrar conteo de registros
        iddivtable: ID del div contenedor
    
    Returns:
        str o tuple: HTML generado o tupla con HTML y totales según configuración
    """
    try:
        ps_idusuario = session['idusuario']
    except Exception:
        ps_idusuario = 0
    if ColumnasJson:
        NombreColumnas = tuple(col[COLUMNA] for col in ColumnasJson)
        DatosColumnas = tuple(col[DATO] for col in ColumnasJson)
        ClassColumnas = tuple(col.get(CLASS, "") for col in ColumnasJson)
        FormatoColumnas = tuple(col.get(FORMATO, "") for col in ColumnasJson)
        TotalizarColumnas = tuple(col.get(TOTALIZAR, False) for col in ColumnasJson)
        SubColumnasDatos = tuple(col.get(SUBDATOS, False) for col in ColumnasJson)

    ValidarLongitudDatos(
        NombreColumnas, DatosColumnas, ClassColumnas, 
        FormatoColumnas, TotalizarColumnas, SubColumnasDatos
    )

    countFilas = 0
    tamano_datos = len(Datos) if progressBar else 0

    ColumnasTH = StringIO()
    for i, col in enumerate(NombreColumnas):
        ColumnasTH.write(f'<th scope="col" class="{ClassColumnas[i]}">{col}</th>')

    
    Totales = {
        f'T{col}': 0.0 for i, col in enumerate(DatosColumnas) 
        if TotalizarColumnas and not isinstance(TotalizarColumnas, bool) and TotalizarColumnas[i]
    }

    FilasTD = StringIO()

    
    Datos_originales = None
    dt_conteo = 0
    
    try:
        
        if not ps_paginando and paginacion_server:
            Datos_originales = Datos.copy() if isinstance(Datos, list) else []
            dt_conteo = len(Datos_originales)
            offset = 0
            limit = offset + LongitudPaginacion
            Datos = Datos_originales[offset:limit] if dt_conteo > 0 else []
            # Calcular los totales para todos los datos originales antes de paginar
            totales_completos = {}
            if TotalizarColumnas and not isinstance(TotalizarColumnas, bool) and any(TotalizarColumnas):
                # Calcular totales para cada columna que requiere totalización
                for i, col in enumerate(DatosColumnas):
                    if TotalizarColumnas[i]:
                        total = 0
                        for row in Datos_originales:
                            if isinstance(row, dict) and col in row:
                                valor = Tools.StrToFloat(row.get(col, 0))
                                total += valor if valor is not None else 0
                        totales_completos[f'T{col}'] = total
                # Registrar los totales calculados para debug
                ruta_tabla_actual = inspect.stack()[1].function if ps_func == '' else ps_func
                EscribirLog(f"Totales calculados para {ruta_tabla_actual}: {totales_completos}")
            
            insert_paginacion(
                RUTA_TABLA=inspect.stack()[1].function if ps_func == '' else ps_func,
                datos=Datos_originales,
                ps_idusuario = ps_idusuario,
                longitud_paginacion=LongitudPaginacion,
                parametros_tabla={
                    'NombreColumnas': NombreColumnas,
                    'DatosColumnas': DatosColumnas,
                    'ClassColumnas': ClassColumnas,
                    'FormatoColumnas': FormatoColumnas,
                    'TotalizarColumnas': TotalizarColumnas,
                    'ColumnasJson': ColumnasJson,
                    'SubColumnasDatos': SubColumnasDatos,
                    'SubFilas': SubFilas,
                    'FilasPlus': FilasPlus,
                    'MarcarRows': MarcarRows,
                    'Titulo': Titulo,
                    'nombreClase': nombreClase,
                    'idtable': idtable,
                    'MostrarLosTH': MostrarLosTH,
                    'MostralConteo': MostralConteo,
                    'TablaNumero': TablaNumero,
                    'IncluirScript': IncluirScript,
                    'RealizarReplace': RealizarReplace,
                    'paginacion': paginacion,
                    'paginacion_server': paginacion_server,
                    'LongitudPaginacion': LongitudPaginacion,
                    'claseprincipal': claseprincipal,
                    'progressBar': progressBar,
                    'sessionidusuario': sessionidusuario,
                    'reporte': reporte,
                    'conteo': conteo,
                    'ps_paginando': True
                },
                totales=totales_completos
            )
        
        elif ps_paginando and paginacion_server:
            if ps_current_active_page > 1:
                Datos_originales = Datos.copy() if isinstance(Datos, list) else []
                dt_conteo = len(Datos_originales)
                offset = ps_offset
                limit = offset + LongitudPaginacion
                Datos = Datos_originales[offset:limit] if dt_conteo > 0 else []
                Datos_originales = Datos
            else:
                resultados = find_paginacion(ps_func, ps_idusuario, ps_current_active_page)
                if resultados and 'paginas' in resultados:
                    Datos_originales = resultados['paginas']
                else:
                    EscribirLog(f"No se encontraron datos para el ID de usuario: {ps_idusuario}")

                dt_conteo = len(Datos_originales)

                offset = (ps_current_active_page - 1) * LongitudPaginacion if ps_offset == 0 else ps_offset
                limit = offset + LongitudPaginacion
    except Exception as e:
        EscribirLog(f"Error en paginación servidor: {str(e)}")
        
        pass

    
    try:
        if not ps_paginando and Totales and Datos_originales is not None and len(Datos_originales) > 0:
            
            # Identificar columnas que necesitan totales sin usar DataFrame
            columnas_total = []
            for i, col in enumerate(DatosColumnas):
                if i < len(TotalizarColumnas) and TotalizarColumnas[i]:
                    columnas_total.append(col)
            
            if columnas_total and Datos_originales:
                # Verificar si Datos_originales es una lista de diccionarios
                if isinstance(Datos_originales[0], dict):
                    # Calcular totales para cada columna que lo necesita
                    for col in columnas_total:
                        total = 0
                        for fila in Datos_originales:
                            if col in fila:
                                # Convertir el valor a float y sumarlo
                                valor = Tools.StrToFloat(fila.get(col))
                                total += valor if valor is not None else 0
                        # Agregar el total al diccionario de Totales
                        Totales[f'T{col}'] += total
                else:
                    # Si no es lista de diccionarios, sino lista de listas
                    # Primero identificar los índices de las columnas a totalizar
                    if DatosColumnas:
                        indices_columnas = []
                        for col in columnas_total:
                            if col in DatosColumnas:
                                idx = DatosColumnas.index(col)
                                indices_columnas.append((col, idx))
                        
                        # Calcular totales usando los índices
                        for col, idx in indices_columnas:
                            total = 0
                            for fila in Datos_originales:
                                if idx < len(fila):
                                    valor = Tools.StrToFloat(fila[idx])
                                    total += valor if valor is not None else 0
                            # Agregar el total al diccionario de Totales
                            Totales[f'T{col}'] += total
                
    except Exception as e:
        
        EscribirLog(f"Error al calcular totales: {str(e)}")
        
        for col in DatosColumnas:
            if col not in Totales:
                Totales[f'T{col}'] = 0.0

    
    if not Datos:
        if not MostrarLosTH:
            ColumnasTH = StringIO()
            FilasTD.write("<div class='text-center'>NO SE ENCONTRARON DATOS.</div>")

    else:
        class_map = {i: ClassColumnas[i] for i in range(len(ClassColumnas))}
        format_map = {i: FormatoColumnas[i] for i in range(len(FormatoColumnas))} if FormatoColumnas else {}

        def formatear_celda(i, col, row):
            valor = ProcesarSubDatos(SubColumnasDatos, i, col, row)
            return Formatos(FormatoColumnas, i, valor) if i in format_map else valor

        def fila_html(idx, row):
            numerador = str(idx) + str(TablaNumero) if TablaNumero > 0 else str(idx)
            style = "background-color: #97d2ea;" if SubFilas else ""
            
            
            if MarcarRows:
                respuesta = MarcarFilas(MarcarRows, SubColumnasDatos, DatosColumnas, row)
                clase_fila = f"{nombreClase} CursorPointer {respuesta}"
            else:
                clase_fila = f"{nombreClase} CursorPointer"
                
            html = f"<tr id='rows_{numerador}' class='{clase_fila}' style='{style}'>"
            
            
            celdas_html = ""
            for i, col in enumerate(DatosColumnas):
                valor = formatear_celda(i, col, row)
                if paginacion_server==False and TotalizarColumnas and not isinstance(TotalizarColumnas, bool) and TotalizarColumnas[i]:
                    Totales[f'T{col}'] += Tools.StrToFloat(valor)
                celdas_html += f'<td id="{col}_{numerador}" class="{class_map[i]} text-wrap">{valor}</td>'
            
            
            
            if SubFilas:
                return html + celdas_html
            else:
                return html + celdas_html + "</tr>"

        for idx, row in enumerate(Datos):
            row = {k: v.replace("\n", "<stln>") if isinstance(v, str) and "\n" in v else v for k, v in row.items()} if RealizarReplace else row
            countFilas += 1
            
            
            fila_principal = fila_html(idx, row)
            FilasTD.write(fila_principal)
            
            
            if SubFilas:
                DtSubFilas = ProcesarSubFilas(SubFilas=SubFilas, row=row, FilasPlus=FilasPlus)
                FilasTD.write(DtSubFilas)
                FilasTD.write("</tr>")  
            
            
            if progressBar and sessionidusuario and idx % 100 == 0:
                socketio.emit(
                    f"ProgresoDeTablaReport_{sessionidusuario}",
                    {'transcurrido': countFilas, 'total': tamano_datos, 'barra': True}
                )
                Tools.TiempoEspera(0.01,True)

    
    ScriptPaginacion = ""
    if paginacion and countFilas >= LongitudPaginacion and not paginacion_server:
        ScriptPaginacion = f"""
            $(function () {{
                paginateTable('{idtable}', {LongitudPaginacion});
            }});
        """

    if paginacion_server:
        func = inspect.stack()[1].function if ps_func == '' else ps_func
        offset = ps_offset
        limit = offset + LongitudPaginacion
        dt_conteo = ps_conteo if ps_paginando else len(Datos_originales)

        ScriptPaginacion = f"""
            async function {func}_ps(page) {{
                var datos = {{ page: page, ps_idusuario: '{ps_idusuario}' }};
                const data = await General.PostBackData(datos, '/{func}_ps');
                if (data.Estatus == 'Exito') {{
                    AgregarHtml('#{iddivtable}', data.html);
                }} else {{
                    AgregarHtml('#{iddivtable}', data.html);
                    MsjError(data);
                }}
            }}
            paginateTableServer('{idtable}', {dt_conteo}, {LongitudPaginacion}, {ps_current_active_page}, async function(page) {{
                await {func}_ps(page);
                document.querySelectorAll('.pagination-button.active').forEach(el => el.classList.remove('active'));
                document.querySelector(`.pagination-button[data-page="${{page}}"]`)?.classList.add('active');
            }});
        """

    Script = ""
    if IncluirScript:
        Script = """
                <script>
             
            function """+idtable+"""(callback) {
                try {
                    var elementos = document.querySelectorAll('."""+nombreClase+"""');

                    elementos.forEach(function(elemento) {
                        // Si ya tiene el evento, no lo agregamos de nuevo
                        if (!elemento.classList.contains('evento-agregado')) {
                            elemento.addEventListener('click', function() {
                                if(VerificarAtributo('#"""+idtable+"""','disabled') == true){
                                    return;
                                }
                                
                                // Crear un objeto JSON directamente
                                var datosJson = {};
                                var iddato = "";
                                
                                // Eliminar la clase de selección previa
                                var elementosSeleccionados = document.querySelectorAll('.Seleccion');
                                elementosSeleccionados.forEach(function(el) {
                                    el.classList.remove('Seleccion');
                                });
                                
                                this.classList.add('Seleccion');

                                // Obtener las celdas de la fila seleccionada
                                var td = this.querySelectorAll('td');
                                td.forEach(function(tdElement) {
                                    var idcontrolsnow = tdElement.id;
                                    var numero = 0;

                                    // Verificar si es un campo que contiene '_id'
                                    if (idcontrolsnow.includes('_id')) {
                                        numero = 1;
                                    }

                                    iddato = tdElement.id.split('_');

                                    // Agregar la propiedad al objeto JSON con el contenido de la celda
                                    datosJson[iddato[numero]] = tdElement.textContent;
                                });

                                // Llamar al callback con el objeto JSON construido
                                callback(datosJson);
                            });

                            // Marcar el elemento como procesado para evitar duplicados
                            elemento.classList.add('evento-agregado');
                        }
                    });

                } catch (error) {
                    //console.log("Error en la función de la tabla: " + error);
                }
            }
            """+ScriptPaginacion+"""
            </script>""" 

    HtmlConteo = ""
    if MostralConteo:
        if paginacion_server:
            offset = (ps_current_active_page - 1) * LongitudPaginacion
            limit = min(offset + LongitudPaginacion, dt_conteo)
            HtmlConteo = f"""
                <span class="badge bg-dark" style="font-size: 12px;width: max-content;">{offset + 1} - {limit} / {dt_conteo}</span>
            """
        else:
            HtmlConteo = f"""
                <span class="badge bg-dark" style="font-size: 12px;width: max-content;">Cant: {countFilas}</span>
            """

    
    Html = f"""
      <div class='card' style='margin-bottom: 0px; margin-top:5px;'>
        <div class='card-header bg-primary text-center' style='font-size: 20px; color: #FFF; padding-top: 5px; padding-bottom: 5px;'>
            <span class='fa fa-th-list'></span>
            <span>{Titulo}</span>
        </div>
        <div class="table-responsive {claseprincipal}">
        <table class="table table-hover table-striped" id='{idtable}' style="overflow: hidden">
        <thead>
            <tr>
            {ColumnasTH.getvalue()}
            </tr>
        </thead>
        <tbody>
            {FilasTD.getvalue()}
        </tbody>
        </table>
        
        </div>
        {HtmlConteo}
        </div>
        {Script}
    """
    
    
    HtmlReporte = ""
    if reporte:
        HtmlReporte = f"""
        <div class="card" style="margin-bottom: 0px; margin-top:5px;">
        <div class="card-header bg-info text-center" style="font-size: 20px; color: #FFF; padding-top: 5px; padding-bottom: 5px;">
            <span class="fa fa-th-list"></span>
            <span>{Titulo}</span>
        </div>
        <div class="table-responsive">
        <table class="table table-hover table-striped" style="overflow: hidden">
        <thead>
            <tr>
            {ColumnasTH.getvalue()}
            </tr>
        </thead>
        <tbody>
            {FilasTD.getvalue()}
        </tbody>
        </table>
        {HtmlConteo}
        </div>
        </div>
        """

    
    if progressBar == True:
        socketio.emit(f"CerrarProgresoDeTablaReport_{sessionidusuario}", '')
    
    
    if TotalizarColumnas and not isinstance(TotalizarColumnas, bool) and any(TotalizarColumnas):
        if reporte == True:
            return Html, Totales, HtmlReporte
        else:
            return Html, Totales
    elif reporte == True:
        return Html, HtmlReporte
    else:
        return Html



def CrearFila(nombreClase, NumeralTabla, style, RespuestaValidacion):
    """
    Genera el HTML para la apertura de una fila de tabla con clases y estilos específicos.
    
    Args:
        nombreClase: Clase CSS base para la fila
        NumeralTabla: Identificador numérico para la fila
        style: Estilos CSS inline para aplicar a la fila
        RespuestaValidacion: Clase CSS adicional basada en validación
        
    Returns:
        str: Etiqueta HTML de apertura para una fila de tabla con atributos configurados
    """
    return f"<tr id='rows_{NumeralTabla}' class='{nombreClase} CursorPointer {RespuestaValidacion}' style='{style}'>"

def MarcarFilas(MarcarRows, SubColumnasDatos, DatosColumnas, row):
    """
    Aplica marcado condicional a filas de tabla basado en valores de datos.
    
    Evalúa recursivamente condiciones para determinar qué clase CSS aplicar a una fila,
    permitiendo árboles de decisión complejos para el estilizado condicional.
    
    Args:
        MarcarRows: Tupla con la configuración de marcado (campo, valor, clase si coincide, clase/condición si no coincide)
        SubColumnasDatos: Configuración para acceder a datos anidados
        DatosColumnas: Tupla con los nombres de las claves en los diccionarios de datos
        row: Diccionario con los datos de la fila actual
        
    Returns:
        str: Clase CSS a aplicar a la fila basada en la evaluación de condiciones
    """
    while True:
        campoValidar = MarcarRows[0]
        ValorValidar = MarcarRows[1]
        EntoncesValidacion = MarcarRows[2]
        ContrarioValidacion = MarcarRows[3]
        formato = type(ContrarioValidacion).__name__
        valor = SubDatosMarcar(SubColumnasDatos, DatosColumnas, campoValidar, row)
        if valor == ValorValidar:
            return EntoncesValidacion
        else:
            if formato == 'tuple':
                MarcarRows = ContrarioValidacion
            else:
                return ContrarioValidacion

def CondicionParaTotalizar(ColumnaTotales, SubColumnasDatos, DatosColumnas, row):
    """
    Determina si una fila debe incluirse en los cálculos de totales basado en una condición.
    
    Args:
        ColumnaTotales: Tupla con (campo_a_validar, valor_a_comparar)
        SubColumnasDatos: Configuración para acceder a datos anidados
        DatosColumnas: Tupla con los nombres de las claves en los diccionarios de datos
        row: Diccionario con los datos de la fila actual
        
    Returns:
        bool: True si la fila debe incluirse en los totales, False en caso contrario
    """
    campoValidar, ValorValidar = ColumnaTotales
    valor = SubDatosMarcar(SubColumnasDatos, DatosColumnas, campoValidar, row)
    return valor != ValorValidar

def ValidarLongitudDatos(NombreColumnas, DatosColumnas, ClassColumnas, FormatoColumnas, TotalizarColumnas, SubColumnasDatos):
    if len(NombreColumnas) != len(DatosColumnas) or len(NombreColumnas) != len(ClassColumnas):
        raise Exception("""Los datos enviados referente a las columnas (NombreColumnas, DatosColumnas y ClassColumnas) deben tener la misma cantidad de datos. 
                        NombreColumnas Cantidad("""+str(len(NombreColumnas))+"""), DatosColumnas Cantidad("""+str(len(DatosColumnas))+""") y ClassColumnas Cantidad("""+str(len(ClassColumnas))+""")""")

    if FormatoColumnas != False:
        if len(NombreColumnas) != len(FormatoColumnas):
            raise Exception("""Los datos enviados referente a las columnas (NombreColumnas y FormatoColumnas) deben tener la misma cantidad de datos.
                            NombreColumnas Cantidad("""+str(len(NombreColumnas))+""") y FormatoColumnas Cantidad("""+str(len(FormatoColumnas))+""")""")

    if TotalizarColumnas != False:
        if len(NombreColumnas) != len(TotalizarColumnas):
            raise Exception("""Los datos enviados referente a las columnas (NombreColumnas y TotalizarColumnas) deben tener la misma cantidad de datos. 
                             NombreColumnas Cantidad("""+str(len(NombreColumnas))+""") y TotalizarColumnas Cantidad("""+str(len(TotalizarColumnas))+""")""")
    if SubColumnasDatos != False:
        if len(NombreColumnas) != len(SubColumnasDatos):
            raise Exception("""Los datos enviados referente a las columnas (NombreColumnas y SubColumnasDatos) deben tener la misma cantidad de datos. 
                                NombreColumnas Cantidad("""+str(len(NombreColumnas))+""") y SubColumnasDatos Cantidad("""+str(len(SubColumnasDatos))+""")""")

def ProcesarSubDatos(SubColumnasDatos, countCol, col, row):
    columna = ""
    if SubColumnasDatos != False:
        tup = SubColumnasDatos[countCol]
        if tup != False:
            if len(tup) == 4:
                try:
                    columna = row[tup[0]][tup[1]][tup[2]]
                except Exception as ex:
                    try:
                        columna = tup[3]
                        if columna.count('<'):
                            columnanombre = tup[3].split('<')
                            columna = row[columnanombre[1]]
                        PCampo = row[tup[0]]
                        formato = type(PCampo).__name__

                        if formato == 'dict':
                            SCampo = PCampo[tup[1]]
                            formato2 = type(SCampo).__name__
                            if formato2 == 'dict':
                                columna = SCampo[tup[2]]
                            elif formato2 == 'list':
                                for Json in SCampo:
                                    columna = Json[tup[2]]

                        elif formato == 'list':
                            for Json in PCampo:
                                SCampo = Json[tup[1]]

                                formato2 = type(SCampo).__name__
                                if formato2 == 'dict':
                                    columna = SCampo[tup[2]]
                                elif formato2 == 'list':
                                    for Json in SCampo:
                                        columna = Json[tup[2]]

                    except Exception as ex:
                        columna = tup[2]
            else:
                try:
                    columna = row[tup[0]][tup[1]]
                except Exception as ex:
                    try:
                        columna = tup[2]
                        if columna.count('<'):
                            columnanombre = tup[2].split('<')
                            columna = row[columnanombre[1]]

                        for Json in row[tup[0]]:
                            columna = Json[tup[1]]
                    except Exception as ex:
                        columna = tup[2]
        else:
            columna = row[col]
    else:
        columna = row[col]
    
    return columna


def SubDatosMarcar(SubColumnasDatos, DatosColumnas, col, row):
    """
    Obtiene datos anidados para marcar filas condicionalmente.
    
    Extrae valores de estructuras de datos anidadas para su uso en la función MarcarFilas,
    permitiendo aplicar estilos condicionales basados en valores de datos complejos.
    Maneja múltiples niveles de anidamiento y tipos de datos (diccionarios y listas).
    
    Args:
        SubColumnasDatos: Configuración para acceso a datos anidados
        DatosColumnas: Tupla con los nombres de las columnas
        col: Nombre de la columna/clave a extraer
        row: Diccionario con los datos de la fila actual
        
    Returns:
        Valor extraído de la estructura anidada para comparación en marcado condicional
    """
    columna = ""
    countCol = 0
    
    for nombrecol in DatosColumnas:
        if col == nombrecol:
            break
        countCol += 1
    
    if SubColumnasDatos != False:
        tup = SubColumnasDatos[countCol]
        if tup != False:
            if len(tup) == 4:
                try:
                    columna = row[tup[0]][tup[1]][col]
                except Exception as ex:
                    try:
                        columna = tup[3]
                        if '<' in columna:
                            columnanombre = tup[3].split('<')
                            columna = row[columnanombre[1]]
                        PCampo = row[tup[0]]
                        formato = type(PCampo).__name__

                        if formato == 'dict':
                            SCampo = PCampo[tup[1]]
                            formato2 = type(SCampo).__name__
                            if formato2 == 'dict':
                                columna = SCampo[col]
                            elif formato2 == 'list':
                                for Json in SCampo:
                                    columna = Json[col]

                        elif formato == 'list':
                            for Json in PCampo:
                                SCampo = Json[tup[1]]

                                formato2 = type(SCampo).__name__
                                if formato2 == 'dict':
                                    columna = SCampo[col]
                                elif formato2 == 'list':
                                    for Json in SCampo:
                                        columna = Json[col]

                    except Exception as ex:
                        columna = col
            else:
                try:
                    columna = row[tup[0]][col]
                except Exception as ex:
                    try:
                        columna = tup[2]
                        if '<' in columna:
                            columnanombre = tup[2].split('<')
                            columna = row[columnanombre[1]]

                        for Json in row[tup[0]]:
                            columna = Json[col]
                    except Exception as ex:
                        columna = col
        else:
            columna = row[col]
    else:
        columna = row[col]
    
    return columna

def process_nested_data(tup, row):
    """
    Procesa datos anidados de forma optimizada utilizando Polars.
    
    Extrae valores de estructuras de datos anidadas con optimizaciones para
    mejorar el rendimiento en conjuntos de datos grandes, utilizando acceso
    directo cuando es posible y mecanismos de fallback cuando no lo es.
    
    Args:
        tup: Tupla de configuración para acceso a datos anidados
        row: Diccionario con los datos de la fila actual
        
    Returns:
        Valor extraído de la estructura anidada o cadena vacía si no se encuentra
    """
    if len(tup) == 4:
        try:
            return row[tup[0]][tup[1]][tup[2]]
        except (KeyError, TypeError, IndexError):
            pass
        
        if '<' in tup[3]:
            campo_alternativo = tup[3].split('<')[1]
            return row.get(campo_alternativo, "")
        
        return recursive_access(row, tup)

    else:
        try:
            return row[tup[0]][tup[1]]
        except (KeyError, TypeError, IndexError):
            pass
        
        return row.get(tup[0], "")

def recursive_access(row, tup):
    """
    Proporciona acceso recursivo a datos anidados con manejo de errores.
    
    Navega estructuras de datos anidadas de forma segura, verificando tipos
    en cada nivel y manejando casos especiales como listas de diccionarios.
    
    Args:
        row: Diccionario con los datos de la fila actual
        tup: Tupla de configuración para acceso a datos anidados
        
    Returns:
        Valor extraído de la estructura anidada o cadena vacía si no se encuentra
    """
    try:
        primer_campo = row.get(tup[0], {})
        if isinstance(primer_campo, dict):
            segundo_campo = primer_campo.get(tup[1], {})
            if isinstance(segundo_campo, dict):
                return segundo_campo.get(tup[2], "")
            elif isinstance(segundo_campo, list):
                return next((item[tup[2]] for item in segundo_campo if isinstance(item, dict)), "")
    except Exception:
        return ""
    return ""





def ProcesarSubFilas(SubFilas, row, FilasPlus: t.Union[list, bool] = False):
    """
    Procesa las subfilas de una tabla y genera el HTML correspondiente.
    
    Genera tablas anidadas dentro de una fila principal, permitiendo mostrar
    datos relacionados en una estructura jerárquica. Maneja múltiples configuraciones
    de datos anidados y aplica formatos según la configuración. Mantiene la estructura
    de datos original sin convertir a DataFrames.
    
    Args:
        SubFilas: Configuración para las subfilas (nombres, columnas, datos, formatos)
        row: Diccionario con los datos de la fila principal
        FilasPlus: Configuración opcional para filas adicionales anidadas
        
    Returns:
        str: HTML generado para las subfilas anidadas
        
    Raises:
        Exception: Captura y maneja excepciones durante el procesamiento
    """
    try:
        tupNomb = SubFilas[0]
        tupDtCol = SubFilas[1]
        DtLista = SubFilas[2]
        Html = ""
        FilasTD = ""
        ColumnasTH = ""
        
        for col in tupNomb:
            ColumnasTH += '<th>'+col+'</th>'
            
        for Tupl in DtLista:
            try:
                tupDatos = Tupl
                tupFrt = SubFilas[3] if len(SubFilas) == 4 else False
                PCampo = row[tupDatos[0]]
                SCampo = None
                
                if len(tupDatos) == 3:
                    if PCampo != [] and PCampo != {}:
                        formato = type(PCampo).__name__
                        if formato == 'dict':
                            SCampo = PCampo[tupDatos[1]]
                        elif formato == 'list':
                            for Json in PCampo:
                                SCampo = Json[tupDatos[1]]
                                break
                    
                        Datos = SCampo
                        DatosColumnas = tupDtCol
                        FormatoColumnas = tupFrt
                    else:
                        TCampoTup = tupDatos[2]
                        PCampo = row[TCampoTup[0]]
                        if len(TCampoTup) == 2:
                            formato = type(PCampo).__name__
                            if formato == 'dict':
                                SCampo = PCampo[TCampoTup[1]]
                            elif formato == 'list':
                                for Json in PCampo:
                                    SCampo = Json[TCampoTup[1]]
                                    break
                            Datos = SCampo
                            DatosColumnas = tupDtCol
                            FormatoColumnas = tupFrt
                        elif len(TCampoTup) == 1:
                            Datos = PCampo
                            DatosColumnas = tupDtCol
                            FormatoColumnas = tupFrt
                elif len(tupDatos) == 2:
                    formato = type(PCampo).__name__
                    if formato == 'dict':
                        SCampo = PCampo[tupDatos[1]]
                    elif formato == 'list':
                        for Json in PCampo:
                            SCampo = Json[tupDatos[1]]
                            break
                    Datos = SCampo
                    DatosColumnas = tupDtCol
                    FormatoColumnas = tupFrt
                elif len(tupDatos) == 1:
                    Datos = PCampo
                    DatosColumnas = tupDtCol
                    FormatoColumnas = tupFrt
                    
                FilasTD += HtmlSubfilas(Datos, DatosColumnas, FormatoColumnas, FilasPlus)
            except Exception as ex:
                FilasTD += ""
                pass
                
        Html = f"""
        <tr>
            <td colspan="12">
                <table class="table" style="width:99.5%;margin-left: 10px;">
                    <tr style="background-color: #c9dadda1;">
                        {ColumnasTH}
                    </tr>
                    {FilasTD}
                </table>
            </td>
        </tr>
        """
        return Html
    except Exception as e:
        EscribirLog(f"Error procesando las subfilas: {str(e)}")
        return f"Error procesando las subfilas: {e}"



def HtmlSubfilas(Datos: t.Union[list, dict],
                 DatosColumnas: t.Union[tuple, tuple], FormatoColumnas: t.Union[tuple, bool] = False, FilasPlus: t.Union[list, bool] = False):
    """
    Genera el HTML para las filas de una subtabla basado en los datos proporcionados.
    
    Convierte datos en formato diccionario o lista de diccionarios en filas HTML para
    subtablas, aplicando formatos si están especificados y procesando configuraciones
    adicionales como FilasPlus. Mantiene la estructura de datos original sin convertir a DataFrames.
    
    Args:
        Datos: Diccionario o lista de diccionarios con los datos a mostrar
        DatosColumnas: Tupla con los nombres de las claves en los diccionarios
        FormatoColumnas: Configuración opcional de formatos para las columnas
        FilasPlus: Configuración opcional para filas adicionales anidadas
        
    Returns:
        str: HTML generado para las filas de la subtabla
    """
    countCol = 0
    FilasTD = ""
    formato = type(Datos).__name__

    if formato == 'dict':
        FilasTD += _procesar_dict_filas(Datos, DatosColumnas, FormatoColumnas, FilasPlus)
    elif formato == 'list':
        for row in Datos:
            FilasTD += _procesar_dict_filas(row, DatosColumnas, FormatoColumnas, FilasPlus)

    return FilasTD

def _procesar_dict_filas(row, DatosColumnas, FormatoColumnas, FilasPlus):
    """
    Genera el HTML para una fila de tabla a partir de un diccionario de datos.
    
    Convierte un diccionario en una fila HTML, aplicando formatos si están especificados
    y procesando configuraciones adicionales como FilasPlus. Función auxiliar utilizada
    por HtmlSubfilas para procesar cada fila individual.
    Mantiene la estructura de datos original sin convertir a DataFrames.
    
    Args:
        row: Diccionario con los datos de la fila
        DatosColumnas: Tupla con los nombres de las claves en el diccionario
        FormatoColumnas: Configuración opcional de formatos para las columnas
        FilasPlus: Configuración opcional para filas adicionales anidadas
        
    Returns:
        str: HTML generado para una fila de tabla
    """
    countCol = 0
    ColumnasTD = ""
    style = "background-color: #e9f1f5;" if FilasPlus != False else ""
    FilasTD = f"<tr style='{style}'>"

    for col in DatosColumnas:
        columna = row.get(col, "")
        if FormatoColumnas:
            columna = Formatos(FormatoColumnas, countCol, columna)

        ColumnasTD += f"<td class='text-wrap'>{str(columna)}</td>"
        countCol += 1

    if FilasPlus != False:
        FilasTD += ColumnasTD
        DtFilasPlus = ProcesarFilasPlus(FilasPlus, row)
        FilasTD += DtFilasPlus + "</tr>"
    else:
        FilasTD += ColumnasTD + "</tr>"

    return FilasTD

def ProcesarFilasPlus(FilasPlus, row):
    """
    Procesa filas adicionales anidadas y genera el HTML correspondiente.
    
    Crea una tabla anidada adicional dentro de una fila principal o subfila,
    permitiendo mostrar datos relacionados en una estructura jerárquica más compleja.
    Maneja múltiples configuraciones de datos anidados y aplica formatos.
    Mantiene la estructura de datos original sin convertir a DataFrames.
    
    Args:
        FilasPlus: Configuración para las filas adicionales (nombres, columnas, datos, formatos)
        row: Diccionario con los datos de la fila principal
        
    Returns:
        str: HTML generado para las filas adicionales anidadas
    """
    tupNomb, tupDtCol, DtLista = FilasPlus[0], FilasPlus[1], FilasPlus[2]
    Html = ""
    FilasTD = ""
    ColumnasTH = ""
    
    ColumnasTH = ''.join(f'<th>{col}</th>' for col in tupNomb)

    for Tupl in DtLista:
        try:
            tupDatos = Tupl
            tupFrt = FilasPlus[3] if len(FilasPlus) == 4 else False
            PCampo = row.get(tupDatos[0], None)
            SCampo = None

            if PCampo:
                if len(tupDatos) == 3:
                    SCampo = obtener_datos_anidados(PCampo, tupDatos[1])
                    Datos = SCampo
                    DatosColumnas = tupDtCol
                    FormatoColumnas = tupFrt
                elif len(tupDatos) == 2:
                    SCampo = obtener_datos_anidados(PCampo, tupDatos[1])
                    Datos = SCampo
                    DatosColumnas = tupDtCol
                    FormatoColumnas = tupFrt
                else:
                    Datos = PCampo
                    DatosColumnas = tupDtCol
                    FormatoColumnas = tupFrt
                
                FilasTD += HtmlfilasPlus(Datos, DatosColumnas, FormatoColumnas)
        except Exception as ex:
            EscribirLog(f"Error en filas plus: {str(ex)}")
            FilasTD += "<tr><td colspan='12'></td></tr>"

    Html = f"""
    <tr>
        <td colspan="12">
            <table class="table" style="width:99.5%;margin-left: 10px;">
                <tr style="background-color: #dde7e9a1;">
                    {ColumnasTH}
                </tr>
                {FilasTD}
            </table>
        </td>
    </tr>
    """
    return Html

def obtener_datos_anidados(PCampo, clave):
    """
    Obtiene datos anidados de diccionarios o listas de forma segura.
    
    Extrae valores de estructuras de datos anidadas, manejando diferentes tipos
    de datos (diccionarios y listas) de forma segura y devolviendo None si no
    se encuentra el valor solicitado.
    
    Args:
        PCampo: Estructura de datos (diccionario o lista) a acceder
        clave: Clave a buscar en la estructura de datos
        
    Returns:
        Valor encontrado o None si no existe
    """
    if isinstance(PCampo, dict):
        return PCampo.get(clave, None)
    elif isinstance(PCampo, list):
        for item in PCampo:
            if isinstance(item, dict):
                if clave in item:
                    return item[clave]
    return None

def HtmlfilasPlus(Datos: t.Union[list, dict],
                  DatosColumnas: t.Union[tuple, tuple], 
                  FormatoColumnas: t.Union[tuple, bool] = False):
    """
    Genera el HTML para filas adicionales en tablas anidadas.
    
    Convierte datos en formato diccionario o lista de diccionarios en filas HTML
    para tablas anidadas adicionales (FilasPlus), aplicando formatos si están
    especificados. Maneja tanto datos individuales como colecciones.
    Mantiene la estructura de datos original sin convertir a DataFrames.
    
    Args:
        Datos: Diccionario o lista de diccionarios con los datos a mostrar
        DatosColumnas: Tupla con los nombres de las claves en los diccionarios
        FormatoColumnas: Configuración opcional de formatos para las columnas
        
    Returns:
        str: HTML generado para las filas adicionales
    """
    countCol = 0
    FilasTD = ""
    formato = type(Datos).__name__

    if formato == 'dict':
        FilasTD = "<tr>"
        for col in DatosColumnas:
            columna = Datos.get(col, "")
            if FormatoColumnas:
                columna = Formatos(FormatoColumnas, countCol, columna)
            FilasTD += f"<td class='text-wrap'>{str(columna)}</td>"
            countCol += 1
        FilasTD += "</tr>"

    elif formato == 'list':
        for row in Datos:
            countCol = 0  # Reiniciar el contador para cada fila
            FilasTD += "<tr class='CursorPointer'>"
            for col in DatosColumnas:
                columna = row.get(col, "")
                if FormatoColumnas:
                    columna = Formatos(FormatoColumnas, countCol, columna)
                FilasTD += f"<td class='text-wrap'>{str(columna)}</td>"
                countCol += 1
            FilasTD += "</tr>"

    return FilasTD



def aplicar_formato_lote(datos: List[str], formato: str) -> List[str]:
    """
    Aplica formato a un lote de datos utilizando operaciones vectorizadas para optimizar rendimiento.
    
    Utiliza Polars para procesamiento vectorizado de grandes conjuntos de datos,
    aplicando diferentes formatos (moneda, fecha, encriptación, etc.) de manera eficiente.
    Optimizado para alto rendimiento con grandes volúmenes de datos.
    
    Args:
        datos: Lista de valores a formatear
        formato: Tipo de formato a aplicar ('moneda', 'date', 'datetime', 'encriptar', 'zfill_N')
        
    Returns:
        List[str]: Lista de valores formateados
    """
    # Procesamos la lista directamente sin usar DataFrames
    if not datos:
        return datos
    
    if formato == 'moneda':
        try:
            # Convertir a float y aplicar formato de moneda
            return [Tools.FormatoMoneda(float(val) if val is not None else 0) for val in datos]
        except Exception as e:
            print(f"Error en formato moneda: {e}")
            return datos

    elif formato == 'date':
        try:
            # Aplicar formato de fecha
            return [Tools.DateFormat(val) for val in datos]
        except Exception as e:
            print(f"Error en formato date: {e}")
            return datos

    elif formato == 'datetime':
        try:
            # Aplicar formato de fecha y hora
            return [Tools.DateTimeFormat(val) for val in datos]
        except Exception as e:
            print(f"Error en formato datetime: {e}")
            return datos

    elif formato == 'encriptar':
        try:
            # Aplicar encriptación
            return [Tools.Encriptar(val) for val in datos]
        except Exception as e:
            print(f"Error en formato encriptar: {e}")
            return datos

    elif 'zfill' in formato:
        try:
            long = formato.split('_')
            if len(long) > 1:
                relleno = Tools.StrToInt(long[1])
                # Rellenar con ceros a la izquierda
                return [str(val).zfill(relleno) for val in datos]
        except Exception as e:
            print(f"Error en zfill: {e}")
            return datos
    
    # Si no hay formato o no coincide con ninguno, devolver los datos sin cambios
    return datos

_FORMAT_STRATEGIES = {
    'date': lambda x: Tools.DateFormat(x),
    'datetime': lambda x: Tools.DateTimeFormat(x),
    'moneda': lambda x: Tools.FormatoMoneda(x),
    'encriptar': lambda x: Tools.Encriptar(x)
}

@lru_cache(maxsize=1024)
def Formatos(FormatoColumnas, countCol, columna):
    """
    Aplica formato a un valor de columna con optimizaciones de rendimiento.
    
    Formatea valores de celdas según la configuración especificada, utilizando
    estrategias optimizadas como caché, vectorización y diccionarios de funciones.
    Maneja tanto valores individuales como colecciones (listas, arrays).
    
    Args:
        FormatoColumnas: Configuración de formatos para las columnas
        countCol: Índice de la columna actual
        columna: Valor a formatear
        
    Returns:
        Valor formateado según la configuración especificada
    """
    if not FormatoColumnas or countCol >= len(FormatoColumnas):
        return columna
    
    formato = str(FormatoColumnas[countCol])
    
    if columna is None or columna == '':
        return ''
    
    if isinstance(columna, (list, np.ndarray)) and len(columna) > 0:
        if formato in VECTOR_FORMAT_HANDLERS:
            return VECTOR_FORMAT_HANDLERS[formato](columna)
        elif 'zfill' in formato:
            try:
                long = formato.split('_')
                if len(long) > 1:
                    relleno = Tools.StrToInt(long[1])
                    vectorized_zfill = np.vectorize(lambda x: str(x).zfill(relleno))
                    return vectorized_zfill(columna)
            except Exception:
                pass
        return columna
    
    if formato in _FORMAT_STRATEGIES:
        return _FORMAT_STRATEGIES[formato](columna)
    
    if 'zfill' in formato:
        try:
            long = formato.split('_')
            if len(long) > 1:
                return str(columna).zfill(Tools.StrToInt(long[1]))
        except Exception:
            pass
    
    return columna



@lru_cache(maxsize=16)
def _format_cached(value, format_type):
    """
    Versión con caché de las funciones de formato para mejorar rendimiento.
    
    Aplica diferentes formatos a valores utilizando caché para evitar
    cálculos repetidos con los mismos valores de entrada, optimizando
    el rendimiento en operaciones frecuentes.
    
    Args:
        value: Valor a formatear
        format_type: Tipo de formato a aplicar ('date', 'datetime', 'moneda', etc.)
        
    Returns:
        Valor formateado según el tipo especificado
    """
    if format_type == 'date':
        return Tools.DateFormat(value)
    elif format_type == 'datetime':
        return Tools.DateTimeFormat(value)
    elif format_type == 'moneda':
        return Tools.FormatoMoneda(value)
    elif format_type == 'entero':
        return Tools.StrToInt(value)
    elif format_type == 'decimal':
        return Tools.FormatterNumber(value)
    return value

def CrearTablaReport(Datos: t.Union[list, list],
                     NombreColumnas: t.Union[tuple, tuple] = None,
                     DatosColumnas: t.Union[tuple, tuple] = None,
                     ClassColumnas: t.Union[tuple, tuple] = None,
                     FormatoColumnas: t.Union[tuple, bool] = False,
                     TotalizarColumnas: t.Union[tuple, bool] = False,
                     ColumnasJson: t.Union[list, dict] = None,
                     SubColumnasDatos: t.Union[list, bool] = False,
                     SubFilas: t.Union[list, bool] = False,
                     FilasPlus: t.Union[list, bool] = False,
                     MarcarRows:t.Union[tuple, bool] = False,conteo=True,progressBar=False,sessionidusuario = None):

    resultado = CrearTabla(Datos=Datos,
                     NombreColumnas=NombreColumnas,
                     DatosColumnas=DatosColumnas,
                     ClassColumnas=ClassColumnas,
                     FormatoColumnas=FormatoColumnas,
                     TotalizarColumnas=TotalizarColumnas,
                     ColumnasJson=ColumnasJson,
                     SubColumnasDatos=SubColumnasDatos,
                     SubFilas=SubFilas,
                     FilasPlus=FilasPlus,
                     MarcarRows=MarcarRows,
                     conteo=conteo,
                     progressBar=progressBar,
                     sessionidusuario = sessionidusuario,
                     reporte=True)
    
    # Validar el tipo de retorno de CrearTabla
    if isinstance(resultado, tuple):
        if len(resultado) == 2:
            # Puede ser (html, totales) o (html, HtmlReporte)
            if TotalizarColumnas and not isinstance(TotalizarColumnas, bool) and any(TotalizarColumnas):
                # Es (html, totales)
                _, totales, HtmlReporte = resultado
                return HtmlReporte, totales
            else:
                # Es (html, HtmlReporte)
                _, HtmlReporte = resultado
                return HtmlReporte
        elif len(resultado) == 3:
            # Es (html, totales, HtmlReporte)
            _, totales, HtmlReporte = resultado
            return HtmlReporte, totales
    else:
        # Solo devolvió html
        return resultado

def TableVacia(NombreColumnas=(), ColumnasJson=(),
               ClassColumnas=(), Titulo="Detalle", idtable="table"):
    

    Html = f"""
        <div class="card" style="margin-bottom: 0px; margin-top:5px;">
        <div class="card-header bg-info text-center" style="font-size: 20px; color: #FFF; padding-top: 5px; padding-bottom: 5px;">
            <span class="fa fa-th-list"></span>
            <span>{Titulo}</span>
        </div>
        <div class="table-responsive AlturaGrid">
        <table class="table table-bordered table-hover table-condensed table-striped" id='{idtable}'>
        <thead>
        </thead>
        <tbody class="text-center">
              <div class='text-center'>NO SE ENCONTRARON DATOS.</div>
        </tbody>
        </table>
        </div>
        </div>
    """
    return Html

@bp.route('/<RUTA_TABLA>_ps', methods = ['POST'])
def PaginacionServer_ps(RUTA_TABLA):
    try:
        data = Tools.OptenerDatos(request)
        page: int = data['page']
        ps_idusuario: int = Tools.StrToInt(data['ps_idusuario']) # el idusuario por el que se va a buscar a la base de datos
        dt_pagina = find_paginacion(RUTA_TABLA, ps_idusuario, page)
        datos = dt_pagina['paginas']
        
        # Verificar y eliminar ps_paginando para evitar duplicados
        parametros = dt_pagina['parametros_tabla'].copy()
        if 'total_rows' in parametros:
            del parametros['total_rows']
        if 'ps_paginando' in parametros:
            del parametros['ps_paginando']
        
        parametros['reporte'] = False
        
        # Obtener los totales almacenados en la paginación (calculados en la carga inicial)
        totales_originales = dt_pagina.get('totales', {})
        
        # Registrar información detallada para depuración - usar el parámetro local
        EscribirLog(f"Paginando tabla: Página {page}, Datos: {len(datos)} registros")
        EscribirLog(f"Totales recuperados de la BD: {totales_originales}")
        
        html = CrearTabla(
            datos,
            **parametros,
            ps_conteo = dt_pagina['total_conteo'],
            ps_func = RUTA_TABLA,  # Ya estamos usando el parámetro correcto de la función
            ps_current_active_page = page,
            ps_paginando = True
        )
        
        # Convertir html a solo el contenido si es una tupla
        if isinstance(html, tuple):
            html = html[0]
        
        # Siempre devolver el Tvalor como valor numérico sin formatear
        Tvalor = '0.00'
        if totales_originales:
            # Primero intentar obtener Tvalor directamente
            if 'Tvalor' in totales_originales:
                # Enviar como string pero sin formato de moneda
                Tvalor = str(totales_originales.get('Tvalor', 0))
            # Si no está disponible, intentar calcularlo desde valor
            elif 'valor' in totales_originales:
                # Enviar como string pero sin formato de moneda
                Tvalor = str(totales_originales.get('valor', 0))
        
        EscribirLog(f"Usando Tvalor sin formato: {Tvalor}")
        return Tools.MensajeV2(html=html, Tvalor=Tvalor)
    except Exception as e:
        EscribirLog(f"Error en PaginacionServer_ps: {str(e)}")
        return Tools.MensajeV2(e=e)