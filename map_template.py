import os
import sys
import traceback
import json
from jinja2 import Template
from pe_utils import text_fix, get_value, xsi_to_null
import re

# Crear la carpeta /scripts si no existe
output_dir = 'scripts'
os.makedirs(output_dir, exist_ok=True)

# Plantilla para los scripts Python
template_script = """
# ==================================
# Modulo: {{ module_name }}
# Autor: José Reyes         
# Correo: jose.reyes3@equifax.com
# Fecha: 24-05-2023    
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

    #Mapeo respuesta DSS
    try:
        # Captura respuesta API-DSS
        payload = primaryConsumer.get('equifax-pe-middleware')

        # Reemplaza por null tag[xsi] presentes en payload
        xsi_to_null(payload)

        # Seleccionamos el modulo target
        nombre  = '{{ module_name }}'
        target  = '{{ target_name }}'
        codigo_persona = {{ codigo_persona }}
        codigo_empresa = {{ codigo_empresa }}
        tipo_documento = primaryConsumer.get('documentType')
        codigo = codigo_persona if tipo_documento == '1' else codigo_empresa
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

    def get_score(ob, key):
        score = ob.get('ScoreHistoricos', {}).get(key)
        if score is not None:
            return {
                "Periodo":  text_fix(score.get('Periodo')),
                "Riesgo":   text_fix(score.get('Riesgo'))
            }
        else:
            return {
                "Periodo":  None,
                "Riesgo":   None
            }

    def empresaRelacionada(data):
        return [
            {
                "TipoDocumento":            text_fix(ob.get('TipoDocumento')),
                "NumeroDocumento":          text_fix(ob.get('NumeroDocumento')),
                "Nombre":                   text_fix(ob.get('Nombre')),
                "Relacion":                 text_fix(ob.get('Relacion')),
                "ScoreHistoricos": {
                    "ScoreActual":          get_score(ob,'ScoreActual'),
                    "ScoreAnterior":        get_score(ob,'ScoreAnterior'),
                    "ScoreHace12Meses":     get_score(ob,'ScoreHace12Meses')
                }
            } for ob in data
        ]

    #################################################
    ################# Data Processing ###############
    #################################################

    # Implementar la lógica de procesamiento de datos aquí

    #################################################
    ################## Set Output ###################
    #################################################
        
    try:
        final_out = {
                "{{ target_name }}": {
                    "Codigo": codigo,
                    "Nombre": modulo[0].get('Nombre'),
                    "Data": modulo[0].get('Data').get('flag'),
                    "{{ target_key }}": get_value(objeto=nodo, lista='{{ target_key }}', func=empresaRelacionada)
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
"""

def read_json(file_path):
    with open(file_path, 'r', encoding="UTF-8") as file:
        data = json.load(file)
    return data

def to_snake_case(name):
    return re.sub(r'\s+', '_', re.sub(r'([a-z])([A-Z])', r'\1_\2', name)).lower()

def generate_script(module_name, target_name, target_key, script_name, codigo_persona, codigo_empresa, fields):
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

def get_modules_info(json_data):
    try:
        modulos = json_data.get('dataSourceResponse').get('GetReporteOnlineResponse').get('ReporteCrediticio').get('Modulos').get('Modulo')
    except AttributeError:
        print("Error: La estructura del JSON no es la esperada.")
        return []

    modules_info = []
    for modulo in modulos:
        nombre = modulo.get('Nombre')
        codigo = modulo.get('Codigo')
        target_name = next((key for key in modulo.get('Data').keys() if key != 'flag'), None)
        fields = modulo.get('Data').get(target_name)
        modules_info.append((nombre, codigo, target_name, fields))

    return modules_info

# Archivos JSON de entrada desde la ruta de ejecución
empresa_json = read_json('empresa.json')
persona_json = read_json('persona.json')

def interact():
    # Combinar módulos de ambos JSONs
    modules_info = get_modules_info(empresa_json) + get_modules_info(persona_json)

    for module_info in modules_info:
        module_name, codigo, target_name, fields = module_info
        if not target_name:
            print(f"Error: No se encontró el target para el módulo {module_name} en los JSONs.")
            continue

        target_key = to_snake_case(target_name)  # Convertir el nombre del target a snake_case
        script_name = to_snake_case(module_name)  # Convertir el nombre del módulo a snake_case

        # Mostrar información
        print(f"\nMódulo: {module_name}")
        print(f"Código: {codigo}")
        print(f"Campos encontrados: {target_name}")
        
        # Generar JSON de Salida con cabeceras
        output_json = {key: key for key in fields.keys()} if fields else {}
        print(f"JSON de salida (cabeceras): {json.dumps(output_json, indent=4)}")

        default_name = f"pe_modulo_{script_name}.py"
        generate = input(f"¿Deseas generar el script {default_name}? (s/n): ").strip().lower()
        if generate == 's':
            custom_name = input(f"Ingresa un nombre para el script (presiona enter para aceptar {default_name}): ").strip()
            script_name_to_use = custom_name if custom_name else script_name
            generate_script(module_name, target_name, target_key, script_name_to_use, codigo, codigo, fields)
        else:
            print(f"Script para el módulo {module_name} no fue generado.")

if __name__ == "__main__":
    interact()
