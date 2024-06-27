
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
        nombre = 'SISTEMA FINANCIERO'
        target = 'SistemaFinanciero'
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

    def semaforo(nodo):
        return {
            'periodo': text_fix(nodo.get('periodo')),
            'NoTieneImpagos': bool(nodo.get('NoTieneImpagos')),
            'TieneDeudasAtrasadas': bool(nodo.get('TieneDeudasAtrasadas')),
            'TieneDeudasImpagasInfocorp': bool(nodo.get('TieneDeudasImpagasInfocorp')),
            'InformacionNoDisponible': bool(nodo.get('InformacionNoDisponible')),
            'DiasAtraso': int_fix(nodo.get('DiasAtraso'))
        }

    def resumen_comportamiento_pago(nodo):
        return {
            'Semaforo': [semaforo(item) for item in nodo.get('Semaforo', [])]
        }

    def deuda_historica(nodo):
        return {
            'periodo': text_fix(nodo.get('periodo')),
            'Calificacion': text_fix(nodo.get('Calificacion')),
            'Porcentaje': text_fix(nodo.get('Porcentaje')),
            'NroEntidades': int_fix(nodo.get('NroEntidades')),
            'DeudaVigente': float_fix(nodo.get('DeudaVigente')),
            'DeudaAtrasada': float_fix(nodo.get('DeudaAtrasada')),
            'DeudaVencida': float_fix(nodo.get('DeudaVencida')),
            'DeudaRefinanciada': float_fix(nodo.get('DeudaRefinanciada')),
            'DeudaReestructurada': float_fix(nodo.get('DeudaReestructurada')),
            'DeudaJudicial': float_fix(nodo.get('DeudaJudicial')),
            'DeudaCastigada': float_fix(nodo.get('DeudaCastigada')),
            'DeudaTotal': float_fix(nodo.get('DeudaTotal')),
            'DiasAtraso': int_fix(nodo.get('DiasAtraso'))
        }

    def deudas_historicas(nodo):
        return {
            'Deuda': [deuda_historica(item) for item in nodo.get('Deuda', [])]
        }

    def producto_deuda(nodo):
        return {
            'Tipo': text_fix(nodo.get('Tipo')),
            'Descripcion': text_fix(nodo.get('Descripcion')),
            'Monto': float_fix(nodo.get('Monto')),
            'DiasAtraso': int_fix(nodo.get('DiasAtraso'))
        }

    def deuda_ultimo_periodo(nodo):
        return {
            'Entidad': text_fix(nodo.get('Entidad')),
            'SistemaFinanciero': text_fix(nodo.get('SistemaFinanciero')),
            'Calificacion': text_fix(nodo.get('Calificacion')),
            'MontoTotal': float_fix(nodo.get('MontoTotal')),
            'Productos': {
                'Producto': [producto_deuda(item) for item in nodo.get('Productos', {}).get('Producto', [])]
            }
        }

    def deudas_ultimo_periodo(nodo):
        return {
            'periodo': text_fix(nodo.get('periodo')),
            'Deuda': [deuda_ultimo_periodo(item) for item in nodo.get('Deuda', [])]
        }

    def entidad(nodo):
        return {
            'Codigo': text_fix(nodo.get('Codigo')),
            'Nombre': text_fix(nodo.get('Nombre')),
            'Calificacion': text_fix(nodo.get('Calificacion')),
            'CreditosVigentes': float_fix(nodo.get('CreditosVigentes')),
            'CreditosRefinanciados': float_fix(nodo.get('CreditosRefinanciados')),
            'CreditosVencidos': float_fix(nodo.get('CreditosVencidos')),
            'CreditosJudicial': float_fix(nodo.get('CreditosJudicial'))
        }

    def detalle_entidades(nodo):
        return {
            'periodo': text_fix(nodo.get('periodo')),
            'Entidad': [entidad(item) for item in nodo.get('Entidad', [])]
        }

    def calificaciones(nodo):
        return {
            'NOR': float_fix(nodo.get('NOR')),
            'CPP': float_fix(nodo.get('CPP')),
            'DEF': float_fix(nodo.get('DEF')),
            'DUD': float_fix(nodo.get('DUD')),
            'PER': float_fix(nodo.get('PER'))
        }

    def deuda(nodo):
        return {
            'CodigoCuenta': text_fix(nodo.get('CodigoCuenta')),
            'NombreCuenta': text_fix(nodo.get('NombreCuenta')),
            'DescripcionCuenta': text_fix(nodo.get('DescripcionCuenta')),
            'CodigoEntidad': text_fix(nodo.get('CodigoEntidad')),
            'NombreEntidad': text_fix(nodo.get('NombreEntidad')),
            'Calificacion': float_fix(nodo.get('Calificacion')),
            'Monto': float_fix(nodo.get('Monto'))
        }

    def periodo(nodo):
        return {
            'valor': text_fix(nodo.get('valor')),
            'flag': bool(nodo.get('flag')),
            'NroEntidades': int_fix(nodo.get('NroEntidades')),
            'Calificaciones': calificaciones(nodo.get('Calificaciones', {})),
            'Deudas': {
                'Deuda': [deuda(item) for item in nodo.get('Deudas', {}).get('Deuda', [])]
            }
        }

    def rcc(nodo):
        return {
            'DetalleEntidades': detalle_entidades(nodo.get('DetalleEntidades', {})),
            'Periodos': {
                'Periodo': [periodo(item) for item in nodo.get('Periodos', {}).get('Periodo', [])]
            }
        }

    def sistema_financiero(nodo):
        return {
            'ResumenComportamientoPago': resumen_comportamiento_pago(nodo.get('ResumenComportamientoPago', {})),
            'DeudasHistoricas': deudas_historicas(nodo.get('DeudasHistoricas', {})),
            'DeudasUltimoPeriodo': deudas_ultimo_periodo(nodo.get('DeudasUltimoPeriodo', {})),
            'RCC': rcc(nodo.get('RCC', {})),
            'Rectificaciones': nodo.get('Rectificaciones', {}),
            'Avalistas': nodo.get('Avalistas', {}),
            'Microfinanzas': nodo.get('Microfinanzas', {})
        }

    data_output = sistema_financiero(nodo)

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
                    "SistemaFinanciero": data_output
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
                    "SistemaFinanciero": {}
                }
            }
    else:
        try:
            final_out = {
                "SistemaFinanciero": {
                    "Codigo": modulo[0].get('Codigo'),
                    "Nombre": modulo[0].get('Nombre'),
                    "Data": {
                        "flag": modulo[0].get('Data').get('flag'),
                        "SistemaFinanciero": data_output
                    }
                }
            }
        except Exception as e:
            print(f"Error generando la salida final (formato_salida=True): {e}")
            traceback.print_exc()
            final_out = {
                "SistemaFinanciero": {
                    "Codigo": codigo,
                    "Nombre": nombre,
                    "Data": {
                        "flag": False,
                        "SistemaFinanciero": {}
                    }
                }
            }
    return final_out
