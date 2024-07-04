import os
import sys
import traceback
from pe_utils import int_fix, float_fix, text_fix, get_value, xsi_to_null, obj_fix

def main(payload):

    #################################################
    ################## Data IN ######################
    #################################################

    try:
        if isinstance(payload.get('applicants'), list):
            primaryConsumer = payload.get('applicants')[0]
        else:
            primaryConsumer = payload.get('applicants', {}).get('primaryConsumer')

        if not primaryConsumer:
            raise ValueError("No se pudo obtener el primaryConsumer")
    except (IndexError, TypeError, ValueError) as e:
        print(f"No se pudo obtener el primaryConsumer: {e}")
        primaryConsumer = {}

    # Captura variables entrada
    try:
        tipoPersona = int(primaryConsumer.get('personalInformation', {}).get('tipoPersona', 0))
        formato_salida = primaryConsumer.get('personalInformation', {}).get('formatoSalida')
    except (ValueError, TypeError):
        tipoPersona = 0
        formato_salida = None

    # Código modulo -> Persona Natural o Persona Jurídica
    codigo_modulo = 450 if tipoPersona == 2 else 451

    try:
        # Captura respuesta API-DSS
        payload = primaryConsumer.get('equifax-pe-middleware', {})

        # Reemplaza por null tag[xsi] presentes en payload
        xsi_to_null(payload)

        # Seleccionamos el modulo target
        nombre = 'REPRESENTANTES LEGALES (CON SCORE)'
        target = 'RepresentantesLegales'
        codigo = codigo_modulo
        modulos = payload.get('dataSourceResponse', {}).get('GetReporteOnlineResponse', {}).get('ReporteCrediticio', {}).get('Modulos', {}).get('Modulo', [])
        modulo = [modulo for modulo in modulos if modulo.get('Data') is not None and nombre in modulo.get('Nombre', '')]

        # Filtra por target si existen múltiples módulos con el mismo nombre
        if len(modulo) > 1:
            modulo_filtrado = [modulo_filtrado for modulo_filtrado in modulo if modulo_filtrado.get('Data', {}).get(target)]
            modulo = modulo_filtrado if len(modulo_filtrado) == 1 else modulo

        # Verifica si el modulo tiene datos
        if not modulo:
            print("No hay datos disponibles en el módulo")
            nodo = {}
        else:
            # Data del modulo
            nodo = modulo[0].get('Data', {}).get(target, {})
            nodo = obj_fix(nodo)
    except Exception as e:
        print(f"Error procesando los datos de entrada: {e}")
        traceback.print_exc()
        nodo = {}

    #################################################
    ################### Variables ###################
    #################################################

    def representantes_data(nodo):
        if not isinstance(nodo, dict):
            return {}
        return {
            'TipoDocumento': text_fix(nodo.get('TipoDocumento')),
            'NumeroDocumento': text_fix(nodo.get('NumeroDocumento')),
            'Nombre': text_fix(nodo.get('Nombre')),
            'ScoreHistoricos': {
                'ScoreActual': {
                    'Periodo': text_fix(nodo.get('ScoreHistoricos', {}).get('ScoreActual', {}).get('Periodo')),
                    'Riesgo': text_fix(nodo.get('ScoreHistoricos', {}).get('ScoreActual', {}).get('Riesgo'))
                },
                'ScoreAnterior': {
                    'Periodo': text_fix(nodo.get('ScoreHistoricos', {}).get('ScoreAnterior', {}).get('Periodo')),
                    'Riesgo': text_fix(nodo.get('ScoreHistoricos', {}).get('ScoreAnterior', {}).get('Riesgo'))
                },
                'ScoreHace12Meses': {
                    'Periodo': text_fix(nodo.get('ScoreHistoricos', {}).get('ScoreHace12Meses', {}).get('Periodo')),
                    'Riesgo': text_fix(nodo.get('ScoreHistoricos', {}).get('ScoreHace12Meses', {}).get('Riesgo'))
                }
            },
            'FechaInicioCargo': text_fix(nodo.get('FechaInicioCargo')),
            'Cargo': text_fix(nodo.get('Cargo'))
        }

    def representantes_legales(nodo):
        if not isinstance(nodo, dict):
            return {}
        return {
            'RepresentadosPor': {
                'RepresentadoPor': representantes_data(nodo.get('RepresentadosPor', {}).get('RepresentadoPor', {}))
            },
            'RepresentantesDe': representantes_data(nodo.get('RepresentantesDe', {}))
        }

    data_output = representantes_legales(nodo)

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
            if nodo:
                final_out = {
                    "Codigo": modulo[0].get('Codigo'),
                    "Nombre": modulo[0].get('Nombre'),
                    "Data": {
                        "flag": True,
                        "RepresentantesLegales": data_output
                    }
                }
            else:
                final_out = {
                    "Codigo": codigo,
                    "Nombre": nombre,
                    "Data": {
                        "flag": False,
                        "RepresentantesLegales": {}
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
                    "RepresentantesLegales": {}
                }
            }
    else:
        try:
            if nodo:
                final_out = {
                    "RepresentantesLegales": {
                        "Codigo": modulo[0].get('Codigo'),
                        "Nombre": modulo[0].get('Nombre'),
                        "Data": {
                            "flag": True,
                            "RepresentantesLegales": data_output
                        }
                    }
                }
            else:
                final_out = {
                    "RepresentantesLegales": {
                        "Codigo": codigo,
                        "Nombre": nombre,
                        "Data": {
                            "flag": False,
                            "RepresentantesLegales": {}
                        }
                    }
                }
        except Exception as e:
            print(f"Error generando la salida final (formato_salida=True): {e}")
            traceback.print_exc()
            final_out = {
                "RepresentantesLegales": {
                    "Codigo": codigo,
                    "Nombre": nombre,
                    "Data": {
                        "flag": False,
                        "RepresentantesLegales": {}
                    }
                }
            }
    return final_out

if __name__ == '__main__':
    import json
    with open('response-dss1.json', 'r', encoding='UTF-8') as file:
        request = json.load(file)
        out = json.dumps(main(request), indent=4)
    with open('respond.json', 'w') as file:
        file.write(out)
