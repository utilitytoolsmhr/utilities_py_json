
import os
import sys
import traceback
from pe_utils import int_fix, float_fix, text_fix, get_value, xsi_to_null

def main(payload):

    #################################################
    ################## Data IN ######################
    #################################################

    try:
        primaryConsumer = payload.get('applicants')[0]
    except:
        primaryConsumer = payload.get('applicants').get('primaryConsumer')

    # Captura variables entrada
    tipoPersona = int(primaryConsumer.get('personalInformation').get('tipoPersona'))
    formato_salida = primaryConsumer.get('personalInformation').get('formatoSalida')

    # Código modulo -> Persona Natural = 1 / Persona Jurídica = 2
    codigo_modulo = 222 if tipoPersona == 1 else 333

    try:
        # Captura respuesta API-DSS
        payload = primaryConsumer.get('equifax-pe-middleware')

        # Reemplaza por null tag[xsi] presentes en payload
        xsi_to_null(payload)

        # Seleccionamos el modulo target
        nombre = 'OTRAS DEUDAS IMPAGAS'
        target = 'OtrasDeudasImpagas'
        codigo = codigo_modulo
        modulos = payload.get('dataSourceResponse').get('GetReporteOnlineResponse').get('ReporteCrediticio').get('Modulos').get('Modulo')
        modulo = [modulo for modulo in modulos if modulo.get('Data') is not None and nombre in modulo.get('Nombre')]

        # Filtra por target si existen múltiples módulos con el mismo nombre
        if len(modulo) > 1:
            modulo_filtrado = [modulo_filtrado for modulo_filtrado in modulo if modulo_filtrado.get('Data').get(target)]
            modulo = modulo_filtrado if len(modulo_filtrado) == 1 else modulo

        # Data del modulo
        nodo = modulo[0].get('Data').get(target)
    except Exception as e:
        print(f"Error procesando los datos de entrada: {e}")
        traceback.print_exc()

    #################################################
    ################### Variables ###################
    #################################################

    def deudas_impagas_protestadas(nodo):
        return {
            'MontoEnSoles': float_fix(nodo.get('MontoEnSoles')),
            'MontoEnDolares': float_fix(nodo.get('MontoEnDolares'))
        }

    def deudas_impagas_infocorp(nodo):
        return {
            'MontoEnSoles': float_fix(nodo.get('MontoEnSoles')),
            'MontoEnDolares': float_fix(nodo.get('MontoEnDolares'))
        }

    def deudas_impagas_sunat(nodo):
        return {
            'MontoEnSoles': float_fix(nodo.get('MontoEnSoles')),
            'MontoEnDolares': float_fix(nodo.get('MontoEnDolares'))
        }

    def deudas_impagas_previsional(nodo):
        return {
            'MontoEnSoles': float_fix(nodo.get('MontoEnSoles')),
            'MontoEnDolares': float_fix(nodo.get('MontoEnDolares'))
        }

    def odi_detalle(nodo):
        return {
            'Periodo': text_fix(nodo.get('Periodo')),
            'Riesgo': text_fix(nodo.get('Riesgo')),
            'DeudasImpagasProtestadas': deudas_impagas_protestadas(nodo.get('DeudasImpagasProtestadas', {})),
            'DeudasImpagasInfocorp': deudas_impagas_infocorp(nodo.get('DeudasImpagasInfocorp', {})),
            'DeudasImpagasSunat': deudas_impagas_sunat(nodo.get('DeudasImpagasSunat', {})),
            'DeudasImpagasPrevisional': deudas_impagas_previsional(nodo.get('DeudasImpagasPrevisional', {}))
        }

    def otras_deudas_impagas(nodo):
        return {
            'ODIDetalle': [odi_detalle(item) for item in nodo.get('ODIDetalle', [])]
        }

    data_output = otras_deudas_impagas(nodo)

    # Limpiar objetos vacíos
    def clean_data(data):
        if isinstance(data, dict):
            return {k: clean_data(v) for k, v in data.items() if v not in [None, "xsi:nil", "xmlns:xsi"]}
        elif isinstance(data, list):
            return [clean_data(v) for v in data if v not in [None, "xsi:nil", "xmlns:xsi"]]
        else:
            return data

    data_output = clean_data(data_output)

    #################################################
    ################## Set Output ###################
    #################################################

    if not formato_salida:
        try:
            final_out = {
                "Codigo": modulo[0].get('Codigo'),
                "Nombre": modulo[0].get('Nombre'),
                "Data": {
                    "flag": modulo[0].get('Data').get('flag'),
                    "OtrasDeudasImpagas": data_output
                }
            }
        except Exception as e:
            print(f"Error generando la salida final (formato_salida=False): {e}")
            traceback.print_exc()
            final_out = {
                "Codigo": codigo,
                "Nombre": nombre,
                "Data": {
                    "flag": False,
                    "OtrasDeudasImpagas": {}
                }
            }
    else:
        try:
            final_out = {
                "OtrasDeudasImpagas": {
                    "Codigo": modulo[0].get('Codigo'),
                    "Nombre": modulo[0].get('Nombre'),
                    "Data": {
                        "flag": modulo[0].get('Data').get('flag'),
                        "OtrasDeudasImpagas": data_output
                    }
                }
            }
        except Exception as e:
            print(f"Error generando la salida final (formato_salida=True): {e}")
            traceback.print_exc()
            final_out = {
                "OtrasDeudasImpagas": {
                    "Codigo": codigo,
                    "Nombre": nombre,
                    "Data": {
                        "flag": False,
                        "OtrasDeudasImpagas": {}
                    }
                }
            }
    return final_out
