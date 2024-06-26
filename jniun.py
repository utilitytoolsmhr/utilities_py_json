import json
import os
import sys
import traceback
from datetime import datetime

def generate_script_from_json(json_data, module_name, target_name, codigo_persona, codigo_empresa):
    script = f"""
# ==================================
# Modulo: {module_name.upper()}
# Autor: José Reyes         
# Correo: jose.reyes3@equifax.com
# Fecha: {datetime.now().strftime('%d-%m-%Y')}
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

    # Código modulo -> Persona Natural = 1 / Persona Jurídica = 2
    codigo_modulo = {codigo_persona} if tipoPersona == 1 else {codigo_empresa}

    try:
        # Captura respuesta API-DSS
        payload = primaryConsumer.get('equifax-pe-middleware')

        # Reemplaza por null tag[xsi] presentes en payload
        xsi_to_null(payload)

        # Seleccionamos el modulo target
        nombre = '{module_name}'
        target = '{target_name}'
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
        print(f"Error procesando los datos de entrada: {{e}}")
        traceback.print_exc()

    #################################################
    ################### Functions ###################
    #################################################

"""
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            if isinstance(value, dict):
                script += f"""
    def process_{target_name.lower()}_{key}(data):
        return {{
"""
                for k, v in value.items():
                    script += f"            '{k}': text_fix(data.get('{k}', '')),\n"
                script += f"        }}\n"

    script += """
    #################################################
    ################# Data Processing ###############
    #################################################

    result = {}

"""
    if isinstance(json_data, dict):
        for key in json_data.keys():
            if isinstance(json_data[key], dict):
                script += f"    result['{key}'] = process_{target_name.lower()}_{key}(nodo.get('{key}', {{}}))\n"

    script += f"""
    #################################################
    ################## Set Output ###################
    #################################################

    if not formato_salida:
        try:
            final_out = {{
                "Codigo": modulo[0].get('Codigo'),
                "Nombre": modulo[0].get('Nombre'),
                "Data": {{
                    "flag": modulo[0].get('Data').get('flag'),
                    "{target_name}": result
                }}
            }}
        except Exception as e:
            print(f"Error generando la salida final (formato_salida=False): {{e}}")
            traceback.print_exc()
            final_out = {{
                "Codigo": codigo,
                "Nombre": nombre,
                "Data": {{
                    "flag": False,
                    "{target_name}": {{}}
                }}
            }}
    else:
        try:
            final_out = {{
                "{target_name}": {{
                    "Codigo": modulo[0].get('Codigo'),
                    "Nombre": modulo[0].get('Nombre'),
                    "Data": modulo[0].get('Data').get('flag'),
                    "{target_name}": result
                }}
            }}
        except Exception as e:
            print(f"Error generando la salida final (formato_salida=True): {{e}}")
            traceback.print_exc()
            final_out = {{
                "{target_name}": {{
                    "Codigo": codigo,
                    "Nombre": nombre,
                    "Data": False
                }}
            }}
    return final_out
"""

    return script

def generate_scripts_for_modules(modules_data):
    directory = 'scripts_final'
    os.makedirs(directory, exist_ok=True)

    def camel_to_snake(name):
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    for module_name, module_data in modules_data.items():
        print(f"Procesando módulo: {module_name}")
        base_module_name = module_name.rsplit('_', 1)[0]
        persona_key = f"{base_module_name}_p"
        empresa_key = f"{base_module_name}_e"
        
        print(f"persona_key: {persona_key}, empresa_key: {empresa_key}")
        print(f"persona_data: {modules_data.get(persona_key)}, empresa_data: {modules_data.get(empresa_key)}")

        codigo_persona = modules_data.get(persona_key, {}).get('Codigo', 222)
        codigo_empresa = modules_data.get(empresa_key, {}).get('Codigo', 333)

        for target_name, target_data in module_data.get('Data', {}).items():
            if target_name != 'flag':
                script = generate_script_from_json(target_data if isinstance(target_data, dict) else {},
                                                   base_module_name, target_name, 
                                                   codigo_persona, 
                                                   codigo_empresa)

                file_name = f'{directory}/pe_modulo_{camel_to_snake(target_name)}.py'
                with open(file_name, 'w') as f:
                    f.write(script)
                print(f'Script generado para el módulo: {base_module_name}, target: {target_name} en {file_name}')

def load_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='cp1252') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error al cargar el archivo JSON: {e}")
        return None

# Leer el JSON de módulos completos
modules_data = load_json_file('modulos_completos.json')

# Verificar si se cargaron los datos correctamente antes de proceder
if modules_data:
    print("Datos del archivo JSON cargados correctamente.")
    # Generar scripts
    generate_scripts_for_modules(modules_data)
else:
    print("No se pudieron cargar los datos del archivo JSON.")
