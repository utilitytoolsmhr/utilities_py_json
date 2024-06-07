import os
import sys
import traceback
import json
from jinja2 import Template
from pe_utils import text_fix, float_fix, int_fix
import re

# Crear la carpeta /scripts si no existe
output_dir = 'scripts'
os.makedirs(output_dir, exist_ok=True)

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
        
        # Aplicar funciones de pe_utils.py
        for key, value in nodo.items():
            if isinstance(value, str):
                nodo[key] = text_fix(value)
            elif isinstance(value, float):
                nodo[key] = float_fix(value)
            elif isinstance(value, int):
                nodo[key] = int_fix(value)

    except:
        traceback.print_exc()

    #################################################
    ################# Data Processing ###############
    #################################################

    try:
        final_out = {
                "{{ target_name }}": {
                    "Codigo": codigo,
                    "Nombre": modulo[0].get('Nombre'),
                    "Data": modulo[0].get('Data').get('flag'),
                    "{{ target_key }}": nodo if nodo else None
                }
            }
    except:
        final_out = {
                "{{ target_name }}": {
                    "Codigo": None,
                    "Nombre": nombre,
                    "Data": False
                }
            }
    return final_out

#################################################
################## TEST #########################
#################################################
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

def read_json(file_path):
    with open(file_path, 'r', encoding="UTF-8") as file:
        data = json.load(file)
    return data

def to_snake_case(name):
    return re.sub(r'\s+', '_', re.sub(r'([a-z])([A-Z])', r'\1_\2', name)).lower()

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
    
    script_path = os.path.join(output_dir, f"pe_modulo_{script_name}.py")
    with open(script_path, 'w', encoding="UTF-8") as file:
        file.write(script_content)
    
    print(f"Script {script_path} generado exitosamente.")

def get_modules_info(json_data, module_name):
    modulos = json_data.get('dataSourceResponse').get('GetReporteOnlineResponse').get('ReporteCrediticio').get('Modulos').get('Modulo')
    print(f"Buscando módulo: {module_name}")
    for modulo in modulos:
        print(f"Módulo encontrado: {modulo.get('Nombre')}")
        if modulo.get('Nombre') == module_name:
            codigo_persona = modulo.get('Codigo')
            target_name = next((key for key in modulo.get('Data').keys() if key != 'flag'), None)  # Ignorar 'flag'
            return codigo_persona, target_name
    return None, None

# Archivos JSON de entrada desde la ruta de ejecución
persona_json = read_json('persona.json')
empresa_json = read_json('empresa.json')

# Módulos a generar con nombres exactos ajustados
modules = [
    {"module_name": "Resumen Flag", "script_name": "resumen_flags"},
    {"module_name": "SCORE PREDICTIVO CON VARIABLES", "script_name": "score_predictivo_con_variables"},
    {"module_name": "REPRESENTANTES LEGALES", "script_name": "representantes_legales"},
    {"module_name": "Registro Crediticio Consolidado (Rcc)", "script_name": "registro_crediticio_consolidado_rcc"},
    {"module_name": "SISTEMA FINANCIERO REGULADO (SBS) Y NO REGULADO (MICROFINANZAS)", "script_name": "sistema_financiero_regulado_y_no_regulado"}
]

# Generar los scripts para cada módulo
for module in modules:
    codigo_persona, target_name = get_modules_info(persona_json, module["module_name"])
    if not target_name:
        print(f"Error: No se encontró el target para el módulo {module['module_name']} en persona.json")
        continue
    
    codigo_empresa, _ = get_modules_info(empresa_json, module["module_name"])
    if not target_name:
        print(f"Error: No se encontró el target para el módulo {module['module_name']} en empresa.json")
        continue

    target_key = to_snake_case(target_name)  # Convertir el nombre del target a snake_case
    script_name = to_snake_case(module["module_name"])  # Convertir el nombre del módulo a snake_case
    generate_script(module["module_name"], target_name, target_key, script_name, codigo_persona, codigo_empresa)
