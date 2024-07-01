# ==================================
# Modulo: RESUMEN FLAGS
# Autor: José Reyes         
# Correo: jose.reyes3@equifax.com
# Fecha: 27-06-2024
# ==================================

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
        nombre = 'RESUMEN FLAGS'
        target = 'ResumenFlags'
        codigo = codigo_modulo
        modulos = payload.get('dataSourceResponse').get('GetReporteOnlineResponse').get('ReporteCrediticio').get('Modulos').get('Modulo')
        modulo = [modulo for modulo in modulos if modulo.get('Data') is not None and nombre in modulo.get('Nombre')]

        # Filtra por target si existen múltiples módulos con el mismo nombre
        if len(modulo) > 1:
            modulo_filtrado = [modulo_filtrado for modulo_filtrado in modulo if modulo_filtrado.get('Data').get(target)]
            modulo = modulo_filtrado if len(modulo_filtrado) == 1 else modulo

        # Verificar si hay datos disponibles en el módulo
        if not modulo:
            raise ValueError("No hay datos disponibles en el módulo")

        # Data del modulo
        nodo = modulo[0].get('Data').get(target)
    except Exception as e:
        print(f"Error procesando los datos de entrada: {e}")
        traceback.print_exc()

    #################################################
    ################### Variables ###################
    #################################################

    def resumen_deuda(nodo):
        return {
            'Periodo': text_fix(nodo.get('Periodo')),
            'DeudaTotal': float_fix(nodo.get('DeudaTotal')),
            'DeudaDirecta': float_fix(nodo.get('DeudaDirecta')),
            'DeudaIndirecta': float_fix(nodo.get('DeudaIndirecta')),
            'PorcentajeDeudaNormal': float_fix(nodo.get('PorcentajeDeudaNormal')),
            'PorcentajeDeudaPotencial': float_fix(nodo.get('PorcentajeDeudaPotencial')),
            'PorcentajeDeudaDeficiente': float_fix(nodo.get('PorcentajeDeudaDeficiente')),
            'PorcentajeDeudaEnRiesgo': float_fix(nodo.get('PorcentajeDeudaEnRiesgo')),
            'PorcentajeDeudaPerdida': float_fix(nodo.get('PorcentajeDeudaPerdida')),
            'Variacion': float_fix(nodo.get('Variacion'))
        }

    def resumen_score_historico(nodo):
        return {
            'ScoreActual': {
                'Periodo': text_fix(nodo.get('ScoreActual', {}).get('Periodo')),
                'Riesgo': text_fix(nodo.get('ScoreActual', {}).get('Riesgo')),
                'MotivoSinScore': text_fix(nodo.get('ScoreActual', {}).get('MotivoSinScore'))
            },
            'ScoreAnterior': {
                'Periodo': text_fix(nodo.get('ScoreAnterior', {}).get('Periodo')),
                'Riesgo': text_fix(nodo.get('ScoreAnterior', {}).get('Riesgo')),
                'MotivoSinScore': text_fix(nodo.get('ScoreAnterior', {}).get('MotivoSinScore'))
            },
            'ScoreHace12Meses': {
                'Periodo': text_fix(nodo.get('ScoreHace12Meses', {}).get('Periodo')),
                'Riesgo': text_fix(nodo.get('ScoreHace12Meses', {}).get('Riesgo')),
                'MotivoSinScore': text_fix(nodo.get('ScoreHace12Meses', {}).get('MotivoSinScore'))
            }
        }

    def resumen_bloque_flags(nodo):
        return {
            'TarjetaCredito': text_fix(nodo.get('TarjetaCredito')),
            'LineaDeCredito': text_fix(nodo.get('LineaDeCredito')),
            'CreditoHipotecario': text_fix(nodo.get('CreditoHipotecario')),
            'BuenPagadorDeServicios': text_fix(nodo.get('BuenPagadorDeServicios')),
            'EstaEnInfocorp': text_fix(nodo.get('EstaEnInfocorp')),
            'AvalAvalado': text_fix(nodo.get('AvalAvalado')),
            'RepresentanteLegal': text_fix(nodo.get('RepresentanteLegal')),
            'GastoMensualEstimado': float_fix(nodo.get('GastoMensualEstimado')),
            'PosibleRestringido': text_fix(nodo.get('PosibleRestringido')),
            'TieneAuto': text_fix(nodo.get('TieneAuto')),
            'EntidadesQueConsultaron': int_fix(nodo.get('EntidadesQueConsultaron')),
            'Homonimos': text_fix(nodo.get('Homonimos')),
            'ComercioExterior': text_fix(nodo.get('ComercioExterior')),
            'DeudaPrevisional': text_fix(nodo.get('DeudaPrevisional')),
            'AlertaPep': text_fix(nodo.get('AlertaPep')),
            'AlertaRedam': text_fix(nodo.get('AlertaRedam')),
            'ReactivaPeru': text_fix(nodo.get('ReactivaPeru')),
            'ReactivaPeruInfo': {
                'Fecha': text_fix(nodo.get('ReactivaPeruInfo', {}).get('Fecha')),
                'Monto': text_fix(nodo.get('ReactivaPeruInfo', {}).get('Monto'))
            }
        }

    def resumen_flags(nodo):
        return {
            'ResumenFlags': {
                'ResumenComportamiento': {
                    'TipoDocumento': text_fix(nodo.get('ResumenComportamiento', {}).get('TipoDocumento')),
                    'NumeroDocumento': text_fix(nodo.get('ResumenComportamiento', {}).get('NumeroDocumento')),
                    'ResumenDeuda': resumen_deuda(nodo.get('ResumenComportamiento', {}).get('ResumenDeuda', {})),
                    'ResumenScoreHistorico': resumen_score_historico(nodo.get('ResumenComportamiento', {}).get('ResumenScoreHistorico', {}))
                },
                'ResumenBloqueFlags': resumen_bloque_flags(nodo.get('ResumenBloqueFlags', {}))
            }
        }

    data_output = resumen_flags(nodo)

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
                        "ResumenFlags": data_output
                    }
                }
            else:
                final_out = {
                    "Codigo": codigo,
                    "Nombre": nombre,
                    "Data": {
                        "flag": False,
                        "ResumenFlags": {}
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
                    "ResumenFlags": {}
                }
            }
    else:
        try:
            if nodo:
                final_out = {
                    "ResumenFlags": {
                        "Codigo": modulo[0].get('Codigo'),
                        "Nombre": modulo[0].get('Nombre'),
                        "Data": {
                            "flag": True,
                            "ResumenFlags": data_output
                        }
                    }
                }
            else:
                final_out = {
                    "ResumenFlags": {
                        "Codigo": codigo,
                        "Nombre": nombre,
                        "Data": {
                            "flag": False,
                            "ResumenFlags": {}
                        }
                    }
                }
        except Exception as e:
            print(f"Error generando la salida final (formato_salida=True): {e}")
            traceback.print_exc()
            final_out = {
                "ResumenFlags": {
                    "Codigo": codigo,
                    "Nombre": nombre,
                    "Data": {
                        "flag": False,
                        "ResumenFlags": {}
                    }
                }
            }
    return final_out
