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

    # Código modulo -> Persona Jurídica = 1
    codigo_modulo = 445 if tipoPersona == 2 else None

    try:
        # Captura respuesta API-DSS
        payload = primaryConsumer.get('equifax-pe-middleware')

        # Reemplaza por null tag[xsi] presentes en payload
        xsi_to_null(payload)

        # Seleccionamos el modulo target
        nombre = 'PROTESTOS GIRADOR'
        target = 'CarteraMorosa'
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

    def periodo_data(nodo):
        return [
            {
                'valor': text_fix(periodo.get('valor')),
                'CantidadSolesAclarados': int_fix(periodo.get('CantidadSolesAclarados')),
                'MontoSolesAclarados': float_fix(periodo.get('MontoSolesAclarados')),
                'CantidadDolaresAclarados': int_fix(periodo.get('CantidadDolaresAclarados')),
                'MontoDolaresAclarados': float_fix(periodo.get('MontoDolaresAclarados')),
                'CantidadOmAclarados': int_fix(periodo.get('CantidadOmAclarados')),
                'CantidadSolesNoAclarados': int_fix(periodo.get('CantidadSolesNoAclarados')),
                'MontoSolesNoAclarados': float_fix(periodo.get('MontoSolesNoAclarados')),
                'CantidadDolaresNoAclarados': int_fix(periodo.get('CantidadDolaresNoAclarados')),
                'MontoDolaresNoAclarados': float_fix(periodo.get('MontoDolaresNoAclarados')),
                'CantidadOmNoAclarados': int_fix(periodo.get('CantidadOmNoAclarados'))
            }
            for periodo in nodo.get('Periodo', [])
        ]

    def detalle_protestos(nodo):
        return [
            {
                'CorrelativoBNP': text_fix(protesto.get('CorrelativoBNP')),
                'NumeroBoletin': text_fix(protesto.get('NumeroBoletin')),
                'TipoDocumento': text_fix(protesto.get('TipoDocumento')),
                'Moneda': text_fix(protesto.get('Moneda')),
                'Monto': float_fix(protesto.get('Monto')),
                'Emisor': text_fix(protesto.get('Emisor')),
                'FechaVencimiento': text_fix(protesto.get('FechaVencimiento')),
                'FechaAclaracion': text_fix(protesto.get('FechaAclaracion')),
                'Notaria': text_fix(protesto.get('Notaria'))
            }
            for protesto in nodo.get('Protesto', [])
        ]

    def cartera_morosa(nodo):
        return {
            'ResumenProtestos': {
                'Periodo': periodo_data(nodo.get('ResumenProtestos', {}))
            },
            'DetalleProtestos': {
                'Protesto': detalle_protestos(nodo.get('DetalleProtestos', {}))
            }
        }

    data_output = cartera_morosa(nodo)

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
                    "CarteraMorosa": data_output
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
                    "CarteraMorosa": {}
                }
            }
    else:
        try:
            final_out = {
                "CarteraMorosa": {
                    "Codigo": modulo[0].get('Codigo'),
                    "Nombre": modulo[0].get('Nombre'),
                    "Data": {
                        "flag": modulo[0].get('Data').get('flag'),
                        "CarteraMorosa": data_output
                    }
                }
            }
        except Exception as e:
            print(f"Error generando la salida final (formato_salida=True): {e}")
            traceback.print_exc()
            final_out = {
                "CarteraMorosa": {
                    "Codigo": codigo,
                    "Nombre": nombre,
                    "Data": {
                        "flag": False,
                        "CarteraMorosa": {}
                    }
                }
            }
    return final_out
