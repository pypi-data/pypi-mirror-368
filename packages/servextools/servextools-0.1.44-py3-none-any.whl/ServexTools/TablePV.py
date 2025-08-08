import ServexTools.Tools as Tools
import typing as t

def CrearFila(nombreClase, NumeralTabla, style, RespuestaValidacion):
    Fila = "<tr id='rows_"+NumeralTabla + "' class='"+nombreClase+" CursorPointer "+RespuestaValidacion+"' style='"+style+"'>"
    return Fila

def MarcarFilas(MarcarRows, SubColumnasDatos, DatosColumnas,row):
            while(True):
                campoValidar=MarcarRows[0]
                ValorValidar=MarcarRows[1]
                EntoncesValidacion=MarcarRows[2]
                ContrarioValidacion=MarcarRows[3]
                formato = type(ContrarioValidacion).__name__
                valor =SubDatosMarcar(SubColumnasDatos, DatosColumnas, campoValidar, row)
                if valor==ValorValidar:
                    return EntoncesValidacion
                else:
                    if formato == 'tuple':
                        MarcarRows=ContrarioValidacion
                    else:
                        return ContrarioValidacion

def CondicionParaTotalizar(ColumnaTotales, SubColumnasDatos, DatosColumnas,row):
    campoValidar=ColumnaTotales[0]
    ValorValidar=ColumnaTotales[1]
    valor =SubDatosMarcar(SubColumnasDatos, DatosColumnas, campoValidar, row)
    if valor==ValorValidar:
        return False
    else:
        return True

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

def SubDatosMarcar(SubColumnasDatos, DatosColumnas,col,row):
    columna = ""
    countCol = 0
    for nombrecol in DatosColumnas:
        if col==nombrecol:
            break
        countCol+=1
    if SubColumnasDatos != False:
        tup = SubColumnasDatos[countCol]
        if tup != False:
            if len(tup) == 4:
                try:
                    columna = row[tup[0]][tup[1]][col]
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
                        if columna.count('<'):
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

def ProcesarSubFilas(SubFilas, row,FilasPlus: t.Union[list, bool] = False):
    #Subfilas=[("Documento","Tipo", "Valor"),("documento","tipo", "valor"),[('c'),('cxp','detalle',('cxp','p')),('nd'),('prod'),('nc','detalle')]]
    tupNomb = SubFilas[0]
    tupDtCol = SubFilas[1]
    DtLista = SubFilas[2]
    Html=""
    FilasTD = ""
    ColumnasTH = ""
    for col in tupNomb:
        ColumnasTH += '<th class="text-uppercase text-bold">'+col+'</th>'
        
    for Tupl in DtLista:
        try:
            tupDatos = Tupl
            tupFrt = SubFilas[3] if len(SubFilas) == 4 else False
            PCampo = row[tupDatos[0]]
            SCampo=None
            if len(tupDatos) == 3:
                if PCampo!=[] and PCampo !={}:
                    formato = type(PCampo).__name__
                    if formato == 'dict':
                        SCampo = PCampo[tupDatos[1]]

                    elif formato == 'list':
                        for Json in PCampo:
                            SCampo = Json[tupDatos[1]]
                            break
                
                    Datos=SCampo
                    DatosColumnas=tupDtCol
                    FormatoColumnas=tupFrt
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

                        Datos=SCampo
                        DatosColumnas=tupDtCol
                        FormatoColumnas=tupFrt
                    elif len(TCampoTup) == 1:
                        Datos=PCampo
                        DatosColumnas=tupDtCol
                        FormatoColumnas=tupFrt
            elif len(tupDatos) == 2:
                formato = type(PCampo).__name__
                if formato == 'dict':
                    SCampo = PCampo[tupDatos[1]]

                elif formato == 'list':
                    for Json in PCampo:
                        SCampo = Json[tupDatos[1]]
                        break

                Datos=SCampo
                DatosColumnas=tupDtCol
                FormatoColumnas=tupFrt
            elif len(tupDatos) == 1:
                Datos=PCampo
                DatosColumnas=tupDtCol
                FormatoColumnas=tupFrt
                
            FilasTD+= HtmlSubfilas(Datos,DatosColumnas,FormatoColumnas,FilasPlus)
        except Exception as ex:
            FilasTD+=""
            pass
            
    Html = """
    <tr>
        <td colspan="12">
            <table class="table" style="width:99.5%;margin-left: 10px;">
                <tr style="">
                    """+ColumnasTH+"""
                </tr>
                """+FilasTD+"""
            </table>
        </td>
    </tr>
    """
    return Html
        
def HtmlSubfilas(Datos: t.Union[list, dict],
                 DatosColumnas: t.Union[tuple, tuple], FormatoColumnas: t.Union[tuple, bool] = False,FilasPlus: t.Union[list, bool] = False):
    
    countCol = 0
    ColumnasTD = ""
    FilasTD = ""
    formato = type(Datos).__name__
    if formato == 'dict':
        row = Datos
        FilasTD += "<tr style=''>"
        for col in DatosColumnas:
            columna = row[col]
            if FormatoColumnas != False:
                columna = Formatos(FormatoColumnas, countCol, columna)

            ColumnasTD += "<td class='text-wrap'>"+str(columna)+"</td>"
            countCol += 1

        if FilasPlus != False:
            FilasTD += ColumnasTD 
            # Dt, NombColumnas, DtColumnas, FrtColumnas=ProcesarSub(FilasPlus, row)
            # DtFilasPlus = HtmlfilasPlus(Datos=Dt, NombreColumnas=NombColumnas, DatosColumnas=DtColumnas, FormatoColumnas=FrtColumnas)
            DtFilasPlus = ProcesarFilasPlus(FilasPlus,row)
            
            FilasTD += DtFilasPlus+"</tr>"
        else:
            FilasTD += ColumnasTD+"</tr>"
        ColumnasTD = ""
        countCol = 0

    elif formato == 'list':
        for row in Datos:
            FilasTD += "<tr style=''>"
            for col in DatosColumnas:
                columna = row[col]
                if FormatoColumnas != False:
                    columna = Formatos(FormatoColumnas, countCol, columna)

                ColumnasTD += "<td class='text-wrap'>"+str(columna)+"</td>"
                countCol += 1
            if FilasPlus != False:
                FilasTD += ColumnasTD 
                # Dt, NombColumnas, DtColumnas, FrtColumnas=ProcesarSub(FilasPlus, row)
                # DtFilasPlus = HtmlfilasPlus(Datos=Dt, NombreColumnas=NombColumnas, DatosColumnas=DtColumnas, FormatoColumnas=FrtColumnas)
                DtFilasPlus = ProcesarFilasPlus(FilasPlus,row)
                FilasTD += DtFilasPlus+"</tr>"
            else:
                FilasTD += ColumnasTD+"</tr>"
                
            ColumnasTD = ""
            countCol = 0

    return FilasTD

def ProcesarFilasPlus(FilasPlus, row):
    #filasPlus=[("Cod.Pro", "Descripcion"),("idproducto", "descripcion"),[('p'),('c','detalle',('c','p')),('nd'),('prod'),('nc','detalle')]]
    tupNomb = FilasPlus[0]
    tupDtCol = FilasPlus[1]
    DtLista = FilasPlus[2]
    Html=""
    FilasTD = ""
    ColumnasTH = ""
    for col in tupNomb:
        ColumnasTH += '<th class="text-uppercase text-bold">'+col+'</th>'
        
    for Tupl in DtLista:
        try:
            tupDatos = Tupl
            tupFrt = FilasPlus[3] if len(FilasPlus) == 4 else False
            PCampo = row[tupDatos[0]]
            SCampo=None
            if len(tupDatos) == 3:
                if PCampo!=[] and PCampo !={}:
                    formato = type(PCampo).__name__
                    if formato == 'dict':
                        SCampo = PCampo[tupDatos[1]]

                    elif formato == 'list':
                        for Json in PCampo:
                            SCampo = Json[tupDatos[1]]
                            break
                
                    Datos=SCampo
                    DatosColumnas=tupDtCol
                    FormatoColumnas=tupFrt
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

                        Datos=SCampo
                        DatosColumnas=tupDtCol
                        FormatoColumnas=tupFrt
                    elif len(TCampoTup) == 1:
                        Datos=PCampo
                        DatosColumnas=tupDtCol
                        FormatoColumnas=tupFrt
            elif len(tupDatos) == 2:
                formato = type(PCampo).__name__
                if formato == 'dict':
                    SCampo = PCampo[tupDatos[1]]

                elif formato == 'list':
                    for Json in PCampo:
                        SCampo = Json[tupDatos[1]]
                        break

                Datos=SCampo
                DatosColumnas=tupDtCol
                FormatoColumnas=tupFrt
            elif len(tupDatos) == 1:
                Datos=PCampo
                DatosColumnas=tupDtCol
                FormatoColumnas=tupFrt
            FilasTD+= HtmlfilasPlus(Datos,DatosColumnas,FormatoColumnas)
        except Exception as ex:
            FilasTD+=""
            pass
    
    Html = """
    <tr>
        <td colspan="12">
            <table class="table" style="width:99.5%;margin-left: 10px;">
                <tr style="font-size: 13px;">
                    """+ColumnasTH+"""
                </tr>
                """+FilasTD+"""
            </table>
        </td>
    </tr>
    """
    return Html

def HtmlfilasPlus(Datos: t.Union[list, dict],
                 DatosColumnas: t.Union[tuple, tuple], FormatoColumnas: t.Union[tuple, bool] = False):
    
    countCol = 0
    ColumnasTD = ""
    FilasTD = ""
    formato = type(Datos).__name__

    if formato == 'dict':
        row = Datos
        FilasTD += "<tr>"
        for col in DatosColumnas:
            columna = row[col]
            if FormatoColumnas != False:
                columna = Formatos(FormatoColumnas, countCol, columna)

            ColumnasTD += "<td class='text-wrap'>"+str(columna)+"</td>"
            countCol += 1

        FilasTD += ColumnasTD+"</tr>"
        ColumnasTD = ""
        countCol = 0

    elif formato == 'list':
        for row in Datos:
            FilasTD += "<tr class='CursorPointer'>"
            for col in DatosColumnas:
                columna = row[col]
                if FormatoColumnas != False:
                    columna = Formatos(FormatoColumnas, countCol, columna)

                ColumnasTD += "<td class='text-wrap'>"+str(columna)+"</td>"
                countCol += 1

            FilasTD += ColumnasTD+"</tr>"
            ColumnasTD = ""
            countCol = 0

    return FilasTD

def Formatos(FormatoColumnas, countCol, columna):
    formato = str(FormatoColumnas[countCol])
    if formato == "date":
        columna = Tools.DateFormat(columna)
    if formato == "datetime":
        columna = Tools.DateTimeFormat(columna)
    if formato == "moneda":
        columna = Tools.FormatoMoneda(columna)
    if formato == "encriptar":
        columna = Tools.Encriptar(columna)
    if formato.count("zfill"):
        long = formato.split('_')
        columna = str(columna).zfill(Tools.StrToInt(long[1]))
    return columna

def CrearTablaReport(Datos: t.Union[list, list],
                     NombreColumnas: t.Union[tuple, tuple],
                     DatosColumnas: t.Union[tuple, tuple],
                     ClassColumnas: t.Union[tuple, tuple],
                     FormatoColumnas: t.Union[tuple, bool] = False,
                     TotalizarColumnas: t.Union[tuple, bool] = False,
                     CondicionTotalizar: t.Union[tuple, bool] = False,
                     SubColumnasDatos: t.Union[list, bool] = False,
                     SubFilas: t.Union[list, bool] = False,
                     FilasPlus: t.Union[list, bool] = False,
                     MarcarRows:t.Union[tuple, bool] = False,conteo=True,Cabezera=True):

    ValidarLongitudDatos(NombreColumnas, DatosColumnas, ClassColumnas, FormatoColumnas, TotalizarColumnas, SubColumnasDatos)

    countCol = 0
    ColumnasTH = ""
    Totales = {}
    for col in NombreColumnas:
        ColumnasTH += '<th scope="col" class="text-uppercase text-bold border-bottom-top">'+col+'</th>'
        countCol += 1

    countCol = 0
    if TotalizarColumnas != False:
        for col in DatosColumnas:
            Totalizar = TotalizarColumnas[countCol]
            if Totalizar == True:
                Totales.update({
                    'T'+col: 0.00
                })
            countCol += 1

    countCol = 0
    countFilas = 0
    ColumnasTD = ""
    FilasTD = ""
    if Datos == [] or Datos is None:
        ColumnasTH = ''
        FilasTD = " <div class='text-center'>NO SE ENCONTRARON DATOS.</div>"
    else:
        for row in Datos:
            NumeralTabla = str(countFilas)
            style=""
            
            if MarcarRows != False:
                Respuesta=MarcarFilas(MarcarRows,SubColumnasDatos,DatosColumnas,row)
                FilasTD += CrearFila('', NumeralTabla, style, Respuesta)
            else:
                FilasTD += "<tr id='rows_"+NumeralTabla + "' class='' style='"+style+"'>"
            
            countFilas += 1
            for col in DatosColumnas:
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

                if FormatoColumnas != False:
                    columna = Formatos(FormatoColumnas, countCol, columna)

                if TotalizarColumnas != False:
                    Sumar = TotalizarColumnas[countCol]
                    condicion = CondicionParaTotalizar(CondicionTotalizar,SubColumnasDatos,DatosColumnas,row) if CondicionTotalizar != False else True
                    if Sumar == True and condicion==True:
                        Totales['T'+str(col)] += Tools.StrToFloat(columna)

                ColumnasTD += "<td id='"+col+"_"+NumeralTabla+"' class='" + ClassColumnas[countCol]+" text-wrap'>"+str(columna)+"</td>"
                countCol += 1

            if SubFilas != False:
                FilasTD += ColumnasTD
                DtSubFilas=ProcesarSubFilas(SubFilas=SubFilas, row=row,FilasPlus=FilasPlus)
                FilasTD += DtSubFilas+"</tr>"
            else:
                FilasTD += ColumnasTD+"</tr>"
                 
            #FilasTD += ColumnasTD+"</tr>"
            ColumnasTD = ""
            countCol = 0

    ConteoHtml=""
    if conteo:
        ConteoHtml="""<span class="badge text-bold" style="font-size: 12px;width: max-content; background-color: #000;">Conteo: """+str(countFilas)+"""</span>"""
    Cabecera="<br>" if Cabezera==False else """<div class="card-header text-center" style="font-size: 20px; color: #000; padding-top: 5px; padding-bottom: 5px; border:2px solid #000;">
            <span class="fa fa-th-list"></span>
            <span>Detalle</span>
        </div>""" 
    Html = """
        """+Cabecera+"""
        <div class="table-responsive">
        <table class="table" style="overflow: hidden;">
        <thead>
            <tr>
            """+ColumnasTH+"""
            </tr>
        </thead>
        <tbody>
            """+FilasTD+"""
        </tbody>
        </table>
        """+ConteoHtml+"""
        </div>
    """
    if TotalizarColumnas != False:
        return Html, Totales
    return Html

def CrearTablaReportHtmlCustom(cabeceras,filas):
    Html = """
            <div class="table-responsive mt-2">
            <table class="table" style="overflow: hidden;">
            <thead>
                """+cabeceras+"""
            </thead>
            <tbody>
                """+filas+"""
            </tbody>
            </table>
            </div>
    """
    return Html