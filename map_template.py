import json
import os
import sys
import traceback
from datetime import datetime

def generate_script_from_json(json_data, module_name, target_name, codigo_persona, codigo_empresa=None):
    script = f"""
# ==================================
# Modulo: {module_name.upper()}
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

    tipoPersona = primaryConsumer.get('personalInformation').get('tipoPersona')

    try:
        # Captura respuesta API-DSS
        payload = primaryConsumer.get('equifax-pe-middleware')
        
        # Reemplaza por null tag[xsi] presentes en payload
        xsi_to_null(payload)

        # Seleccionamos el modulo target
        nombre  = '{module_name}'
        target  = '{target_name}'
        codigo  = codigo_persona if tipoPersona == 1 else {codigo_empresa if codigo_empresa is not None else codigo_persona}
        modulos = payload.get('dataSourceResponse').get('GetReporteOnlineResponse').get('ReporteCrediticio').get('Modulos').get('Modulo')
        modulo  = [modulo for modulo in modulos if modulo.get('Data') is not None and nombre in modulo.get('Nombre')]  

        # Filtra por target si existen múltiples módulos con el mismo nombre
        if len(modulo) > 1: 
            modulo_filtrado = [modulo_filtrado for modulo_filtrado in modulo if modulo_filtrado.get('Data').get(target)]
            modulo = modulo_filtrado if len(modulo_filtrado) == 1 else modulo

        # Data del modulo
        nodo = modulo[0].get('Data').get(target)
    except:
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
                    script += f"            '{k}': data.get('{k}', ''),\n"
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

    try:
        final_out = {{
                "{target_name}": {{
                    "Codigo": modulo[0].get('Codigo'),
                    "Nombre": modulo[0].get('Nombre'),
                    "Data": modulo[0].get('Data').get('flag'),
                    "Details": result
                }}
            }}
    except:
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

def generate_scripts_for_modules(persona_data, empresa_data):
    directory = 'scripts_final'
    os.makedirs(directory, exist_ok=True)

    processed_targets = {}

    # Helper function to convert camelCase to snake_case
    def camel_to_snake(name):
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    # Process both persona and empresa data
    for data, entity in [(persona_data, 'persona'), (empresa_data, 'empresa')]:
        for module_name, module_data in data.items():
            if 'Data' in module_data and 'flag' in module_data['Data'] and module_data['Data']['flag']:
                for target_name, target_data in module_data['Data'].items():
                    if target_name != 'flag':
                        codigo = module_data['Codigo']
                        if target_name not in processed_targets:
                            processed_targets[target_name] = {'persona': None, 'empresa': None}
                        processed_targets[target_name][entity] = codigo

                        script = generate_script_from_json(target_data if isinstance(target_data, dict) else {},
                                                           module_name, target_name, 
                                                           processed_targets[target_name]['persona'], 
                                                           processed_targets[target_name]['empresa'])

                        prefix = 'empresa_' if processed_targets[target_name]['empresa'] is not None else ''
                        file_name = f'{directory}/pe_modulo_{prefix}{camel_to_snake(target_name)}.py'
                        with open(file_name, 'w') as f:
                            f.write(script)
                        print(f'Script generado para el módulo: {module_name}, target: {target_name} en {file_name}')

# Leer los JSONs de persona y empresa
with open('persona.json') as f:
    persona_data = json.load(f)

with open('empresa.json') as f:
    empresa_data = json.load(f)

# Generar scripts
generate_scripts_for_modules(persona_data, empresa_data)
