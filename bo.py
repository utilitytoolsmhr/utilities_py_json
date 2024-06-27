import os
import sys
import traceback
from pe_utils import int_fix, float_fix, text_fix, get_value, xsi_to_null

def main(payload):
    try:
        primaryConsumer = payload.get('applicants')[0]
    except:
        primaryConsumer = payload.get('applicants').get('primaryConsumer')

    tipoPersona = int(primaryConsumer.get('personalInformation').get('tipoPersona'))
    formato_salida = primaryConsumer.get('personalInformation').get('formatoSalida')

    codigo_modulo = 222 if tipoPersona == 1 else 333

    try:
        payload = primaryConsumer.get('equifax-pe-middleware')
        xsi_to_null(payload)

        nombre = 'BOLETÍN OFICIAL'
        target = 'BoletinOficial'
        codigo = codigo_modulo
        modulos = payload.get('dataSourceResponse').get('GetReporteOnlineResponse').get('ReporteCrediticio').get('Modulos').get('Modulo')
        modulo = [modulo for modulo in modulos if modulo.get('Data') is not None and nombre in modulo.get('Nombre')]

        if len(modulo) > 1:
            modulo_filtrado = [modulo_filtrado for modulo_filtrado in modulo if modulo_filtrado.get('Data').get(target)]
            modulo = modulo_filtrado if len(modulo_filtrado) == 1 else modulo

        nodo = modulo[0].get('Data').get(target)
    except Exception as e:
        print(f"Error procesando los datos de entrada: {e}")
        traceback.print_exc()

    #################################################
    ################### Variables ###################
    #################################################
    data_output = boletinoficial(nodo)

    def clean_data(data):
        if isinstance(data, dict):
            return {k: clean_data(v) for k, v in data.items() if v not in [None, "xsi:nil", "xmlns:xsi"]}
        elif isinstance(data, list):
            return [clean_data(v) for v in data if v not in [None, "xsi:nil", "xmlns:xsi"]]
        else:
            return data

    data_output = clean_data(data_output)

    if not formato_salida:
        try:
            final_out = {
                "Codigo": modulo[0].get('Codigo'),
                "Nombre": modulo[0].get('Nombre'),
                "Data": {
                    "flag": modulo[0].get('Data').get('flag'),
                    "BoletinOficial": data_output
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
                    "BoletinOficial": {}
                }
            }
    else:
        try:
            final_out = {
                "BoletinOficial": {
                    "Codigo": modulo[0].get('Codigo'),
                    "Nombre": modulo[0].get('Nombre'),
                    "Data": {
                        "flag": modulo[0].get('Data').get('flag'),
                        "BoletinOficial": data_output
                    }
                }
            }
        except Exception as e:
            print(f"Error generando la salida final (formato_salida=True): {e}")
            traceback.print_exc()
            final_out = {
                "BoletinOficial": {
                    "Codigo": codigo,
                    "Nombre": nombre,
                    "Data": {
                        "flag": False,
                        "BoletinOficial": {}
                    }
                }
            }
    return final_out

def boletinoficial(nodo):
    return {
        'ExtincionPatrimonioFamiliar': extincion_patrimonio_familiar(nodo.get('ExtincionPatrimonioFamiliar', {})),
        'ConstitucionPatrimonioFamiliar': constitucion_patrimonio_familiar(nodo.get('ConstitucionPatrimonioFamiliar', {})),
        'ObligacionDarDinero': obligacion_dar_dinero(nodo.get('ObligacionDarDinero', {})),
        'RematesBienesMuebles': remates_bienes_muebles(nodo.get('RematesBienesMuebles', {})),
        'RematesBienesInmuebles': remates_bienes_inmuebles(nodo.get('RematesBienesInmuebles', {})),
        'ConvocatoriaAccredores': convocatoria_accredores(nodo.get('ConvocatoriaAccredores', {})),
        'AvisosQuiebra': avisos_quiebra(nodo.get('AvisosQuiebra', {})),
        'FusionSociedades': fusion_sociedades(nodo.get('FusionSociedades', {})),
        'EscisionPatrimonio': escision_patrimonio(nodo.get('EscisionPatrimonio', {})),
        'RematesWarrants': remates_warrants(nodo.get('RematesWarrants', {})),
        'Disoluciones': disoluciones(nodo.get('Disoluciones', {})),
        'CambiosCapital': cambios_capital(nodo.get('CambiosCapital', {}))
    }

def extincion_patrimonio_familiar(nodo):
    return {
        'PatrimonioFamiliar': [
            {
                'FechaComunicacion': item.get('FechaComunicacion'),
                'FechaPublicacion': item.get('FechaPublicacion'),
                'Personas': personas(item.get('Personas', {})),
                'Bienes': bienes(item.get('Bienes', {}))
            } for item in nodo.get('PatrimonioFamiliar', [])
        ]
    }

def constitucion_patrimonio_familiar(nodo):
    return {
        'PatrimonioFamiliar': [
            {
                'FechaComunicacion': item.get('FechaComunicacion'),
                'FechaPublicacion': item.get('FechaPublicacion'),
                'Personas': personas(item.get('Personas', {})),
                'Bienes': bienes(item.get('Bienes', {}))
            } for item in nodo.get('PatrimonioFamiliar', [])
        ]
    }

def obligacion_dar_dinero(nodo):
    return {
        'Obligacion': [
            {
                'Motivo': item.get('Motivo'),
                'Divisa': item.get('Divisa'),
                'Monto': item.get('Monto'),
                'Juzgado': item.get('Juzgado'),
                'FechaResolucion': item.get('FechaResolucion'),
                'FechaPublicacion': item.get('FechaPublicacion'),
                'Acreedores': acreedores(item.get('Acreedores', {})),
                'Deudores': deudores(item.get('Deudores', {}))
            } for item in nodo.get('Obligacion', [])
        ]
    }

def remates_bienes_muebles(nodo):
    return {
        'RemateMueble': [
            {
                'NumeroExpediente': item.get('NumeroExpediente'),
                'NumeroRemate': item.get('NumeroRemate'),
                'Motivo': item.get('Motivo'),
                'Juzgado': item.get('Juzgado'),
                'EncargoDe': item.get('EncargoDe'),
                'Divisa': item.get('Divisa'),
                'MontoTasacion': item.get('MontoTasacion'),
                'MontoBase': item.get('MontoBase'),
                'FechaPublicacion': item.get('FechaPublicacion'),
                'Ubigeo': item.get('Ubigeo'),
                'Direccion': item.get('Direccion'),
                'Demandantes': demandantes(item.get('Demandantes', {})),
                'Demandados': demandados(item.get('Demandados', {})),
                'Muebles': muebles(item.get('Muebles', {})),
                'Inmuebles': inmuebles(item.get('Inmuebles', {})),
                'Mercaderias': mercaderias(item.get('Mercaderias', {}))
            } for item in nodo.get('RemateMueble', [])
        ]
    }

def remates_bienes_inmuebles(nodo):
    return {
        'RemateInmueble': [
            {
                'NumeroExpediente': item.get('NumeroExpediente'),
                'NumeroRemate': item.get('NumeroRemate'),
                'Motivo': item.get('Motivo'),
                'Juzgado': item.get('Juzgado'),
                'Divisa': item.get('Divisa'),
                'MontoTasacion': item.get('MontoTasacion'),
                'MontoBase': item.get('MontoBase'),
                'FechaPublicacion': item.get('FechaPublicacion'),
                'Ubigeo': item.get('Ubigeo'),
                'Direccion': item.get('Direccion'),
                'Demandantes': demandantes(item.get('Demandantes', {})),
                'Demandados': demandados(item.get('Demandados', {})),
                'Muebles': muebles(item.get('Muebles', {})),
                'Inmuebles': inmuebles(item.get('Inmuebles', {})),
                'Mercaderias': mercaderias(item.get('Mercaderias', {}))
            } for item in nodo.get('RemateInmueble', [])
        ]
    }

def convocatoria_accredores(nodo):
    return {
        'Convocatoria': [
            {
                'Motivo': item.get('Motivo'),
                'Numero': item.get('Numero'),
                'FechaPublicacion': item.get('FechaPublicacion'),
                'Juzgado': item.get('Juzgado'),
                'Personas': personas(item.get('Personas', {}))
            } for item in nodo.get('Convocatoria', [])
        ]
    }

def avisos_quiebra(nodo):
    return {
        'AvisoQuiebra': [
            {
                'NumeroExpediente': item.get('NumeroExpediente'),
                'FechaPublicacion': item.get('FechaPublicacion'),
                'Juzgado': item.get('Juzgado'),
                'Personas': personas(item.get('Personas', {}))
            } for item in nodo.get('AvisoQuiebra', [])
        ]
    }

def fusion_sociedades(nodo):
    return {
        'Fusion': [
            {
                'Motivo': item.get('Motivo'),
                'FechaPublicacion': item.get('FechaPublicacion'),
                'Personas': personas(item.get('Personas', {})),
                'Sociedades': sociedades(item.get('Sociedades', {}))
            } for item in nodo.get('Fusion', [])
        ]
    }

def escision_patrimonio(nodo):
    return {
        'Escision': [
            {
                'Motivo': item.get('Motivo'),
                'FechaPublicacion': item.get('FechaPublicacion'),
                'Personas': personas(item.get('Personas', {})),
                'Sociedades': sociedades(item.get('Sociedades', {}))
            } for item in nodo.get('Escision', [])
        ]
    }

def remates_warrants(nodo):
    return {
        'RemateWarrant': [
            {
                'NumeroExpediente': item.get('NumeroExpediente'),
                'NumeroRemate': item.get('NumeroRemate'),
                'Motivo': item.get('Motivo'),
                'Juzgado': item.get('Juzgado'),
                'EncargoDe': item.get('EncargoDe'),
                'Divisa': item.get('Divisa'),
                'MontoTasacion': item.get('MontoTasacion'),
                'MontoBase': item.get('MontoBase'),
                'FechaPublicacion': item.get('FechaPublicacion'),
                'Ubigeo': item.get('Ubigeo'),
                'Direccion': item.get('Direccion'),
                'Demandantes': demandantes(item.get('Demandantes', {})),
                'Demandados': demandados(item.get('Demandados', {})),
                'Muebles': muebles(item.get('Muebles', {})),
                'Inmuebles': inmuebles(item.get('Inmuebles', {})),
                'Mercaderias': mercaderias(item.get('Mercaderias', {}))
            } for item in nodo.get('RemateWarrant', [])
        ]
    }

def disoluciones(nodo):
    return {
        'Disolucion': [
            {
                'Motivo': item.get('Motivo'),
                'FechaPublicacion': item.get('FechaPublicacion'),
                'Personas': personas(item.get('Personas', {})),
                'Sociedades': sociedades(item.get('Sociedades', {}))
            } for item in nodo.get('Disolucion', [])
        ]
    }

def cambios_capital(nodo):
    return {
        'CambiosCapital': [
            {
                'Motivo': item.get('Motivo'),
                'FechaPublicacion': item.get('FechaPublicacion'),
                'Personas': personas(item.get('Personas', {})),
                'Sociedades': sociedades(item.get('Sociedades', {}))
            } for item in nodo.get('CambiosCapital', [])
        ]
    }

def personas(nodo):
    return {
        'Personas': [
            {
                'Nombre': item.get('Nombre'),
                'Paterno': item.get('Paterno'),
                'Materno': item.get('Materno'),
                'RazonSocial': item.get('RazonSocial'),
                'DocumentoIdentidad': documento_identidad(item.get('DocumentoIdentidad', {})),
                'Sociedades': sociedades(item.get('Sociedades', {}))
            } for item in nodo.get('Personas', [])
        ]
    }

def bienes(nodo):
    return {
        'Bienes': [
            {
                'Tipo': item.get('Tipo'),
                'Ubicacion': item.get('Ubicacion'),
                'DomicilioLegal': item.get('DomicilioLegal'),
                'FechaAdquisicion': item.get('FechaAdquisicion'),
                'Moneda': item.get('Moneda'),
                'Monto': item.get('Monto'),
                'EntidadFinanciera': item.get('EntidadFinanciera'),
                'Hipoteca': item.get('Hipoteca')
            } for item in nodo.get('Bienes', [])
        ]
    }

def acreedores(nodo):
    return {
        'Acreedores': [
            {
                'Nombre': item.get('Nombre'),
                'Paterno': item.get('Paterno'),
                'Materno': item.get('Materno'),
                'RazonSocial': item.get('RazonSocial'),
                'DocumentoIdentidad': documento_identidad(item.get('DocumentoIdentidad', {})),
                'Sociedades': sociedades(item.get('Sociedades', {}))
            } for item in nodo.get('Acreedores', [])
        ]
    }

def deudores(nodo):
    return {
        'Deudores': [
            {
                'Nombre': item.get('Nombre'),
                'Paterno': item.get('Paterno'),
                'Materno': item.get('Materno'),
                'RazonSocial': item.get('RazonSocial'),
                'DocumentoIdentidad': documento_identidad(item.get('DocumentoIdentidad', {})),
                'Sociedades': sociedades(item.get('Sociedades', {}))
            } for item in nodo.get('Deudores', [])
        ]
    }

def demandantes(nodo):
    return {
        'Demandantes': [
            {
                'Nombre': item.get('Nombre'),
                'Paterno': item.get('Paterno'),
                'Materno': item.get('Materno'),
                'RazonSocial': item.get('RazonSocial'),
                'DocumentoIdentidad': documento_identidad(item.get('DocumentoIdentidad', {})),
                'Sociedades': sociedades(item.get('Sociedades', {}))
            } for item in nodo.get('Demandantes', [])
        ]
    }

def demandados(nodo):
    return {
        'Demandados': [
            {
                'Nombre': item.get('Nombre'),
                'Paterno': item.get('Paterno'),
                'Materno': item.get('Materno'),
                'RazonSocial': item.get('RazonSocial'),
                'DocumentoIdentidad': documento_identidad(item.get('DocumentoIdentidad', {})),
                'Sociedades': sociedades(item.get('Sociedades', {}))
            } for item in nodo.get('Demandados', [])
        ]
    }

def muebles(nodo):
    return {
        'Muebles': [
            {
                'Descripcion': item.get('Descripcion'),
                'Marca': item.get('Marca'),
                'Modelo': item.get('Modelo'),
                'Serie': item.get('Serie'),
                'Caracteristicas': item.get('Caracteristicas')
            } for item in nodo.get('Muebles', [])
        ]
    }

def inmuebles(nodo):
    return {
        'Inmuebles': [
            {
                'Descripcion': item.get('Descripcion'),
                'Ubicacion': item.get('Ubicacion'),
                'PartidaRegistral': item.get('PartidaRegistral'),
                'FichaTomo': item.get('FichaTomo'),
                'AreaTerreno': item.get('AreaTerreno'),
                'AreaConstruida': item.get('AreaConstruida'),
                'FechaAdquisicion': item.get('FechaAdquisicion'),
                'Moneda': item.get('Moneda'),
                'Monto': item.get('Monto'),
                'EntidadFinanciera': item.get('EntidadFinanciera'),
                'Hipoteca': item.get('Hipoteca')
            } for item in nodo.get('Inmuebles', [])
        ]
    }

def mercaderias(nodo):
    return {
        'Mercaderias': [
            {
                'Descripcion': item.get('Descripcion'),
                'Cantidad': item.get('Cantidad'),
                'UnidadMedida': item.get('UnidadMedida'),
                'ValorUnitario': item.get('ValorUnitario'),
                'Caracteristicas': item.get('Caracteristicas')
            } for item in nodo.get('Mercaderias', [])
        ]
    }

def sociedades(nodo):
    return {
        'Sociedades': [
            {
                'Nombre': item.get('Nombre'),
                'RUC': item.get('RUC'),
                'TipoSociedad': item.get('TipoSociedad'),
                'FechaInicio': item.get('FechaInicio'),
                'FechaFin': item.get('FechaFin')
            } for item in nodo.get('Sociedades', [])
        ]
    }

def documento_identidad(nodo):
    return {
        'TipoDocumento': nodo.get('TipoDocumento'),
        'NumeroDocumento': nodo.get('NumeroDocumento'),
        'PaisExpedicion': nodo.get('PaisExpedicion'),
        'FechaExpedicion': nodo.get('FechaExpedicion'),
        'FechaVencimiento': nodo.get('FechaVencimiento')
    }

if __name__ == "__main__":
    try:
        payload = {
            'applicants': [
                {
                    'personalInformation': {
                        'name': 'Juan',
                        'lastName': 'Perez',
                        'motherLastName': 'Gomez',
                        'documentType': 'DNI',
                        'documentNumber': '12345678',
                        'country': 'PE',
                        'expirationDate': '2024-12-31'
                    },
                    'companies': [
                        {
                            'businessName': 'Empresa1',
                            'ruc': '20123456789',
                            'companyType': 'Sociedad Anonima',
                            'startDate': '2010-01-01',
                            'endDate': '2023-12-31'
                        },
                        {
                            'businessName': 'Empresa2',
                            'ruc': '20456789123',
                            'companyType': 'Sociedad Comercial de Responsabilidad Limitada',
                            'startDate': '2015-06-01',
                            'endDate': '2023-12-31'
                        }
                    ]
                },
                {
                    'personalInformation': {
                        'name': 'Maria',
                        'lastName': 'Lopez',
                        'motherLastName': 'Garcia',
                        'documentType': 'DNI',
                        'documentNumber': '87654321',
                        'country': 'PE',
                        'expirationDate': '2023-10-15'
                    },
                    'companies': [
                        {
                            'businessName': 'Empresa3',
                            'ruc': '20987654321',
                            'companyType': 'Sociedad Anonima Cerrada',
                            'startDate': '2017-03-20',
                            'endDate': '2023-12-31'
                        }
                    ]
                }
            ]
        }

        import json

        with open('test.json', 'w') as f:
            json.dump(payload, f, indent=2)

        with open('test.json') as f:
            data = json.load(f)

        resultado = [
            {
                'EntidadesJudiciales': entidades_judiciales(data)
            },
            {
                'Disolucion': disoluciones(data)
            },
            {
                'CambiosCapital': cambios_capital(data)
            },
            {
                'AvisoQuiebra': avisos_quiebra(data)
            },
            {
                'Convocatoria': convocatorias(data)
            },
            {
                'Escision': escision_patrimonio(data)
            },
            {
                'Fusion': fusion_sociedades(data)
            },
            {
                'RemateWarrant': remates_warrants(data)
            }
        ]

        with open('resultado.json', 'w') as f:
            json.dump(resultado, f, indent=2)

        print('Proceso terminado correctamente.')

    except Exception as e:
        print(f'Error: {e}')
