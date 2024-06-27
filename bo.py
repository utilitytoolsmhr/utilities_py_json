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
        'CambiosCapital': cambios_capital(nodo.get('CambiosCapital', {})),
        'EntidadesJudiciales': entidades_judiciales(nodo.get('EntidadesJudiciales', {})),
        'Convocatorias': convocatorias(nodo.get('Convocatorias', {}))
    }

def extincion_patrimonio_familiar(nodo):
    return {
        'PatrimonioFamiliar': [
            {
                'FechaComunicacion': text_fix(item.get('FechaComunicacion')),
                'FechaPublicacion': text_fix(item.get('FechaPublicacion')),
                'Personas': personas(item.get('Personas', {})),
                'Bienes': bienes(item.get('Bienes', {}))
            } for item in nodo.get('PatrimonioFamiliar', [])
        ]
    }

def constitucion_patrimonio_familiar(nodo):
    return {
        'PatrimonioFamiliar': [
            {
                'FechaComunicacion': text_fix(item.get('FechaComunicacion')),
                'FechaPublicacion': text_fix(item.get('FechaPublicacion')),
                'Personas': personas(item.get('Personas', {})),
                'Bienes': bienes(item.get('Bienes', {}))
            } for item in nodo.get('PatrimonioFamiliar', [])
        ]
    }

def obligacion_dar_dinero(nodo):
    return {
        'Obligacion': [
            {
                'Motivo': text_fix(item.get('Motivo')),
                'Divisa': text_fix(item.get('Divisa')),
                'Monto': float_fix(item.get('Monto')),
                'Juzgado': text_fix(item.get('Juzgado')),
                'FechaResolucion': text_fix(item.get('FechaResolucion')),
                'FechaPublicacion': text_fix(item.get('FechaPublicacion')),
                'Acreedores': acreedores(item.get('Acreedores', {})),
                'Deudores': deudores(item.get('Deudores', {}))
            } for item in nodo.get('Obligacion', [])
        ]
    }

def remates_bienes_muebles(nodo):
    return {
        'RemateMueble': [
            {
                'NumeroExpediente': text_fix(item.get('NumeroExpediente')),
                'NumeroRemate': text_fix(item.get('NumeroRemate')),
                'Motivo': text_fix(item.get('Motivo')),
                'Juzgado': text_fix(item.get('Juzgado')),
                'EncargoDe': text_fix(item.get('EncargoDe')),
                'Divisa': text_fix(item.get('Divisa')),
                'MontoTasacion': float_fix(item.get('MontoTasacion')),
                'MontoBase': float_fix(item.get('MontoBase')),
                'FechaPublicacion': text_fix(item.get('FechaPublicacion')),
                'Ubigeo': text_fix(item.get('Ubigeo')),
                'Direccion': text_fix(item.get('Direccion')),
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
                'NumeroExpediente': text_fix(item.get('NumeroExpediente')),
                'NumeroRemate': text_fix(item.get('NumeroRemate')),
                'Motivo': text_fix(item.get('Motivo')),
                'Juzgado': text_fix(item.get('Juzgado')),
                'Divisa': text_fix(item.get('Divisa')),
                'MontoTasacion': float_fix(item.get('MontoTasacion')),
                'MontoBase': float_fix(item.get('MontoBase')),
                'FechaPublicacion': text_fix(item.get('FechaPublicacion')),
                'Ubigeo': text_fix(item.get('Ubigeo')),
                'Direccion': text_fix(item.get('Direccion')),
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
                'Motivo': text_fix(item.get('Motivo')),
                'Numero': text_fix(item.get('Numero')),
                'FechaComunicado': text_fix(item.get('FechaComunicado')),
                'FechaPublicacion': text_fix(item.get('FechaPublicacion')),
                'FechaJunta': text_fix(item.get('FechaJunta')),
                'HoraJunta': text_fix(item.get('HoraJunta')),
                'Direccion': text_fix(item.get('Direccion')),
                'Ubigeo': text_fix(item.get('Ubigeo'))
            } for item in nodo.get('Convocatoria', [])
        ]
    }

def avisos_quiebra(nodo):
    return {
        'Quiebra': [
            {
                'Expediente': text_fix(item.get('Expediente')),
                'FechaResolucion': text_fix(item.get('FechaResolucion')),
                'FechaPublicacion': text_fix(item.get('FechaPublicacion')),
                'Liquidadores': liquidadores(item.get('Liquidadores', {}))
            } for item in nodo.get('Quiebra', [])
        ]
    }

def fusion_sociedades(nodo):
    return {
        'Fusion': [
            {
                'NuevoNombre': text_fix(item.get('NuevoNombre')),
                'Divisa': text_fix(item.get('Divisa')),
                'NuevoCapital': float_fix(item.get('NuevoCapital')),
                'FechaAcuerdo': text_fix(item.get('FechaAcuerdo')),
                'FechaPublicacion': text_fix(item.get('FechaPublicacion')),
                'Empresas': empresas(item.get('Empresas', {}))
            } for item in nodo.get('Fusion', [])
        ]
    }

def escision_patrimonio(nodo):
    return {
        'Escision': [
            {
                'Divisa': text_fix(item.get('Divisa')),
                'PatrimonioEscindido': float_fix(item.get('PatrimonioEscindido')),
                'FechaVigencia': text_fix(item.get('FechaVigencia')),
                'FechaPublicacion': text_fix(item.get('FechaPublicacion')),
                'EscindenteTipoDocumento': text_fix(item.get('EscindenteTipoDocumento')),
                'EscindenteNumeroDocumento': text_fix(item.get('EscindenteNumeroDocumento')),
                'EscindenteNombre': text_fix(item.get('EscindenteNombre')),
                'EscindenteCapital': float_fix(item.get('EscindenteCapital')),
                'BeneficiarioTipoDocumento': text_fix(item.get('BeneficiarioTipoDocumento')),
                'BeneficiarioNumeroDocumento': text_fix(item.get('BeneficiarioNumeroDocumento')),
                'BeneficiarioNombre': text_fix(item.get('BeneficiarioNombre')),
                'BeneficiarioCapital': float_fix(item.get('BeneficiarioCapital'))
            } for item in nodo.get('Escision', [])
        ]
    }

def remates_warrants(nodo):
    return {
        'RemateWarrant': [
            {
                'Motivo': text_fix(item.get('Motivo')),
                'EncargoDe': text_fix(item.get('EncargoDe')),
                'Divisa': text_fix(item.get('Divisa')),
                'MontoTasacion': float_fix(item.get('MontoTasacion')),
                'MontoBase': float_fix(item.get('MontoBase')),
                'FechaPublicacion': text_fix(item.get('FechaPublicacion')),
                'Ubigeo': text_fix(item.get('Ubigeo')),
                'Direccion': text_fix(item.get('Direccion')),
                'FechaRemate': text_fix(item.get('FechaRemate')),
                'HoraRemate': text_fix(item.get('HoraRemate')),
                'Demandantes': demandantes(item.get('Demandantes', {})),
                'Mercaderias': mercaderias(item.get('Mercaderias', {}))
            } for item in nodo.get('RemateWarrant', [])
        ]
    }

def disoluciones(nodo):
    return {
        'Disolucion': [
            {
                'Direccion': text_fix(item.get('Direccion')),
                'Ubigeo': text_fix(item.get('Ubigeo')),
                'FechaVigencia': text_fix(item.get('FechaVigencia')),
                'FechaPublicacion': text_fix(item.get('FechaPublicacion')),
                'Liquidadores': liquidadores(item.get('Liquidadores', {}))
            } for item in nodo.get('Disolucion', [])
        ]
    }

def cambios_capital(nodo):
    return {
        'Cambio': [
            {
                'FechaAcuerdo': text_fix(item.get('FechaAcuerdo')),
                'Divisa': text_fix(item.get('Divisa')),
                'TipoCambio': text_fix(item.get('TipoCambio')),
                'MontoAcuerdo': float_fix(item.get('MontoAcuerdo')),
                'CapitalAnterior': float_fix(item.get('CapitalAnterior')),
                'CapitalActual': float_fix(item.get('CapitalActual')),
                'FechaPublicacion': text_fix(item.get('FechaPublicacion'))
            } for item in nodo.get('Cambio', [])
        ]
    }

def personas(nodo):
    return {
        'Persona': [
            {
                'TipoDocumento': text_fix(item.get('TipoDocumento')),
                'NumeroDocumento': text_fix(item.get('NumeroDocumento')),
                'Nombres': text_fix(item.get('Nombres')),
                'Tipo': text_fix(item.get('Tipo'))
            } for item in nodo.get('Persona', [])
        ]
    }

def bienes(nodo):
    return {
        'Bien': [
            {
                'Tipo': text_fix(item.get('Tipo')),
                'RegistroPublico': text_fix(item.get('RegistroPublico')),
                'Direccion': text_fix(item.get('Direccion')),
                'Ubigeo': text_fix(item.get('Ubigeo'))
            } for item in nodo.get('Bien', [])
        ]
    }

def acreedores(nodo):
    return {
        'Acreedor': [
            {
                'TipoDocumento': text_fix(item.get('TipoDocumento')),
                'NumeroDocumento': text_fix(item.get('NumeroDocumento')),
                'Nombres': text_fix(item.get('Nombres')),
                'Tipo': text_fix(item.get('Tipo'))
            } for item in nodo.get('Acreedor', [])
        ]
    }

def deudores(nodo):
    return {
        'Deudor': [
            {
                'TipoDocumento': text_fix(item.get('TipoDocumento')),
                'NumeroDocumento': text_fix(item.get('NumeroDocumento')),
                'Nombres': text_fix(item.get('Nombres')),
                'Tipo': text_fix(item.get('Tipo'))
            } for item in nodo.get('Deudor', [])
        ]
    }

def demandantes(nodo):
    return {
        'Demandante': [
            {
                'NumeroDocumento': text_fix(item.get('NumeroDocumento')),
                'TipoDocumento': text_fix(item.get('TipoDocumento')),
                'Nombres': text_fix(item.get('Nombres')),
                'Tipo': text_fix(item.get('Tipo'))
            } for item in nodo.get('Demandante', [])
        ]
    }

def demandados(nodo):
    return {
        'Demandado': [
            {
                'NumeroDocumento': text_fix(item.get('NumeroDocumento')),
                'TipoDocumento': text_fix(item.get('TipoDocumento')),
                'Nombres': text_fix(item.get('Nombres')),
                'Tipo': text_fix(item.get('Tipo'))
            } for item in nodo.get('Demandado', [])
        ]
    }

def muebles(nodo):
    return {
        'Mueble': [
            {
                'Tipo': text_fix(item.get('Tipo')),
                'Caracteristica': text_fix(item.get('Caracteristica')),
                'MontoTasacion': float_fix(item.get('MontoTasacion')),
                'MontoBase': float_fix(item.get('MontoBase'))
            } for item in nodo.get('Mueble', [])
        ]
    }

def inmuebles(nodo):
    return {
        'Inmueble': [
            {
                'Tipo': text_fix(item.get('Tipo')),
                'Caracteristica': text_fix(item.get('Caracteristica')),
                'MontoTasacion': float_fix(item.get('MontoTasacion')),
                'MontoBase': float_fix(item.get('MontoBase'))
            } for item in nodo.get('Inmueble', [])
        ]
    }

def mercaderias(nodo):
    return {
        'Mercaderia': [
            {
                'Tipo': text_fix(item.get('Tipo')),
                'Caracteristica': text_fix(item.get('Caracteristica')),
                'MontoTasacion': float_fix(item.get('MontoTasacion')),
                'MontoBase': float_fix(item.get('MontoBase'))
            } for item in nodo.get('Mercaderia', [])
        ]
    }

def liquidadores(nodo):
    return {
        'Liquidador': [
            {
                'NumeroDocumento': text_fix(item.get('NumeroDocumento')),
                'TipoDocumento': text_fix(item.get('TipoDocumento')),
                'Nombres': text_fix(item.get('Nombres'))
            } for item in nodo.get('Liquidador', [])
        ]
    }

def empresas(nodo):
    return {
        'Empresa': [
            {
                'NumeroDocumento': text_fix(item.get('NumeroDocumento')),
                'TipoDocumento': text_fix(item.get('TipoDocumento')),
                'Nombres': text_fix(item.get('Nombres'))
            } for item in nodo.get('Empresa', [])
        ]
    }

def entidades_judiciales(nodo):
    return {
        'EntidadJudicial': [
            {
                'TipoDocumento': text_fix(item.get('TipoDocumento')),
                'NumeroDocumento': text_fix(item.get('NumeroDocumento')),
                'Nombres': text_fix(item.get('Nombres')),
                'Tipo': text_fix(item.get('Tipo'))
            } for item in nodo.get('EntidadJudicial', [])
        ]
    }

def convocatorias(nodo):
    return {
        'Convocatoria': [
            {
                'Motivo': text_fix(item.get('Motivo')),
                'Numero': text_fix(item.get('Numero')),
                'FechaComunicado': text_fix(item.get('FechaComunicado')),
                'FechaPublicacion': text_fix(item.get('FechaPublicacion')),
                'FechaJunta': text_fix(item.get('FechaJunta')),
                'HoraJunta': text_fix(item.get('HoraJunta')),
                'Direccion': text_fix(item.get('Direccion')),
                'Ubigeo': text_fix(item.get('Ubigeo'))
            } for item in nodo.get('Convocatoria', [])
        ]
    }
