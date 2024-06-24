import json
import os
import traceback
from datetime import datetime

def generate_dynamic_functions(fields, parent_key=""):
    functions = ""
    if isinstance(fields, dict):
        for key, value in fields.items():
            current_key = f"{parent_key}_{key}" if parent_key else key
            if isinstance(value, dict):
                functions += generate_dynamic_functions(value, current_key)
            elif isinstance(value, list) and isinstance(value[0], dict):
                function_name = f"process_{current_key}"
                functions += f"\n    def {function_name}(data):\n"
                functions += f"        return [\n"
                for sub_key in value[0].keys():
                    functions += f"            {{'{sub_key}': text_fix(ob.get('{sub_key}'))}} for ob in data\n"
                functions += f"        ]\n"
            else:
                function_name = f"process_{current_key}"
                functions += f"\n    def {function_name}(data):\n"
                functions += f"        return text_fix(data.get('{key}'))\n"
    return functions

def build_field_mappings(fields):
    mappings = {}
    if isinstance(fields, dict):
        for key, value in fields.items():
            if isinstance(value, dict):
                mappings[key] = build_field_mappings(value)
            elif isinstance(value, list) and isinstance(value[0], dict):
                mappings[key] = [build_field_mappings(value[0])]
            else:
                mappings[key] = ""
    return mappings

def generate_script(module, codigo_persona, codigo_empresa, target_name, fields, tipo_documento):
    dynamic_functions = generate_dynamic_functions(fields)
    field_mappings = build_field_mappings(fields)

    # Template del script con las variables correctamente referenciadas
    script_template = f"""
# ==================================
# Modulo: {module}
# Autor: Generado automáticamente
# Fecha: {datetime.now().strftime('%d-%m-%Y')}
# ==================================

import os
import sys
import traceback
from pe_utils import text_fix, get_value, xsi_to_null

def main(payload):

    #################################################
    ################## Data IN ######################
    #################################################

    try:
        primaryConsumer = payload.get('applicants')[0]
    except:
        primaryConsumer = payload.get('applicants').get('primaryConsumer')

    try:
        # Captura respuesta API-DSS
        payload = primaryConsumer.get('equifax-pe-middleware')
        
        # Reemplaza por null tag[xsi] presentes en payload
        xsi_to_null(payload)

        # Seleccionamos el modulo target
        nombre  = '{module}'
        target  = '{target_name}'
        codigo  = {codigo_persona if tipo_documento == 1 else codigo_empresa}
        modulos = payload.get('dataSourceResponse').get('GetReporteOnlineResponse').get('ReporteCrediticio').get('Modulos').get('Modulo')
        modulo  = [modulo for modulo in modulos if modulo.get('Data') is not None and nombre in modulo.get('Nombre')]  

        # Filtra por target si existen múltiples módulos con el mismo nombre
        if len(modulo) > 1: 
            modulo_filtrado = [modulo_filtrado for modulo_filtrado in modulo if modulo_filtrado.get('Data').get(target)]
            modulo = modulo_filtrado if len(modulo_filtrado) == 1 else modulo

        # Data del modulo
        nodo = modulo[0].get('Data').get(target)
    except Exception as e:
        print(f"Error al procesar los datos de entrada: {e}")
        traceback.print_exc()

    #################################################
    ################### Functions ###################
    #################################################

    {dynamic_functions}

    #################################################
    ################# Data Processing ###############
    #################################################

    def process_data(data, field_mappings):
        result = {{}}
        for key, value in field_mappings.items():
            if isinstance(value, dict):
                result[key] = process_data(data.get(key, {{}}), value)
            elif isinstance(value, list):
                result[key] = [process_data(item, value[0]) for item in data.get(key, [])]
            else:
                function_name = f"process_{target_name.lower()}_{key}"
                if function_name in globals():
                    result[key] = globals()[function_name](data)
                else:
                    result[key] = text_fix(data.get(key))
        return result

    #################################################
    ################## Set Output ###################
    #################################################

    try:
        final_out = {{
            "Codigo": modulo[0].get('Codigo'),
            "Nombre": modulo[0].get('Nombre'),
            "Data": {{
                "flag": modulo[0].get('Data').get('flag'),
                "{target_name}": process_data(nodo, {json.dumps(field_mappings, indent=4)})
            }}
        }}
    except Exception as e:
        print(f"Error al generar la salida final: {e}")
        traceback.print_exc()
        final_out = {{
            "Codigo": codigo, 
            "Nombre": nombre, 
            "Data": {{
                "flag": False
            }}
        }}
    return final_out
    """

    filename = f"pe_modulo_{target_name.lower()}.py"
    os.makedirs("scripts_final", exist_ok=True)
    filepath = os.path.join("scripts_final", filename)
    
    # Check if the file already exists and add a suffix if it does
    counter = 2
    while os.path.exists(filepath):
        base, ext = os.path.splitext(filepath)
        filepath = f"{base}_{counter}{ext}"
        counter += 1

    with open(filepath, 'w') as f:
        f.write(script_template)
    print(f"Script {os.path.basename(filepath)} generado exitosamente.")

def get_modules_info(json_data, module_name):
    try:
        module = json_data[module_name]
        codigo_persona = module['Codigo']
        codigo_empresa = module['Codigo']
        target_name = next((key for key in module.get('Data', {}).keys() if key != 'flag'), None)
        fields = module.get('Data', {}).get(target_name, {})
        return codigo_persona, codigo_empresa, target_name, fields
    except KeyError as e:
        print(f"Error: No se encontró el módulo {module_name} en la estructura.")
        return None, None, None, None

def generate_all_scripts():
    with open("modulos_completos.json", 'r') as f:
        complete_data = json.load(f)

    for module_name in complete_data.keys():
        if '_p' in module_name:
            tipo_documento = 1
        elif '_e' in module_name:
            tipo_documento = 2
        else:
            continue

        base_module_name = module_name[:-2]
        codigo_persona, codigo_empresa, target_name, fields = get_modules_info(complete_data, module_name)
        if target_name:
            print(f"Generando script para el módulo: {base_module_name}")
            generate_script(base_module_name, codigo_persona, codigo_empresa, target_name, fields, tipo_documento)

if __name__ == "__main__":
    generate_all_scripts()
