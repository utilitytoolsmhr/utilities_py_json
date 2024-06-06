import os
import sys
import traceback
import json
from jinja2 import Template

# Importar funciones desde pe_utils.py
from pe_utils import text_fix, float_fix, int_fix

# Plantilla para los scripts Python
template_script = """
import os
import sys
import traceback
import json
from pe_utils import text_fix, float_fix, int_fix

def main(payload):

    #################################################
    ################## Data IN ######################
    #################################################

    try:
        # Determinar si es persona o empresa
        tipo_documento = payload.get('dataSourceResponse').get('GetReporteOnlineResponse').get('ReporteCrediticio').get('DatosPrincipales').get('TipoDocumento')
        codigo = '{{ codigo_persona }}' if tipo_documento == 'DNI' else '{{ codigo_empresa }}'
        
        # Seleccionamos el módulo target
        nombre  = '{{ module_name }}'
        target  = '{{ target_name }}'
        modulos = payload.get('dataSourceResponse').get('GetReporteOnlineResponse').get('ReporteCrediticio').get('Modulos').get('Modulo')
        modulo  = [modulo for modulo in modulos if modulo.get('Data') is not None and nombre in modulo.get('Nombre')]
        
        # Filtra por target si existen múltiples módulos con el mismo nombre
        if len(modulo) > 1: 
            modulo_filtrado = [modulo_filtrado for modulo_filtrado in modulo if modulo_filtrado.get('Data').get(target)]
            modulo = modulo_filtrado if len(modulo_filtrado) == 1 else modulo

        # Data del módulo
        nodo = modulo[0].get('Data').get(target)
    except:
        traceback.print_exc()

    #################################################
    ################### Functions ###################
    #################################################

    def process_data(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    data[key] = text_fix(value)
                elif isinstance(value, float):
                    data[key] = float_fix(value)
                elif isinstance(value, int):
                    data[key] = int_fix(value)
                elif isinstance(value, list) or isinstance(value, dict):
                    process_data(value)
        elif isinstance(data, list):
            for item in data:
                process_data(item)
        return data

    #################################################
    ################# Data Processing ###############
    #################################################

    try:
        final_out = {
                "{{ target_name }}": {
                    "Codigo": codigo,
                    "Nombre": modulo[0].get('Nombre'),
                    "Data": modulo[0].get('Data').get('flag'),
                    "{{ target_key }}": process_data(nodo) if nodo else None
                }
            }
    except:
        final_out = {
                "{{ target_name }}": {
                    "Codigo": codigo,
                    "Nombre": nombre,
                    "Data": False
                }
            }
    return final_out

#################################################
################## TEST #########################
#################################################
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python {{ script_name }}.py <archivo_json>")
    else:
        archivo_json = sys.argv[1]
        with open(archivo_json, 'r', encoding="UTF-8") as file:
            request = json.load(file)
            out = json.dumps(main(request), indent=4)
            print(out)
            with open('respond.json', 'w', encoding="UTF-8") as outfile:
                outfile.write(out)
"""

def generate_script(module_name, target_name, target_key, script_name, codigo_persona, codigo_empresa):
    template = Template(template_script)
    script_content = template.render(
        module_name=module_name, 
        target_name=target_name, 
        target_key=target_key, 
        script_name=script_name,
        codigo_persona=codigo_persona,
        codigo_empresa=codigo_empresa
    )
    
    script_path = f"pe_modulo_{script_name}.py"
    with open(script_path, 'w', encoding="UTF-8") as file:
        file.write(script_content)
    
    print(f"Script {script_path} generado exitosamente.")

# Módulos a generar
modules = [
    {"module_name": "RESUMEN FLAG", "target_name": "ResumenFlags", "target_key": "Flags", "script_name": "resumen_flags", "codigo_persona": 865, "codigo_empresa": 868},
    {"module_name": "SCORE PREDICTIVO CON VARIABLES", "target_name": "ResumenScoreRP3", "target_key": "ScorePredictivo", "script_name": "resumen_score", "codigo_persona": 822, "codigo_empresa": 822},
    {"module_name": "REPRESENTANTES LEGALES", "target_name": "RepresentantesLegales", "target_key": "Legales", "script_name": "representantes_legales", "codigo_persona": 830, "codigo_empresa": 831},
    {"module_name": "REGISTRO CREDITICIO CONSOLIDADO (RCC)", "target_name": "RegistroCrediticioConsolidado", "target_key": "Crediticio", "script_name": "registro_crediticio_consolidado", "codigo_persona": 865, "codigo_empresa": 868},
    {"module_name": "SISTEMA FINANCIERO REGULADO (SBS) Y NO REGULADO (MICROFINANZAS)", "target_name": "SistemaFinanciero", "target_key": "Financiero", "script_name": "sistema_financiero", "codigo_persona": 865, "codigo_empresa": 868}
]

# Generar los scripts para cada módulo
for module in modules:
    generate_script(**module)
