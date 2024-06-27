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

    def deuda_detalle(nodo):
        return {
            'FechaVencimiento': text_fix(nodo.get('FechaVencimiento')),
            'FechaReportada': text_fix(nodo.get('FechaReportada')),
            'Divisa': text_fix(nodo.get('Divisa')),
            'Monto': float_fix(nodo.get('Monto')),
            'Acreedor': text_fix(nodo.get('Acreedor')),
            'DocumentoBancario': text_fix(nodo.get('DocumentoBancario')),
            'CondicionDeuda': text_fix(nodo.get('CondicionDeuda')),
            'TipoDeudor': text_fix(nodo.get('TipoDeudor')),
            'GiroNegocio': text_fix(nodo.get('GiroNegocio'))
        }

    def sicom_detalle(nodo):
        return {
            'FechaVencimientoReciente': text_fix(nodo.get('FechaVencimientoReciente')),
            'CantidadSoles': int_fix(nodo.get('CantidadSoles')),
            'MontoSoles': float_fix(nodo.get('MontoSoles')),
            'CantidadDolares': int_fix(nodo.get('CantidadDolares')),
            'MontoDolares': float_fix(nodo.get('MontoDolares')),
            'Detalle': {
                'Deuda': [deuda_detalle(item) for item in nodo.get('Deuda', [])]
            }
        }

    def negativo_sunat_detalle(nodo):
        return {
            'FechaCobranzaReciente': text_fix(nodo.get('FechaCobranzaReciente')),
            'CantidadTotal': int_fix(nodo.get('CantidadTotal')),
            'MontoTotal': float_fix(nodo.get('MontoTotal')),
            'Detalle': {
                'Deuda': [
                    {
                        'Periodo': text_fix(nodo.get('Periodo')),
                        'Monto': float_fix(nodo.get('Monto')),
                        'Tipo': text_fix(nodo.get('Tipo')),
                        'Dependencia': text_fix(nodo.get('Dependencia')),
                        'FechaCobranza': text_fix(nodo.get('FechaCobranza')),
                        'FechaProceso': text_fix(nodo.get('FechaProceso'))
                    }
                ]
            }
        }

    def omision_detalle(nodo):
        return {
            'FechaOmision': text_fix(nodo.get('FechaOmision')),
            'Concepto': text_fix(nodo.get('Concepto')),
            'FechaProceso': text_fix(nodo.get('FechaProceso'))
        }

    def protestos_detalle(nodo):
        return {
            'CorrelativoBNP': text_fix(nodo.get('CorrelativoBNP')),
            'NumeroBoletin': text_fix(nodo.get('NumeroBoletin')),
            'TipoDocumento': text_fix(nodo.get('TipoDocumento')),
            'Divisa': text_fix(nodo.get('Divisa')),
            'Monto': float_fix(nodo.get('Monto')),
            'EmisorDocumento': text_fix(nodo.get('EmisorDocumento')),
            'AceptanteDocumento': text_fix(nodo.get('AceptanteDocumento')),
            'FechaVencimiento': text_fix(nodo.get('FechaVencimiento')),
            'FechaAclaracion': text_fix(nodo.get('FechaAclaracion')),
            'Notaria': text_fix(nodo.get('Notaria'))
        }

    def protestos_aclarados_detalle(nodo):
        return {
            'FechaVencimientoReciente': text_fix(nodo.get('FechaVencimientoReciente')),
            'CantidadSoles': int_fix(nodo.get('CantidadSoles')),
            'MontoSoles': float_fix(nodo.get('MontoSoles')),
            'CantidadDolares': int_fix(nodo.get('CantidadDolares')),
            'MontoDolares': float_fix(nodo.get('MontoDolares')),
            'Detalle': {
                'Deuda': [protestos_detalle(item) for item in nodo.get('Deuda', [])]
            }
        }

    def protestos_no_aclarados_detalle(nodo):
        return {
            'FechaVencimientoReciente': text_fix(nodo.get('FechaVencimientoReciente')),
            'CantidadSoles': int_fix(nodo.get('CantidadSoles')),
            'MontoSoles': float_fix(nodo.get('MontoSoles')),
            'CantidadDolares': int_fix(nodo.get('CantidadDolares')),
            'MontoDolares': float_fix(nodo.get('MontoDolares')),
            'Detalle': {
                'Deuda': [protestos_detalle(item) for item in nodo.get('Deuda', [])]
            }
        }

    def cuentas_cerradas_detalle(nodo):
        return {
            'FechaSancionReciente': text_fix(nodo.get('FechaSancionReciente')),
            'Detalle': {
                'InformacionNegativa': [
                    {
                        'FechaSancion': text_fix(nodo.get('FechaSancion')),
                        'FechaFinSancion': text_fix(nodo.get('FechaFinSancion')),
                        'FechaPublicacion': text_fix(nodo.get('FechaPublicacion')),
                        'NumeroPublicacion': text_fix(nodo.get('NumeroPublicacion')),
                        'Divisa': text_fix(nodo.get('Divisa')),
                        'TipoCuenta': text_fix(nodo.get('TipoCuenta')),
                        'Entidad': text_fix(nodo.get('Entidad'))
                    }
                ]
            }
        }

    def tarjetas_anuladas_detalle(nodo):
        return {
            'FechaSancionReciente': text_fix(nodo.get('FechaSancionReciente')),
            'Detalle': {
                'InformacionNegativa': [
                    {
                        'FechaSancion': text_fix(nodo.get('FechaSancion')),
                        'FechaFinSancion': text_fix(nodo.get('FechaFinSancion')),
                        'FechaPublicacion': text_fix(nodo.get('FechaPublicacion')),
                        'NumeroPublicacion': text_fix(nodo.get('NumeroPublicacion')),
                        'Divisa': text_fix(nodo.get('Divisa')),
                        'TipoCuenta': text_fix(nodo.get('TipoCuenta')),
                        'Entidad': text_fix(nodo.get('Entidad'))
                    }
                ]
            }
        }

    def redam_detalle(nodo):
        return {
            'FechaCreacionReciente': text_fix(nodo.get('FechaCreacionReciente')),
            'CantidadSoles': int_fix(nodo.get('CantidadSoles')),
            'MontoSoles': float_fix(nodo.get('MontoSoles')),
            'CantidadDolares': int_fix(nodo.get('CantidadDolares')),
            'MontoDolares': float_fix(nodo.get('MontoDolares')),
            'Detalle': nodo.get('Detalle', {})
        }

    def inquilinos_morosos_detalle(nodo):
        return {
            'Cabecera': nodo.get('Cabecera', {}),
            'Detalle': nodo.get('Detalle', {})
        }

    def otras_deudas_impagas(nodo):
        return {
            'Sicom': [sicom_detalle(item) for item in nodo.get('Sicom', [])],
            'NegativoSunat': negativo_sunat_detalle(nodo.get('NegativoSunat', {})),
            'Omisos': {
                'Cabecera': {
                    'Cantidad': int_fix(nodo.get('Cabecera', {}).get('Cantidad'))
                },
                'Detalle': {
                    'Omision': [omision_detalle(item) for item in nodo.get('Detalle', {}).get('Omision', [])]
                }
            },
            'Protestos': {
                'ProtestosAclarados': protestos_aclarados_detalle(nodo.get('ProtestosAclarados', {})),
                'ProtestosNoAclarados': protestos_no_aclarados_detalle(nodo.get('ProtestosNoAclarados', {}))
            },
            'CuentasCerradas': cuentas_cerradas_detalle(nodo.get('CuentasCerradas', {})),
            'TarjetasAnuladas': tarjetas_anuladas_detalle(nodo.get('TarjetasAnuladas', {})),
            'Redam': redam_detalle(nodo.get('Redam', {})),
            'InquilinosMorosos': inquilinos_morosos_detalle(nodo.get('InquilinosMorosos', {}))
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
