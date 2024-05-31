import os
import sys
import traceback
import json
from pe_utils import text_fix

def main(payload):
    try:
        nombre  = 'OTRAS DEUDAS IMPAGAS: RESUMEN'
        target  = 'otras_deudas_impagas:_resumen'
        codigo  = 857
        modulos = payload.get('dataSourceResponse').get('GetReporteOnlineResponse').get('ReporteCrediticio').get('Modulos').get('Modulo')
        modulo  = [modulo for modulo in modulos if modulo.get('Data') is not None and nombre in modulo.get('Nombre')]
        if len(modulo) > 1:
            modulo_filtrado = [modulo_filtrado for modulo_filtrado in modulo if modulo_filtrado.get('Data').get(target)]
            modulo = modulo_filtrado if len(modulo_filtrado) == 1 else modulo
        data = modulo[0].get('Data')
    except Exception as e:
        traceback.print_exc()
        data = None

    def process_otrasdeudasimpagas(data):
        if not data: return None
        return {
            'Protestos': process_protestos(data.get('Protestos')),
            'CuentasCerradas': process_cuentascerradas(data.get('CuentasCerradas')),
            'TarjetasAnuladas': process_tarjetasanuladas(data.get('TarjetasAnuladas')),
            'InquilinosMorosos': process_inquilinosmorosos(data.get('InquilinosMorosos')),
            'Sicom': process_sicom(data.get('Sicom')),
            'NegativoSunat': process_negativosunat(data.get('NegativoSunat')),
            'Omisos': process_omisos(data.get('Omisos')),
            'Redam': process_redam(data.get('Redam')),
        }

        def process_protestos(data):
            if not data: return None
            return {
                'ProtestosNoAclarados': process_protestosnoaclarados(data.get('ProtestosNoAclarados')),
                'ProtestosAclarados': process_protestosaclarados(data.get('ProtestosAclarados')),
            }

            def process_protestosnoaclarados(data):
                if not data: return None
                return {
                    'xsi:nil': text_fix(data.get('xsi:nil')),
                    'xmlns:xsi': text_fix(data.get('xmlns:xsi')),
                }

            def process_protestosaclarados(data):
                if not data: return None
                return {
                    'xsi:nil': text_fix(data.get('xsi:nil')),
                    'xmlns:xsi': text_fix(data.get('xmlns:xsi')),
                }

        def process_cuentascerradas(data):
            if not data: return None
            return {
                'Cabecera': process_cabecera(data.get('Cabecera')),
                'Detalle': process_detalle(data.get('Detalle')),
            }

            def process_cabecera(data):
                if not data: return None
                return {
                    'xsi:nil': text_fix(data.get('xsi:nil')),
                    'xmlns:xsi': text_fix(data.get('xmlns:xsi')),
                }

            def process_detalle(data):
                if not data: return None
                return {
                    'xsi:nil': text_fix(data.get('xsi:nil')),
                    'xmlns:xsi': text_fix(data.get('xmlns:xsi')),
                }

        def process_tarjetasanuladas(data):
            if not data: return None
            return {
                'Cabecera': process_cabecera(data.get('Cabecera')),
                'Detalle': process_detalle(data.get('Detalle')),
            }

            def process_cabecera(data):
                if not data: return None
                return {
                    'xsi:nil': text_fix(data.get('xsi:nil')),
                    'xmlns:xsi': text_fix(data.get('xmlns:xsi')),
                }

            def process_detalle(data):
                if not data: return None
                return {
                    'xsi:nil': text_fix(data.get('xsi:nil')),
                    'xmlns:xsi': text_fix(data.get('xmlns:xsi')),
                }

        def process_inquilinosmorosos(data):
            if not data: return None
            return {
                'Cabecera': process_cabecera(data.get('Cabecera')),
                'Detalle': process_detalle(data.get('Detalle')),
            }

            def process_cabecera(data):
                if not data: return None
                return {
                    'xsi:nil': text_fix(data.get('xsi:nil')),
                    'xmlns:xsi': text_fix(data.get('xmlns:xsi')),
                }

            def process_detalle(data):
                if not data: return None
                return {
                    'xsi:nil': text_fix(data.get('xsi:nil')),
                    'xmlns:xsi': text_fix(data.get('xmlns:xsi')),
                }

        def process_sicom(data):
            if not data: return None
            return {
                'Cabecera': process_cabecera(data.get('Cabecera')),
                'Detalle': process_detalle(data.get('Detalle')),
            }

            def process_cabecera(data):
                if not data: return None
                return {
                    'xsi:nil': text_fix(data.get('xsi:nil')),
                    'xmlns:xsi': text_fix(data.get('xmlns:xsi')),
                }

            def process_detalle(data):
                if not data: return None
                return {
                    'xsi:nil': text_fix(data.get('xsi:nil')),
                    'xmlns:xsi': text_fix(data.get('xmlns:xsi')),
                }

        def process_negativosunat(data):
            if not data: return None
            return {
                'Cabecera': process_cabecera(data.get('Cabecera')),
                'Detalle': process_detalle(data.get('Detalle')),
            }

            def process_cabecera(data):
                if not data: return None
                return {
                    'xsi:nil': text_fix(data.get('xsi:nil')),
                    'xmlns:xsi': text_fix(data.get('xmlns:xsi')),
                }

            def process_detalle(data):
                if not data: return None
                return {
                    'xsi:nil': text_fix(data.get('xsi:nil')),
                    'xmlns:xsi': text_fix(data.get('xmlns:xsi')),
                }

        def process_omisos(data):
            if not data: return None
            return {
                'Cabecera': process_cabecera(data.get('Cabecera')),
                'Detalle': process_detalle(data.get('Detalle')),
            }

            def process_cabecera(data):
                if not data: return None
                return {
                    'xsi:nil': text_fix(data.get('xsi:nil')),
                    'xmlns:xsi': text_fix(data.get('xmlns:xsi')),
                }

            def process_detalle(data):
                if not data: return None
                return {
                    'xsi:nil': text_fix(data.get('xsi:nil')),
                    'xmlns:xsi': text_fix(data.get('xmlns:xsi')),
                }

        def process_redam(data):
            if not data: return None
            return {
                'Cabecera': process_cabecera(data.get('Cabecera')),
                'Detalle': process_detalle(data.get('Detalle')),
            }

            def process_cabecera(data):
                if not data: return None
                return {
                    'xsi:nil': text_fix(data.get('xsi:nil')),
                    'xmlns:xsi': text_fix(data.get('xmlns:xsi')),
                }

            def process_detalle(data):
                if not data: return None
                return {
                    'xsi:nil': text_fix(data.get('xsi:nil')),
                    'xmlns:xsi': text_fix(data.get('xmlns:xsi')),
                }

    try:
        final_out = {
            'otras_deudas_impagas:_resumen': {
                'Codigo': modulo[0].get('Codigo'),
                'Nombre': modulo[0].get('Nombre'),
                'Data': data.get('flag') if data else None,
                'flag': text_fix(data.get('flag')),
                'OtrasDeudasImpagas': process_otrasdeudasimpagas(data.get('OtrasDeudasImpagas')),
            }
        }
    except Exception as e:
        traceback.print_exc()
        final_out = {
            'otras_deudas_impagas:_resumen': {
                'Codigo': codigo,
                'Nombre': nombre,
                'Data': False
            }
        }
    return final_out

if __name__ == '__main__':
    with open('response-dss1.json', 'r', encoding='UTF-8') as file:
        request = json.load(file)
        out = json.dumps(main(request), indent=4)
    with open('respond.json', 'w') as file:
        file.write(out)
