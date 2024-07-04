import json
import os
import sys
import traceback
from pe_utils import int_fix, float_fix, text_fix, get_value, xsi_to_null, obj_fix

def main(payload):
    print(payload)
    primaryConsumer = None
    
    try:
        applicants = payload.get('applicants')
        if isinstance(applicants, list) and applicants:
            primaryConsumer = applicants[0]
        elif isinstance(applicants, dict):
            primaryConsumer = applicants.get('primaryConsumer')
        
        if not primaryConsumer:
            raise ValueError("No se pudo obtener el primaryConsumer")
    except Exception as e:
        print(f"Error obteniendo primaryConsumer: {e}")
        traceback.print_exc()
        return None

    try:
        tipoPersona = int(primaryConsumer.get('personalInformation', {}).get('tipoPersona', 0))
        formato_salida = primaryConsumer.get('personalInformation', {}).get('formatoSalida', False)
    except Exception as e:
        print(f"Error obteniendo tipoPersona o formato_salida: {e}")
        traceback.print_exc()
        return None

    codigo_modulo = 869 if tipoPersona == 1 else 623

    try:
        payload = primaryConsumer.get('equifax-pe-middleware', {})
        xsi_to_null(payload)

        nombre = 'BOLETÍN OFICIAL'
        target = 'BoletinOficial'
        codigo = codigo_modulo
        modulos = payload.get('dataSourceResponse', {}).get('GetReporteOnlineResponse', {}).get('ReporteCrediticio', {}).get('Modulos', {}).get('Modulo', [])
        modulo = [modulo for modulo in modulos if modulo.get('Data') is not None and nombre in modulo.get('Nombre', '')]

        if len(modulo) > 1:
            modulo_filtrado = [mod for mod in modulo if mod.get('Data', {}).get(target)]
            modulo = modulo_filtrado if len(modulo_filtrado) == 1 else modulo

        if not modulo:
            raise ValueError("Modulo sin datos")

        nodo = modulo[0].get('Data', {}).get(target, {})
        nodo = obj_fix(nodo)
    except Exception as e:
        print(f"Error procesando los datos de entrada: {e}")
        traceback.print_exc()
        return None

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

    #################################################
    ################## Set Output ###################
    #################################################

    final_out = {}
    try:
        if not formato_salida:
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
        else:
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
        print(f"Error generando la salida final: {e}")
        traceback.print_exc()

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
    if not isinstance(nodo, dict):
        return {}
    
    return {
        'PatrimonioFamiliar': [
            {
                'FechaComunicacion': text_fix(item.get('FechaComunicacion')),
                'FechaPublicacion': text_fix(item.get('FechaPublicacion')),
                'Personas': personas(item.get('Personas', {})),
                'Bienes': bienes(item.get('Bienes', {}))
            } for item in nodo.get('PatrimonioFamiliar', []) if isinstance(nodo.get('PatrimonioFamiliar', []), list)
        ]
    }

def constitucion_patrimonio_familiar(nodo):
    if not isinstance(nodo, dict):
        return {}
    
    return {
        'PatrimonioFamiliar': [
            {
                'FechaComunicacion': text_fix(item.get('FechaComunicacion')),
                'FechaPublicacion': text_fix(item.get('FechaPublicacion')),
                'Personas': personas(item.get('Personas', {})),
                'Bienes': bienes(item.get('Bienes', {}))
            } for item in nodo.get('PatrimonioFamiliar', []) if isinstance(nodo.get('PatrimonioFamiliar', []), list)
        ]
    }

def obligacion_dar_dinero(nodo):
    if not isinstance(nodo, dict):
        return {}
    
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
            } for item in nodo.get('Obligacion', []) if isinstance(nodo.get('Obligacion', []), list)
        ]
    }

def remates_bienes_muebles(nodo):
    if not isinstance(nodo, dict):
        return {}
    
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
            } for item in nodo.get('RemateMueble', []) if isinstance(nodo.get('RemateMueble', []), list)
        ]
    }

def remates_bienes_inmuebles(nodo):
    if not isinstance(nodo, dict):
        return {}
    
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
            } for item in nodo.get('RemateInmueble', []) if isinstance(nodo.get('RemateInmueble', []), list)
        ]
    }

def convocatoria_accredores(nodo):
    if not isinstance(nodo, dict):
        return {}
    
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
            } for item in nodo.get('Convocatoria', []) if isinstance(nodo.get('Convocatoria', []), list)
        ]
    }

def avisos_quiebra(nodo):
    if not isinstance(nodo, dict):
        return {}
    
    return {
        'Quiebra': [
            {
                'Expediente': text_fix(item.get('Expediente')),
                'FechaResolucion': text_fix(item.get('FechaResolucion')),
                'FechaPublicacion': text_fix(item.get('FechaPublicacion')),
                'Liquidadores': liquidadores(item.get('Liquidadores', {}))
            } for item in nodo.get('Quiebra', []) if isinstance(nodo.get('Quiebra', []), list)
        ]
    }

def fusion_sociedades(nodo):
    if not isinstance(nodo, dict):
        return {}
    
    return {
        'Fusion': [
            {
                'NuevoNombre': text_fix(item.get('NuevoNombre')),
                'Divisa': text_fix(item.get('Divisa')),
                'NuevoCapital': float_fix(item.get('NuevoCapital')),
                'FechaAcuerdo': text_fix(item.get('FechaAcuerdo')),
                'FechaPublicacion': text_fix(item.get('FechaPublicacion')),
                'Empresas': empresas(item.get('Empresas', {}))
            } for item in nodo.get('Fusion', []) if isinstance(nodo.get('Fusion', []), list)
        ]
    }

def escision_patrimonio(nodo):
    if not isinstance(nodo, dict):
        return {}
    
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
            } for item in nodo.get('Escision', []) if isinstance(nodo.get('Escision', []), list)
        ]
    }

def remates_warrants(nodo):
    if not isinstance(nodo, dict):
        return {}
    
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
            } for item in nodo.get('RemateWarrant', []) if isinstance(nodo.get('RemateWarrant', []), list)
        ]
    }

def disoluciones(nodo):
    if not isinstance(nodo, dict):
        return {}
    
    return {
        'Disolucion': [
            {
                'Direccion': text_fix(item.get('Direccion')),
                'Ubigeo': text_fix(item.get('Ubigeo')),
                'FechaVigencia': text_fix(item.get('FechaVigencia')),
                'FechaPublicacion': text_fix(item.get('FechaPublicacion')),
                'Liquidadores': liquidadores(item.get('Liquidadores', {}))
            } for item in nodo.get('Disolucion', []) if isinstance(nodo.get('Disolucion', []), list)
        ]
    }

def cambios_capital(nodo):
    if not isinstance(nodo, dict):
        return {}
    
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
            } for item in nodo.get('Cambio', []) if isinstance(nodo.get('Cambio', []), list)
        ]
    }

def personas(nodo):
    if not isinstance(nodo, dict):
        return {}
    
    return {
        'Persona': [
            {
                'TipoDocumento': text_fix(item.get('TipoDocumento')),
                'NumeroDocumento': text_fix(item.get('NumeroDocumento')),
                'Nombres': text_fix(item.get('Nombres')),
                'Tipo': text_fix(item.get('Tipo'))
            } for item in nodo.get('Persona', []) if isinstance(nodo.get('Persona', []), list)
        ]
    }

def bienes(nodo):
    if not isinstance(nodo, dict):
        return {}
    
    return {
        'Bien': [
            {
                'Tipo': text_fix(item.get('Tipo')),
                'RegistroPublico': text_fix(item.get('RegistroPublico')),
                'Direccion': text_fix(item.get('Direccion')),
                'Ubigeo': text_fix(item.get('Ubigeo'))
            } for item in nodo.get('Bien', []) if isinstance(nodo.get('Bien', []), list)
        ]
    }

def acreedores(nodo):
    if not isinstance(nodo, dict):
        return {}
    
    return {
        'Acreedor': [
            {
                'TipoDocumento': text_fix(item.get('TipoDocumento')),
                'NumeroDocumento': text_fix(item.get('NumeroDocumento')),
                'Nombres': text_fix(item.get('Nombres')),
                'Tipo': text_fix(item.get('Tipo'))
            } for item in nodo.get('Acreedor', []) if isinstance(nodo.get('Acreedor', []), list)
        ]
    }

def deudores(nodo):
    if not isinstance(nodo, dict):
        return {}
    
    return {
        'Deudor': [
            {
                'TipoDocumento': text_fix(item.get('TipoDocumento')),
                'NumeroDocumento': text_fix(item.get('NumeroDocumento')),
                'Nombres': text_fix(item.get('Nombres')),
                'Tipo': text_fix(item.get('Tipo'))
            } for item in nodo.get('Deudor', []) if isinstance(nodo.get('Deudor', []), list)
        ]
    }

def demandantes(nodo):
    if not isinstance(nodo, dict):
        return {}
    
    return {
        'Demandante': [
            {
                'NumeroDocumento': text_fix(item.get('NumeroDocumento')),
                'TipoDocumento': text_fix(item.get('TipoDocumento')),
                'Nombres': text_fix(item.get('Nombres')),
                'Tipo': text_fix(item.get('Tipo'))
            } for item in nodo.get('Demandante', []) if isinstance(nodo.get('Demandante', []), list)
        ]
    }

def demandados(nodo):
    if not isinstance(nodo, dict):
        return {}
    
    return {
        'Demandado': [
            {
                'NumeroDocumento': text_fix(item.get('NumeroDocumento')),
                'TipoDocumento': text_fix(item.get('TipoDocumento')),
                'Nombres': text_fix(item.get('Nombres')),
                'Tipo': text_fix(item.get('Tipo'))
            } for item in nodo.get('Demandado', []) if isinstance(nodo.get('Demandado', []), list)
        ]
    }

def muebles(nodo):
    if not isinstance(nodo, dict):
        return {}
    
    return {
        'Mueble': [
            {
                'Tipo': text_fix(item.get('Tipo')),
                'Caracteristica': text_fix(item.get('Caracteristica')),
                'MontoTasacion': float_fix(item.get('MontoTasacion')),
                'MontoBase': float_fix(item.get('MontoBase'))
            } for item in nodo.get('Mueble', []) if isinstance(nodo.get('Mueble', []), list)
        ]
    }

def inmuebles(nodo):
    if not isinstance(nodo, dict):
        return {}
    
    return {
        'Inmueble': [
            {
                'Tipo': text_fix(item.get('Tipo')),
                'Caracteristica': text_fix(item.get('Caracteristica')),
                'MontoTasacion': float_fix(item.get('MontoTasacion')),
                'MontoBase': float_fix(item.get('MontoBase'))
            } for item in nodo.get('Inmueble', []) if isinstance(nodo.get('Inmueble', []), list)
        ]
    }

def mercaderias(nodo):
    if not isinstance(nodo, dict):
        return {}
    
    return {
        'Mercaderia': [
            {
                'Tipo': text_fix(item.get('Tipo')),
                'Caracteristica': text_fix(item.get('Caracteristica')),
                'MontoTasacion': float_fix(item.get('MontoTasacion')),
                'MontoBase': float_fix(item.get('MontoBase'))
            } for item in nodo.get('Mercaderia', []) if isinstance(nodo.get('Mercaderia', []), list)
        ]
    }

def liquidadores(nodo):
    if not isinstance(nodo, dict):
        return {}
    
    return {
        'Liquidador': [
            {
                'NumeroDocumento': text_fix(item.get('NumeroDocumento')),
                'TipoDocumento': text_fix(item.get('TipoDocumento')),
                'Nombres': text_fix(item.get('Nombres'))
            } for item in nodo.get('Liquidador', []) if isinstance(nodo.get('Liquidador', []), list)
        ]
    }

def empresas(nodo):
    if not isinstance(nodo, dict):
        return {}
    
    return {
        'Empresa': [
            {
                'NumeroDocumento': text_fix(item.get('NumeroDocumento')),
                'TipoDocumento': text_fix(item.get('TipoDocumento')),
                'Nombres': text_fix(item.get('Nombres'))
            } for item in nodo.get('Empresa', []) if isinstance(nodo.get('Empresa', []), list)
        ]
    }

def entidades_judiciales(nodo):
    if not isinstance(nodo, dict):
        return {}
    
    return {
        'EntidadJudicial': [
            {
                'TipoDocumento': text_fix(item.get('TipoDocumento')),
                'NumeroDocumento': text_fix(item.get('NumeroDocumento')),
                'Nombres': text_fix(item.get('Nombres')),
                'Tipo': text_fix(item.get('Tipo'))
            } for item in nodo.get('EntidadJudicial', []) if isinstance(nodo.get('EntidadJudicial', []), list)
        ]
    }

def convocatorias(nodo):
    if not isinstance(nodo, dict):
        return {}
    
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
            } for item in nodo.get('Convocatoria', []) if isinstance(nodo.get('Convocatoria', []), list)
        ]
    }

if __name__ == '__main__':
    with open('response-dss1.json', 'r', encoding='UTF-8') as file:
        request = json.load(file)
        out = json.dumps(main(request), indent=4)
    with open('respond.json', 'w') as file:
        file.write(out)
