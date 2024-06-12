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
                clean_dict[k] = ""
            else:
                clean_dict[k] = clean_data(v)
        return clean_dict
    elif isinstance(data, list):
        return [clean_data(item) for item in data if not ("xsi:nil" in item and item["xsi:nil"])]
    else:
        return data

def get_most_complete_module(modules, max_items=2):
    max_keys = 0
    most_complete_module = {}
    for module in modules:
        cleaned_module = clean_data(module)
        num_keys = len(json.dumps(cleaned_module))
        if num_keys > max_keys:
            max_keys = num_keys
            most_complete_module = cleaned_module
    # Limitar a los primeros 'max_items' elementos si es una lista
    for key, value in most_complete_module.items():
        if isinstance(value, list):
            most_complete_module[key] = value[:max_items]
    return most_complete_module

def process_json_data(data_list):
    module_dict = defaultdict(list)
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
                            module_dict[module_name].append(module)
                            print(f"Processed module: {module_name}")

    most_complete_modules = {}
    for module_name, modules in module_dict.items():
        most_complete_module_data = get_most_complete_module([module['Data'] for module in modules])
        for module in modules:
            if module['Data'] == most_complete_module_data:
                most_complete_modules[module_name] = module
                print(f"Selected most complete module: {module_name}")
                break
        if module_name not in most_complete_modules:
            most_complete_modules[module_name] = modules[0]  # Add at least one module if none is selected
            print(f"Added at least one module: {module_name}")
    
    return most_complete_modules

def main():
    persona_dir = 'Persona'
    empresa_dir = 'Empresa'
    
    persona_data_list = load_json_files(persona_dir)
    empresa_data_list = load_json_files(empresa_dir)

    persona_modules = process_json_data(persona_data_list)
    empresa_modules = process_json_data(empresa_data_list)

    # Combinar módulos de persona y empresa
    combined_modules = {**persona_modules, **empresa_modules}

    with open('Modulos_completos.json', 'w', encoding='utf-8') as f:
        json.dump(combined_modules, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()
