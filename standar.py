import os
import json
import pandas as pd
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
                clean_dict[k] = "No se encontraron datos para esta variable, debe analizarse a futuro"
            else:
                clean_dict[k] = clean_data(v)
        return clean_dict
    elif isinstance(data, list):
        return [clean_data(item) for item in data[:2]]  # Limit lists to 2 items
    else:
        return data

def merge_modules(module_list):
    merged = defaultdict(dict)
    for module in module_list:
        module_data = module['Data']
        for key, value in module_data.items():
            if isinstance(value, list):
                if key not in merged or not isinstance(merged[key], list):
                    merged[key] = []
                merged[key].extend(value[:2])
                merged[key] = merged[key][:2]
            else:
                merged[key] = value
    return dict(merged)

def process_json_data(data_list, suffix):
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
                            module_name = f"{module['Nombre']}_{suffix}"
                            module_dict[module_name].append(module)
                            print(f"Processed module: {module_name}")

    most_complete_modules = {}
    for module_name, modules in module_dict.items():
        most_complete_modules[module_name] = {
            'Nombre': module_name,
            'Data': merge_modules(modules)
        }
        print(f"Added module: {module_name}")

    return most_complete_modules

def extract_data_to_dataframe(modules):
    data = []
    for module_name, module in modules.items():
        flat_module = flatten_json(module['Data'])
        for key, value in flat_module.items():
            data.append({
                'Module': module_name,
                'Key': key,
                'Example Value': value,
            })
    df = pd.DataFrame(data)
    return df

def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '.')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '.')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out

def main():
    persona_dir = 'Persona'
    empresa_dir = 'Empresa'
    
    persona_data_list = load_json_files(persona_dir)
    empresa_data_list = load_json_files(empresa_dir)

    persona_modules = process_json_data(persona_data_list, "p")
    empresa_modules = process_json_data(empresa_data_list, "e")

    # Crear DataFrames y archivos Excel
    persona_df = extract_data_to_dataframe(persona_modules)
    empresa_df = extract_data_to_dataframe(empresa_modules)

    persona_df.to_excel('Persona_data.xlsx', index=False)
    empresa_df.to_excel('Empresa_data.xlsx', index=False)

    # Combinar módulos de persona y empresa
    combined_modules = {**persona_modules, **empresa_modules}

    # Guardar todos los módulos en un único archivo JSON
    with open('modulos_completos.json', 'w', encoding='utf-8') as f:
        json.dump(combined_modules, f, ensure_ascii=False, indent=4)
        print(f'Saved combined modules to modulos_completos.json')

    print('DataFrames and Excel files created successfully.')

if __name__ == '__main__':
    main()
