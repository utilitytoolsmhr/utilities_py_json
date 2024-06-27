# ==================================
# Modulo: REGISTRO CREDITICIO CONSOLIDADO
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

    # Código modulo -> Persona Natural o Persona Jurídica
    codigo_modulo = 446 if tipoPersona == 2 else 447

    try:
        # Captura respuesta API-DSS
        payload = primaryConsumer.get('equifax-pe-middleware')

        # Reemplaza por null tag[xsi] presentes en payload
        xsi_to_null(payload)

        # Seleccionamos el modulo target
        nombre = 'REGISTRO CREDITICIO CONSOLIDADO'
        target = 'RegistroCrediticioConsolidado'
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

    def detalle_entidades(nodo):
        return {
            'Entidad': [
                {
                    'Codigo': text_fix(entidad.get('Codigo')),
                    'Nombre': text_fix(entidad.get('Nombre')),
                    'Calificacion': text_fix(entidad.get('Calificacion')),
                    'CreditosVigentes': float_fix(entidad.get('CreditosVigentes')),
                    'CreditosRefinanciados': float_fix(entidad.get('CreditosRefinanciados')),
                    'CreditosVencidos': float_fix(entidad.get('CreditosVencidos')),
                    'CreditosJudicial': float_fix(entidad.get('CreditosJudicial'))
                }
                for entidad in nodo.get('Entidad', [])
            ],
            'periodo': text_fix(nodo.get('periodo'))
        }

    def periodos_data(nodo):
        return {
            'Periodo': [
                {
                    'valor': text_fix(periodo.get('valor')),
                    'flag': periodo.get('flag') == "true",
                    'NroEntidades': text_fix(periodo.get('NroEntidades')),
                    'Calificaciones': {
                        'NOR': text_fix(periodo.get('Calificaciones').get('NOR')),
                        'CPP': text_fix(periodo.get('Calificaciones').get('CPP')),
                        'DEF': text_fix(periodo.get('Calificaciones').get('DEF')),
                        'DUD': text_fix(periodo.get('Calificaciones').get('DUD')),
                        'PER': text_fix(periodo.get('Calificaciones').get('PER'))
                    },
                    'Deudas': {
                        'Deuda': [
                            {
                                'CodigoCuenta': text_fix(deuda.get('CodigoCuenta')),
                                'NombreCuenta': text_fix(deuda.get('NombreCuenta')),
                                'DescripcionCuenta': text_fix(deuda.get('DescripcionCuenta')),
                                'CodigoEntidad': text_fix(deuda.get('CodigoEntidad')),
                                'NombreEntidad': text_fix(deuda.get('NombreEntidad')),
                                'Calificacion': text_fix(deuda.get('Calificacion')),
                                'Monto': float_fix(deuda.get('Monto'))
                            }
                            for deuda in periodo.get('Deudas', {}).get('Deuda', [])
                        ]
                    }
                }
                for periodo in nodo.get('Periodo', [])
            ]
        }

    def avalistas_data(nodo):
        return {
            'Aval': [
                {
                    'TipoDocumento': text_fix(aval.get('TipoDocumento')),
                    'NumeroDocumento': text_fix(aval.get('NumeroDocumento')),
                    'NombreAval': text_fix(aval.get('NombreAval')),
                    'Entidades': {
                        'Entidad': [
                            {
                                'Descripcion': text_fix(entidad.get('Descripcion')),
                                'Periodos': {
                                    'Periodo': [
                                        {
                                            'periodo': text_fix(periodo.get('periodo')),
                                            'Calificacion': text_fix(periodo.get('Calificacion')),
                                            'Saldo': float_fix(periodo.get('Saldo'))
                                        }
                                        for periodo in entidad.get('Periodos', {}).get('Periodo', [])
                                    ]
                                }
                            }
                            for entidad in aval.get('Entidades', {}).get('Entidad', [])
                        ]
                    }
                }
                for aval in nodo.get('Aval', [])
            ]
        }

    def microfinanzas_data(nodo):
        return {
            'CalificacionEntidad': {
                'Entidades': [
                    {
                        'periodo': text_fix(entidad.get('periodo')),
                        'flag': entidad.get('flag') == "true",
                        'Entidad': [
                            {
                                'Codigo': text_fix(ent.get('Codigo')),
                                'Nombre': text_fix(ent.get('Nombre')),
                                'Clasificacion': text_fix(ent.get('Clasificacion'))
                            }
                            for ent in entidad.get('Entidad', [])
                        ]
                    }
                    for entidad in nodo.get('CalificacionEntidad', {}).get('Entidades', [])
                ]
            },
            'Periodos': {
                'Periodo': [
                    {
                        'valor': text_fix(periodo.get('valor')),
                        'flag': periodo.get('flag') == "true",
                        'NroEntidades': text_fix(periodo.get('NroEntidades')),
                        'Calificaciones': {
                            'NOR': text_fix(periodo.get('Calificaciones').get('NOR')),
                            'CPP': text_fix(periodo.get('Calificaciones').get('CPP')),
                            'DEF': text_fix(periodo.get('Calificaciones').get('DEF')),
                            'DUD': text_fix(periodo.get('Calificaciones').get('DUD')),
                            'PER': text_fix(periodo.get('Calificaciones').get('PER'))
                        },
                        'Deudas': {
                            'Deuda': [
                                {
                                    'Cuenta': text_fix(deuda.get('Cuenta')),
                                    'CodigoCuenta': text_fix(deuda.get('CodigoCuenta')),
                                    'NombreCuenta': text_fix(deuda.get('NombreCuenta')),
                                    'CodigoEntidad': text_fix(deuda.get('CodigoEntidad')),
                                    'NombreEntidad': text_fix(deuda.get('NombreEntidad')),
                                    'Monto': float_fix(deuda.get('Monto'))
                                }
                                for deuda in periodo.get('Deudas', {}).get('Deuda', [])
                            ]
                        }
                    }
                    for periodo in nodo.get('Periodos', {}).get('Periodo', [])
                ]
            }
        }

    def rectificaciones_data(nodo):
        return {
            'Rectificacion': [
                {
                    'periodo': text_fix(rectificacion.get('periodo')),
                    'Entidades': {
                        'Entidad': [
                            {
                                'Codigo': text_fix(entidad.get('Codigo')),
                                'Nombre': text_fix(entidad.get('Nombre')),
                                'Detalles': {
                                    'Detalle': [
                                        {
                                            'Concepto': text_fix(detalle.get('Concepto')),
                                            'Dice': text_fix(detalle.get('Dice')),
                                            'Debedecir': text_fix(detalle.get('Debedecir'))
                                        }
                                        for detalle in entidad.get('Detalles', {}).get('Detalle', [])
                                    ]
                                }
                            }
                            for entidad in rectificacion.get('Entidades', {}).get('Entidad', [])
                        ]
                    }
                }
                for rectificacion in nodo.get('Rectificacion', [])
            ]
        }

    def registro_crediticio_consolidado(nodo):
        return {
            'RCC': {
                'DetalleEntidades': detalle_entidades(nodo.get('RCC', {}).get('DetalleEntidades', {})),
                'Periodos': periodos_data(nodo.get('RCC', {}).get('Periodos', {}))
            },
            'Avalistas': avalistas_data(nodo.get('Avalistas', {})),
            'Microfinanzas': microfinanzas_data(nodo.get('Microfinanzas', {})),
            'Rectificaciones': rectificaciones_data(nodo.get('Rectificaciones', {}))
        }

    data_output = registro_crediticio_consolidado(nodo)

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
                    "RegistroCrediticioConsolidado": data_output
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
                    "RegistroCrediticioConsolidado": {}
                }
            }
    else:
        try:
            final_out = {
                "RegistroCrediticioConsolidado": {
                    "Codigo": modulo[0].get('Codigo'),
                    "Nombre": modulo[0].get('Nombre'),
                    "Data": {
                        "flag": modulo[0].get('Data').get('flag'),
                        "RegistroCrediticioConsolidado": data_output
                    }
                }
            }
        except Exception as e:
            print(f"Error generando la salida final (formato_salida=True): {e}")
            traceback.print_exc()
            final_out = {
                "RegistroCrediticioConsolidado": {
                    "Codigo": codigo,
                    "Nombre": nombre,
                    "Data": {
                        "flag": False,
                        "RegistroCrediticioConsolidado": {}
                    }
                }
            }
    return final_out
