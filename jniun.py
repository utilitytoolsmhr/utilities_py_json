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

    # Código modulo -> Persona Natural o Persona Jurídica
    codigo_modulo = 448 if tipoPersona == 2 else 449

    try:
        # Captura respuesta API-DSS
        payload = primaryConsumer.get('equifax-pe-middleware')

        # Reemplaza por null tag[xsi] presentes en payload
        xsi_to_null(payload)

        # Seleccionamos el modulo target
        nombre = 'RESUMEN FINANCIERO: SISTEMA FINANCIERO (SBS) Y NO REGULADO (MICROFINANZAS)'
        target = 'ResumenFinanciero'
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

    def deudas_data(nodo):
        return {
            'Entidad': text_fix(nodo.get('Entidad')),
            'SistemaFinanciero': text_fix(nodo.get('SistemaFinanciero')),
            'CalificacionMesActual': text_fix(nodo.get('CalificacionMesActual')),
            'MontoSubTotalMesActual': float_fix(nodo.get('MontoSubTotalMesActual')),
            'CalificacionMesAnterior': text_fix(nodo.get('CalificacionMesAnterior')),
            'MontoSubTotalMesAnterior': float_fix(nodo.get('MontoSubTotalMesAnterior')),
            'CalificacionAnioAnterior': text_fix(nodo.get('CalificacionAnioAnterior')),
            'MontoSubTotalAnioAnterior': float_fix(nodo.get('MontoSubTotalAnioAnterior')),
            'Productos': {
                'Producto': [
                    {
                        'Tipo': text_fix(producto.get('Tipo')),
                        'Descripcion': text_fix(producto.get('Descripcion')),
                        'MontoMesActual': float_fix(producto.get('MontoMesActual')),
                        'MontoMesAnterior': float_fix(producto.get('MontoMesAnterior')),
                        'MontoAnioAnterior': float_fix(producto.get('MontoAnioAnterior')),
                        'DiasAtraso': text_fix(producto.get('DiasAtraso'))
                    }
                    for producto in nodo.get('Productos', {}).get('Producto', [])
                ]
            }
        }

    def resumen_financiero(nodo):
        return {
            'DeudasUltimoPeriodo': {
                'periodo': text_fix(nodo.get('DeudasUltimoPeriodo', {}).get('periodo')),
                'MesActual': text_fix(nodo.get('DeudasUltimoPeriodo', {}).get('MesActual')),
                'MesAnterior': text_fix(nodo.get('DeudasUltimoPeriodo', {}).get('MesAnterior')),
                'AnioAnterior': text_fix(nodo.get('DeudasUltimoPeriodo', {}).get('AnioAnterior')),
                'Deudas': {
                    'Deuda': [
                        deudas_data(deuda)
                        for deuda in nodo.get('DeudasUltimoPeriodo', {}).get('Deudas', {}).get('Deuda', [])
                    ]
                },
                'Totales': {
                    'MontoTotalMesActual': float_fix(nodo.get('DeudasUltimoPeriodo', {}).get('Totales', {}).get('MontoTotalMesActual')),
                    'MontoTotalMesAnterior': float_fix(nodo.get('DeudasUltimoPeriodo', {}).get('Totales', {}).get('MontoTotalMesAnterior')),
                    'MontoTotalAnioAnterior': float_fix(nodo.get('DeudasUltimoPeriodo', {}).get('Totales', {}).get('MontoTotalAnioAnterior'))
                }
            }
        }

    data_output = resumen_financiero(nodo)

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
                    "ResumenFinanciero": data_output
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
                    "ResumenFinanciero": {}
                }
            }
    else:
        try:
            final_out = {
                "ResumenFinanciero": {
                    "Codigo": modulo[0].get('Codigo'),
                    "Nombre": modulo[0].get('Nombre'),
                    "Data": {
                        "flag": modulo[0].get('Data').get('flag'),
                        "ResumenFinanciero": data_output
                    }
                }
            }
        except Exception as e:
            print(f"Error generando la salida final (formato_salida=True): {e}")
            traceback.print_exc()
            final_out = {
                "ResumenFinanciero": {
                    "Codigo": codigo,
                    "Nombre": nombre,
                    "Data": {
                        "flag": False,
                        "ResumenFinanciero": {}
                    }
                }
            }
    return final_out
