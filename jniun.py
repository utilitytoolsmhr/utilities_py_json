from datetime import datetime


def int_fix(s: any, default = None):
    """ 
        Función que covierte un valor a un entero, en caso de que no sea un valor valido retorna un caracter vacio
    Args:
        s (any): Valor de tipo no especificado 

    Returns:
        _type_: int or any
    """
    try:
        return int(float(s)) 
    except (ValueError, TypeError):
        return s


def float_fix(n: any):
    """
    Intenta convertir el valor n a un número de punto flotante.
    
    Args:
    n: El valor que se intentará convertir a un número de punto flotante.
    
    Returns:
    Un número de punto flotante que representa el valor de n si es posible convertirlo, de lo contrario devuelve n.
    """
    try: 
        return float(n)
    except: 
        return n


def float_round_fix(n: any, r=2):
    """
    Intenta convertir el valor n a un número de punto flotante con solo r decimales sin aproximar.
    
    Args:
    n (any): El valor que se intentará convertir a un número de punto flotante con solo r decimales.
    r (int): La cantidad de decimales a mantener (por defecto 2).
    
    Returns:
    float: Un número de punto flotante con solo r decimales que representa el valor de n si es posible convertirlo, de lo contrario devuelve n.
    """
    if n:
        try:
            n = str(n)
            if "." in n:     
                integer_part, decimal_part = n.split('.')           
                return float(integer_part + "." + decimal_part[:r])
        except:
            return n
    return n


def text_fix(s: any):
    """
        Función que convierte un valor a String, si el valor es 'null' or 'NULL' retornará None
    Args:
        s (any): Valor de tipo no especificado 

    Returns:
        _type_: str or None
    """
    return str(s) if s is not None and str(s).lower() != 'null' else None

def moneda_fix(numero):
    """
    Funcion para formatear moneda
    """
    partes = str(numero).split('.')
    entero = partes[0]
    decimal = (partes[1] if len(partes) > 1 else '00')[:2]
    if len(decimal) == 1:
        decimal = decimal + '0'
    entero = entero[::-1]
    entero = ','.join(entero[i:i+3] for i in range(0, len(entero), 3))
    entero = entero[::-1]
    # return "RD$ " + entero + "." + decimal
    return entero + "." + decimal
    

def obj_fix(obj):
    if not isinstance(obj, dict):
        return obj  # Si no es un objeto, lo devuelve tal cual.
    fixed_obj = {}
    for key, value in obj.items():
        if isinstance(value, str):
            fixed_obj[key] = text_fix(value)
        elif isinstance(value, int):
            fixed_obj[key] = int_fix(value)
        elif isinstance(value, float):
            fixed_obj[key] = float_fix(value)
        elif isinstance(value, dict):
            fixed_obj[key] = obj_fix(value)  # Recursión para objetos anidados.
        else:
            fixed_obj[key] = value  # Otros tipos se mantienen igual.
    return fixed_obj

#Convierte fecha a formato (01-2023) - (01-11-2023)
def date_fix(value, separator='-'):
    """
    Esta función toma un valor de fecha en formato 'YYYYMM' o 'YYYYMMDD' y un separador opcional,
    y devuelve la fecha en el formato 'DD-MM-YYYY' o 'MM-YYYY' respectivamente.

    Args:
    value (str): El valor de fecha en formato 'YYYYMM' o 'YYYYMMDD'.
    separator (str, opcional): El separador a utilizar en el resultado. Por defecto es '-'.

    Returns:
    str: La fecha formateada en el formato especificado, si no es posible convertir retorna el valor de entrada.
    """
    try:
        if len(value) == 6:
            fecha = datetime.strptime(value, "%Y%m").strftime("%m" + separator + "%Y")
        else:
            fecha = datetime.strptime(value, "%Y%m%d").strftime("%d" + separator + "%m" + separator + "%Y")
    except:
        fecha = value
    return fecha



####################### Funciones PE #######################


def get_value(objeto, lista=False, func=None):
    """
    Función que procesa un objeto (diccionario o lista) de acuerdo a los parámetros proporcionados.

    Parámetros:
    objeto (dict o list): El objeto a procesar.
    lista (bool, opcional): Indica si se debe tratar el objeto como una lista. Por defecto es False.
    func (función, opcional): Función a aplicar al objeto procesado. Por defecto es None.

    Retorna:
    dict, list u objeto original: Dependiendo de las operaciones realizadas en función de los parámetros.

    Ejemplos de uso:
    - get_value(objeto=nodo,lista='Avalado',func=avalados) 
    """
    check = isinstance(objeto,dict) or isinstance(objeto,list)
    if check:
        if lista: #convierte trama capturada en lista a un []
            target = objeto.get(lista)
            if isinstance(target,list):
                return get_value(target,False,func)
            elif isinstance(target,dict):
                return get_value([target],False,func) 
            else:
                return objeto
        elif not lista: #consume func retorna resultado
            if isinstance(objeto,list):
                return func(objeto) 
            elif isinstance(objeto,dict):
                if lista:
                    return func([objeto])
                else:
                    return func(objeto)
            else:
                return objeto
    else:
        return objeto
        
#Reemplaza por null los tag xsi
def xsi_to_null(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict) and "xsi:nil" in value and value["xsi:nil"] == True and "xmlns:xsi" in value and value["xmlns:xsi"] == "http://www.w3.org/2001/XMLSchema-instance":
                data[key] = None
            else:
                xsi_to_null(value)
    elif isinstance(data, list):
        for item in data:
            xsi_to_null(item)

