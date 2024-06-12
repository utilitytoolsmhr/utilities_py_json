import os
import json
from collections import defaultdict

def load_json_files(directory):
    json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
    data_list = []
    for file in json_files:
        with open(os.path.join(directory, file), 'r', encoding='utf-8') as f:
            data = json.load(f)
            data_list.append(data)
    return data_list

def clean_data(data):
    if isinstance(data, dict):
        clean_dict = {}
        for k, v in data.items():
            if isinstance(v, dict) and ("xsi:nil" in v and v["xsi:nil"]):
                clean_dict[k] = "sin data"
            else:
                clean_dict[k] = clean_data(v)
        return clean_dict
    elif isinstance(data, list):
        return [clean_data(item) for item in data[:2]]  # Limit lists to 2 items
    else:
        return data

def merge_dicts(dict_list, max_items=2):
    merged_dict = defaultdict(lambda: defaultdict(list))
    for d in dict_list:
        for key, value in d.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, list):
                        merged_dict[key][sub_key].extend(sub_value[:max_items])
                        merged_dict[key][sub_key] = merged_dict[key][sub_key][:max_items]
                    else:
                        merged_dict[key][sub_key] = sub_value
            else:
                merged_dict[key] = value
    return {k: dict(v) for k, v in merged_dict.items()}

def get_most_complete_module(modules):
    max_keys = 0
    most_complete_module = {}
    for module in modules:
        cleaned_module = clean_data(module)
        num_keys = len(json.dumps(cleaned_module))
        if num_keys > max_keys:
            max_keys = num_keys
            most_complete_module = cleaned_module
    # Limitar a los primeros 2 elementos si es una lista
    for key, value in most_complete_module.items():
        if isinstance(value, list):
            most_complete_module[key] = value[:2]
    return most_complete_module

def process_json_data(data_list):
    module_dict = defaultdict(lambda: defaultdict(list))
    for data in data_list:
        if 'dataSourceResponse' in data:
            response = data['dataSourceResponse']
            if 'GetReporteOnlineResponse' in response:
                report = response['GetReporteOnlineResponse']
                if 'ReporteCrediticio' in report:
                    credit_report = report['ReporteCrediticio']
                    if 'Modulos' in credit_report:
                        modules = credit_report['Modulos']
                        for module in modules['Modulo']:
                            module_name = module['Nombre']
                            module_code = module['Codigo']
                            module_dict[module_name][module_code].append(module)
                            print(f"Processed module: {module_name} with code: {module_code}")

    most_complete_modules = {}
    for module_name, code_modules in module_dict.items():
        for code, modules in code_modules.items():
            most_complete_module_data = get_most_complete_module([module['Data'] for module in modules])
            for module in modules:
                if module['Data'] == most_complete_module_data:
                    module_key = f"{module_name}_{code}"
                    most_complete_modules[module_key] = module
                    print(f"Selected most complete module: {module_key}")
                    break
            if f"{module_name}_{code}" not in most_complete_modules:
                # Add the least complete module if none is selected
                least_complete_module_data = clean_data(modules[0]['Data'])
                module_key = f"{module_name}_{code}"
                most_complete_modules[module_key] = modules[0]
                most_complete_modules[module_key]['Data'] = least_complete_module_data
                print(f"Added least complete module: {module_key}")

    return most_complete_modules

def check_structure_difference(persona_modules, empresa_modules):
    for key in persona_modules.keys() | empresa_modules.keys():
        persona_module = persona_modules.get(key)
        empresa_module = empresa_modules.get(key)
        if persona_module and empresa_module and persona_module != empresa_module:
            print(f"Inconsistency found in module {key}:")
            print(f"Persona module: {json.dumps(persona_module, indent=4)}")
            print(f"Empresa module: {json.dumps(empresa_module, indent=4)}")

def main():
    persona_dir = 'Persona'
    empresa_dir = 'Empresa'
    
    persona_data_list = load_json_files(persona_dir)
    empresa_data_list = load_json_files(empresa_dir)

    persona_modules = process_json_data(persona_data_list)
    empresa_modules = process_json_data(empresa_data_list)

    # Verificar diferencias de estructura
    check_structure_difference(persona_modules, empresa_modules)

    # Combinar módulos de persona y empresa
    combined_modules = {**persona_modules, **empresa_modules}

    # Guardar todos los módulos en un único archivo JSON
    with open('Modulos_completos.json', 'w', encoding='utf-8') as f:
        json.dump(combined_modules, f, ensure_ascii=False, indent=4)
        print(f'Saved combined modules to Modulos_completos.json')

if __name__ == '__main__':
    main()
