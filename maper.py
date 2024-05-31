import json
import os

# Función para limpiar textos
text_fix = lambda x: x.strip() if isinstance(x, str) else x

def generate_script_for_module(module, tipo):
    nombre_modulo = module['Nombre'].replace(' ', '_').lower()
    codigo_modulo = module['Codigo']
    nombre_archivo = f"{tipo}_modulo_{codigo_modulo}_{nombre_modulo}.py"

    with open(nombre_archivo, 'w') as f:
        f.write("import os\n")
        f.write("import sys\n")
        f.write("import traceback\n")
        f.write("import json\n")
        f.write("from pe_utils import text_fix\n\n")

        f.write("def main(payload):\n")
        f.write("    try:\n")
        f.write(f"        nombre  = '{module['Nombre']}'\n")
        f.write(f"        target  = '{nombre_modulo}'\n")
        f.write(f"        codigo  = {codigo_modulo}\n")
        f.write("        modulos = payload.get('dataSourceResponse').get('GetReporteOnlineResponse').get('ReporteCrediticio').get('Modulos').get('Modulo')\n")
        f.write(f"        modulo  = [modulo for modulo in modulos if modulo.get('Data') is not None and nombre in modulo.get('Nombre')]\n")
        f.write("        if len(modulo) > 1:\n")
        f.write("            modulo_filtrado = [modulo_filtrado for modulo_filtrado in modulo if modulo_filtrado.get('Data').get(target)]\n")
        f.write("            modulo = modulo_filtrado if len(modulo_filtrado) == 1 else modulo\n")
        f.write("        data = modulo[0].get('Data')\n")
        f.write("    except Exception as e:\n")
        f.write("        traceback.print_exc()\n")
        f.write("        data = None\n\n")

        def write_function_definitions(key, value, indent_level=1):
            indent = "    " * indent_level
            if isinstance(value, dict):
                f.write(f"{indent}def process_{key.lower()}(data):\n")
                f.write(f"{indent}    if not data: return None\n")
                f.write(f"{indent}    return {{\n")
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, dict):
                        f.write(f"{indent}        '{sub_key}': process_{sub_key.lower()}(data.get('{sub_key}')),\n")
                    elif isinstance(sub_value, list):
                        f.write(f"{indent}        '{sub_key}': [process_item(item) for item in data.get('{sub_key}', [])],\n")
                    else:
                        f.write(f"{indent}        '{sub_key}': text_fix(data.get('{sub_key}')),\n")
                f.write(f"{indent}    }}\n\n")
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, dict):
                        write_function_definitions(sub_key, sub_value, indent_level=1)
            elif isinstance(value, list):
                f.write(f"{indent}def process_{key.lower()}(data):\n")
                f.write(f"{indent}    if not data: return None\n")
                f.write(f"{indent}    return [process_item(item) for item in data]\n\n")

        def process_item(data):
            if not data: return None
            return {key: text_fix(value) for key, value in data.items()}

        if 'Data' in module:
            for key, value in module['Data'].items():
                write_function_definitions(key, value)

        f.write("    try:\n")
        f.write("        final_out = {\n")
        f.write(f"            '{nombre_modulo}': {{\n")
        f.write("                'Codigo': modulo[0].get('Codigo'),\n")
        f.write("                'Nombre': modulo[0].get('Nombre'),\n")
        f.write("                'Data': data.get('flag') if data else None,\n")
        if 'Data' in module:
            for key, value in module['Data'].items():
                if isinstance(value, dict):
                    f.write(f"                '{key}': process_{key.lower()}(data.get('{key}')),\n")
                else:
                    f.write(f"                '{key}': text_fix(data.get('{key}')),\n")
        f.write("            }\n")
        f.write("        }\n")
        f.write("    except Exception as e:\n")
        f.write("        traceback.print_exc()\n")
        f.write("        final_out = {\n")
        f.write(f"            '{nombre_modulo}': {{\n")
        f.write("                'Codigo': codigo,\n")
        f.write("                'Nombre': nombre,\n")
        f.write("                'Data': False\n")
        f.write("            }\n")
        f.write("        }\n")
        f.write("    return final_out\n\n")

        f.write("if __name__ == '__main__':\n")
        f.write("    with open('response-dss1.json', 'r', encoding='UTF-8') as file:\n")
        f.write("        request = json.load(file)\n")
        f.write("        out = json.dumps(main(request), indent=4)\n")
        f.write("    with open('respond.json', 'w') as file:\n")
        f.write("        file.write(out)\n")

def main():
    with open('persona.json', 'r') as f:
        json_perfecto_persona = json.load(f).get('dataSourceResponse', {}).get('GetReporteOnlineResponse', {})
    for modulo in json_perfecto_persona.get('ReporteCrediticio', {}).get('Modulos', {}).get('Modulo', []):
        generate_script_for_module(modulo, 'persona')
    
    with open('empresa.json', 'r') as f:
        json_perfecto_empresa = json.load(f).get('dataSourceResponse', {}).get('GetReporteOnlineResponse', {})
    for modulo in json_perfecto_empresa.get('ReporteCrediticio', {}).get('Modulos', {}).get('Modulo', []):
        generate_script_for_module(modulo, 'empresa')

if __name__ == '__main__':
    main()
