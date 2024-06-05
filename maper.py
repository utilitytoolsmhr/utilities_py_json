import json
import os
import re
import traceback

# Función para limpiar textos
text_fix = lambda x: x.strip() if isinstance(x, str) else x

# Directorios
persona_dir = 'persona'
empresa_dir = 'empresa'

def sanitize_filename(filename):
    # Reemplaza caracteres no alfanuméricos por guiones bajos
    return re.sub(r'[^a-zA-Z0-9_]', '_', filename)

def generate_script_for_module(module, tipo_persona, tipo_empresa, nombre_modulo, codigo_persona, codigo_empresa, valid_data_persona, valid_data_empresa):
    nombre_archivo = f"modulo_{sanitize_filename(nombre_modulo)}.py"

    with open(nombre_archivo, 'w') as f:
        f.write("import os\n")
        f.write("import sys\n")
        f.write("import traceback\n")
        f.write("import json\n")
        f.write("from pe_utils import text_fix\n\n")

        f.write("def main(payload):\n")
        f.write("    try:\n")
        f.write("        tipo_persona = payload.get('applicants').get('primaryConsumer').get('personalInformation').get('tipoPersona')\n")
        f.write(f"        nombre  = '{nombre_modulo}'\n")
        f.write(f"        codigo_persona  = {codigo_persona}\n")
        f.write(f"        codigo_empresa  = {codigo_empresa}\n")
        f.write("        modulos = payload.get('applicants').get('primaryConsumer').get('equifax-pe-middleware').get('Modulos')\n")
        f.write(f"        modulo  = [modulo for modulo in modulos if modulo.get('Nombre') == nombre]\n")
        f.write("        if not modulo:\n")
        f.write("            return None\n")
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
                    if sub_key in ('xsi:nil', 'xmlns:xsi'):
                        f.write(f"{indent}        '{sub_key}': None,\n")
                    elif isinstance(sub_value, dict):
                        f.write(f"{indent}        '{sub_key}': process_{sub_key.lower()}(data.get('{sub_key}')),\n")
                    elif isinstance(sub_value, list):
                        f.write(f"{indent}        '{sub_key}': [process_item(item) for item in data.get('{sub_key}', [])],\n")
                    else:
                        f.write(f"{indent}        '{sub_key}': text_fix(data.get('{sub_key}')),\n")
                f.write(f"{indent}    }}\n\n")
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, dict) and sub_key not in ('xsi:nil', 'xmlns:xsi'):
                        write_function_definitions(sub_key, sub_value, indent_level=1)
            elif isinstance(value, list):
                f.write(f"{indent}def process_{key.lower()}(data):\n")
                f.write(f"{indent}    if not data: return None\n")
                f.write(f"{indent}    return [process_item(item) for item in data]\n\n")

        def process_item(data):
            if not data: return None
            return {key: text_fix(value) for key, value in data.items()}

        valid_data = valid_data_persona if tipo_persona == 1 else valid_data_empresa
        if valid_data:
            for key, value in valid_data.items():
                write_function_definitions(key, value)

        f.write("    try:\n")
        f.write("        final_out = {\n")
        f.write(f"            '{nombre_modulo}': {{\n")
        f.write("                'Codigo': codigo_persona if tipo_persona == 1 else codigo_empresa,\n")
        f.write("                'Nombre': nombre,\n")
        f.write("                'Data': data.get('flag') if data else None,\n")
        if valid_data:
            for key, value in valid_data.items():
                if isinstance(value, dict):
                    f.write(f"                '{key}': process_{key.lower()}(data.get('{key}')),\n")
                elif key not in ('xsi:nil', 'xmlns:xsi'):
                    f.write(f"                '{key}': text_fix(data.get('{key}')),\n")
        f.write("            }\n")
        f.write("        }\n")
        f.write("    except Exception as e:\n")
        f.write("        traceback.print_exc()\n")
        f.write("        final_out = {\n")
        f.write(f"            '{nombre_modulo}': {{\n")
        f.write("                'Codigo': codigo_persona if tipo_persona == 1 else codigo_empresa,\n")
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

def find_valid_module_data(modules, modulo_nombre, modulo_codigo):
    for module in modules:
        if module.get('Nombre') == modulo_nombre and module.get('Codigo') == modulo_codigo:
            data = module.get('Data')
            if data:
                valid = True
                for key, value in data.items():
                    if key in ('xsi:nil', 'xmlns:xsi'):
                        valid = False
                        break
                if valid:
                    return data
    return None

def process_directory(directory, tipo):
    module_info = {}
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as f:
                try:
                    content = json.load(f)
                    modules = content.get('dataSourceResponse', {}).get('GetReporteOnlineResponse', {}).get('ReporteCrediticio', {}).get('Modulos', {}).get('Modulo', [])
                    for module in modules:
                        module_nombre = module.get('Nombre')
                        module_codigo = module.get('Codigo')
                        if module_nombre not in module_info:
                            module_info[module_nombre] = {}
                        if tipo == 'persona':
                            module_info[module_nombre]['codigo_persona'] = module_codigo
                            module_info[module_nombre]['data_persona'] = find_valid_module_data(modules, module_nombre, module_codigo)
                        elif tipo == 'empresa':
                            module_info[module_nombre]['codigo_empresa'] = module_codigo
                            module_info[module_nombre]['data_empresa'] = find_valid_module_data(modules, module_nombre, module_codigo)
                except Exception as e:
                    traceback.print_exc()
    return module_info

def main():
    persona_info = process_directory(persona_dir, 'persona')
    empresa_info = process_directory(empresa_dir, 'empresa')

    for nombre_modulo, info in persona_info.items():
        codigo_persona = info.get('codigo_persona')
        codigo_empresa = empresa_info.get(nombre_modulo, {}).get('codigo_empresa', None)
        data_persona = info.get('data_persona')
        data_empresa = empresa_info.get(nombre_modulo, {}).get('data_empresa', None)
        generate_script_for_module(
            module={
                'Nombre': nombre_modulo,
                'Codigo': codigo_persona
            },
            tipo_persona=1,
            tipo_empresa=2,
            nombre_modulo=nombre_modulo,
            codigo_persona=codigo_persona,
            codigo_empresa=codigo_empresa,
            valid_data_persona=data_persona,
            valid_data_empresa=data_empresa
        )

if __name__ == '__main__':
    main()
